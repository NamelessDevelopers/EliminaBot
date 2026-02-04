# Elimina Bot — Refactor & Fix Plan

> **Repo:** https://github.com/namelessdevelopers/eliminabot
> **Last touched:** Oct 2024 (1y4m dormant)
> **Stack:** Python, discord.py 2.x, SQLAlchemy 2.x, SQLite, Pydantic
> **Scale:** ~400-500 servers, hardcoded 32 shards
> **Created:** 2026-02-04

---

## Phase 1: Critical Bugs (Shit That's Actually Broken)

These are things that are silently failing or crashing right now.

### 1.1 — `update_guild` never saves channel/bot list changes
**File:** `elimina/db/guild.py` → `update_guild()`
**Impact:** `~toggle` and `~ignore` commands **do nothing**. Completely broken.

```python
# CURRENT (broken) — .append() returns None, json.dumps(None) = "null", AND result isn't assigned back
if enabled_channel:
    json.dumps(json.loads(guild.toggled_channels).append(enabled_channel))
```

**Fix:** Parse the list, mutate, serialize, assign back to the entity:
```python
if enabled_channel:
    channels = json.loads(guild.toggled_channels)
    channels.append(enabled_channel)
    guild.toggled_channels = json.dumps(channels)
```
Same pattern for `disabled_channel`, `ignored_bot`, `unignored_bot`.

### 1.2 — `transform_lists` copy-paste bug
**File:** `elimina/db/guild.py` → `transform_lists()`

```python
# CURRENT (broken) — loads toggled_channels into bots
bots = json.loads(guild.toggled_channels)  # should be guild.ignored_bots
```

### 1.3 — Snipe/EditSnipe classes never initialize attributes
**File:** `elimina/helpers/snipe.py`

```python
# CURRENT — declares type hint but never sets value
def __init__(self) -> None:
    self.message: Optional[Message]  # this is NOT assignment, just annotation
```

**Fix:** `self.message: Optional[Message] = None`

Same for `EditSnipe.edited_message`.

### 1.4 — `on_message_delete` / `on_message_edit` store wrong types
**File:** `elimina/handlers/event_handler.py`

```python
# CURRENT — stores raw discord.Message, but snipe command accesses .message attribute
self.snipe_message[guild_id] = message  # should wrap in Snipe()

# on_message_edit stores only `after`, but editsnipe needs both before and after
self.edit_snipe_message[guild_id] = after
```

**Fix:**
```python
# on_message_delete
snipe = Snipe()
snipe.message = message
self.snipe_message[guild_id] = snipe

# on_message_edit
edit_snipe = EditSnipe()
edit_snipe.message = before
edit_snipe.edited_message = after
self.edit_snipe_message[guild_id] = edit_snipe
```

### 1.5 — `snipe`/`editsnipe` send embed as positional arg
**File:** `elimina/handlers/event_handler.py`

```python
await ctx.send(snipe_embed)       # WRONG — sends as content string
await ctx.send(embed=snipe_embed) # CORRECT
```

### 1.6 — `Embed.add_field()` missing keyword arguments
**File:** `elimina/handlers/event_handler.py` (snipe + editsnipe commands)

discord.py 2.x requires `name=` and `value=` as keyword args:
```python
# CURRENT (broken)
snipe_embed.add_field(attachment.filename, attachment.proxy_url, inline=True)
# FIX
snipe_embed.add_field(name=attachment.filename, value=attachment.proxy_url, inline=True)
```

### 1.7 — `message.delete(60)` → `message.delete(delay=60)`
**File:** `elimina/handlers/event_handler.py` → `on_message()`

discord.py 2.x changed positional `delay` to keyword-only:
```python
return await message.delete(60)        # BROKEN
return await message.delete(delay=60)  # CORRECT
```

### 1.8 — `on_guild_update` AttributeError
**File:** `elimina/handlers/event_handler.py`

```python
guild_id = before.guild.id  # WRONG — Guild object doesn't have .guild
guild_id = before.id        # CORRECT
```

### 1.9 — No DM guard → crash on any DM
**File:** `elimina/handlers/event_handler.py` → `on_message()`

`message.guild` is `None` in DMs → `message.guild.id` crashes. Same for `on_message_delete`, `on_message_edit`.

**Fix:** Add early return at the top of each listener:
```python
if not message.guild:
    return
```

Also add `@commands.guild_only()` decorator to all commands.

### 1.10 — `on_guild_remove` hardcoded channel IDs
**File:** `elimina/handlers/event_handler.py`

```python
# CURRENT — hardcoded, inconsistent with on_guild_join which uses config
await self.bot.get_guild(777063033301106728).get_channel(779045674557767680).send(...)
# FIX — use config values
await self.bot.get_guild(config.SUPPORT_SERVER_ID).get_channel(config.JOIN_LEAVE_CHANNEL).send(...)
```

### 1.11 — `on_guild_remove` KeyError on snipe dict deletion
**File:** `elimina/handlers/event_handler.py`

```python
# CURRENT — will KeyError if guild was never in the dict
del self.snipe_message[guild_id]
# FIX
self.snipe_message.pop(guild_id, None)
self.edit_snipe_message.pop(guild_id, None)
```

### 1.12 — Error handler `get_cooldown_retry_after` doesn't exist
**File:** `elimina/handlers/error_handler.py`

```python
# CURRENT
command.get_cooldown_retry_after(ctx)
# FIX — use the error object directly
error.retry_after
```

---

## Phase 2: Database Layer (AsyncSession + Cache Fix)

### 2.1 — Migrate to AsyncSession + async engine
**Files:** `elimina/db/__init__.py`, `elimina/db/guild.py`

Currently using sync `Session` inside `async def` functions — this **blocks the event loop** on every DB call.

**Changes:**
- Replace `create_engine` → `create_async_engine` (requires `aiosqlite` dep)
- Replace `Session(engine)` → `async with AsyncSession(engine) as session:`
- Replace `session.query(...)` → `await session.execute(select(...))`
- Update `DB_URI` format: `sqlite+aiosqlite:///db.sqlite3`
- Add `aiosqlite` to dependencies

### 2.2 — Fix caching (currently never invalidates)
**File:** `elimina/db/guild.py`

`@cachetools.cached(cache)` on `get_whitelists()` means the cache **never clears**. Any `toggle`/`ignore` change is invisible until restart.

**Options (pick one):**
- **A) TTLCache** — `cachetools.TTLCache(maxsize=1, ttl=60)` — simple, slight delay
- **B) Manual invalidation** — call `cache.clear()` after every `update_guild` / `create_guild` / `delete_guild`
- **C) In-memory dict managed by the bot** — drop cachetools, maintain a dict updated on writes

**Recommendation:** Option B (manual invalidation). Simple, immediate, no weird stale data.

### 2.3 — Clean up JSON serialization mess
**File:** `elimina/entities/guild.py`, `elimina/db/guild.py`

The entity declares `Mapped[List[int]]` with `JSON` column type, but the code does manual `json.loads`/`json.dumps` everywhere. SQLAlchemy's JSON type handles serialization automatically.

**Fix:**
- Remove all manual `json.loads()`/`json.dumps()` in DB functions
- Let SQLAlchemy handle it natively through the JSON column type
- Remove `transform_lists()` entirely — it becomes unnecessary

### 2.4 — Remove duplicate Table definition
**File:** `elimina/entities/guild.py`

`guild_table = Table(...)` and `class Guild(Base)` both define the same table. The standalone `Table` object is never used. Delete it.

---

## Phase 3: discord.py Modernization

### 3.1 — Remove hardcoded shards / use AutoShardedBot properly
**File:** `elimina/__init__.py`

```python
# CURRENT — hardcoded 32 shards for a 400-500 server bot (overkill, wastes resources)
shards=32,
# FIX — remove the kwarg entirely, let AutoShardedBot decide (or use regular Bot)
```

Discord recommends sharding at 2,500+ guilds. For 400-500 servers, `commands.Bot` (no sharding) is fine. If you want to keep `AutoShardedBot` for future growth, just remove the `shards=32` and let Discord's gateway tell you how many you need.

### 3.2 — Fix `purge` command permission check
**File:** `elimina/commands/mod.py`

```python
# CURRENT — manual role name check
for role in ctx.author.roles:
    if role.name.lower() == "moderation":
        has_moderation = True
```

**Fix:** Use discord.py's built-in decorator:
```python
@commands.has_permissions(manage_messages=True)
```
Drop the manual role iteration and SUPER_USERS check (handle super users via `bot.is_owner()` or a custom check).

### 3.3 — Deprecation: `discriminator` usage
**File:** `elimina/handlers/event_handler.py`

```python
f"sniped by {ctx.author.name}#{ctx.author.discriminator}"
```
Discord migrated to unique usernames. `discriminator` is "0" for most users now. Use `ctx.author.display_name` or just `ctx.author.name`.

### 3.4 — Add `@commands.guild_only()` to all commands
Prevents DM invocations from crashing. Apply to every command in every cog.

### 3.5 — Intents audit
**File:** `elimina/__init__.py`

```python
intents=discord.Intents(53608189)  # magic number
```

Replace with explicit intent construction for clarity:
```python
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # if needed
```

---

## Phase 4: Refactoring + Polish

### 4.1 — Snipe/EditSnipe refactor
**Current issues:**
- Stored per-guild, not per-channel (can only snipe the last deleted msg in the entire server)
- No TTL (deleted message from 3 hours ago is still snipeable)
- Snipe data lives on the EventHandler cog (coupling)

**Proposed refactor:**
- Store per-channel: `Dict[int, Dict[int, Snipe]]` → `{guild_id: {channel_id: Snipe}}`
- Add TTL: auto-expire after 60 seconds (match README claim)
- Move snipe storage to a dedicated service/manager class
- `snipe`/`editsnipe` commands can stay on EventHandler or move to their own cog

### 4.2 — dctimer
**Current state:** Creates a temp voice channel, moves user to it, deletes the channel. Hacky but functional.

**Known issues:**
- `asyncio.sleep(time)` doesn't survive bot restarts
- Double `tempChannel.delete()` (second one always fails)
- No way to cancel the timer

**Decision:** Keep as-is per your call. Minor cleanup:
- Remove the second `delete()` call and the 30s sleep
- Add a try/except around the whole disconnect flow
- Maybe add a `~canceldctimer` command later

### 4.3 — Logging cleanup
- Replace f-string logging with lazy `%s` formatting (performance)
- Add structured context (guild_id, channel_id) to log messages
- Consider using discord.py's built-in logging config

### 4.4 — Config modernization
- Move `SUPER_USERS` from `constants.py` to config/env
- Add `OWNER_IDS` to Config for `commands.is_owner()` support
- Consider adding `LOG_LEVEL` to config

### 4.5 — README update
- Update command docs to reflect current state
- Fix "default is 5 seconds" vs "default: 15 seconds" inconsistency (help says 15, entity default is 5)
- Add setup/deployment instructions

---

## Execution Order

| Phase | Status | Commits |
|-------|--------|---------|
| Phase 1 (Critical Bugs) | ✅ DONE | `f72b1e7`..`e721af4` |
| Phase 2 (Database Layer) | ✅ DONE | `934a8b0`..`eb6b623` |
| Phase 3 (discord.py Modern) | ✅ DONE | `7d400df`..`bb3e6f2` |
| Phase 4 (Refactor + Polish) | ✅ DONE | `cf0274f`..`8e5c79d` |

**All phases completed 2026-02-04. 17 commits, not yet pushed.**

---

## Dependencies to Add
```toml
# pyproject.toml additions
"aiosqlite>=0.20.0",  # for async SQLite support
```

## Files Touched Per Phase

**Phase 1:** `db/guild.py`, `helpers/snipe.py`, `handlers/event_handler.py`, `handlers/error_handler.py`, `commands/mod.py`
**Phase 2:** `db/__init__.py`, `db/guild.py`, `entities/guild.py`, `__init__.py`, `pyproject.toml`
**Phase 3:** `__init__.py`, `commands/mod.py`, `handlers/event_handler.py`, `handlers/error_handler.py`, all command cogs (guild_only)
**Phase 4:** `helpers/snipe.py`, `handlers/event_handler.py`, `commands/utility.py`, `config.py`, `constants.py`, `README.md`

---

*Let's get this thing working again.* 🔧
