# Elimina Discord Bot

A Discord bot that automatically deletes messages from bots after a configurable delay in selected channels. Also features message sniping, purge, polls, and a voice disconnect timer.

## Features

- **Auto-delete bot messages** in toggled channels after X seconds (1–300s, default 5s)
- **Snipe** — view the most recently deleted message (per-channel, 60s TTL)
- **EditSnipe** — view the most recently edited message (per-channel, 60s TTL)
- **Purge** — bulk delete bot messages
- **Ignore list** — whitelist specific bots from auto-deletion
- **DC Timer** — auto-disconnect from voice after a set time
- **Polls** — quick reaction polls via `poll: <question>`

Elimina's own messages are auto-deleted after 1 minute in toggled channels.

## Commands

| Command | Permission | Description |
|---|---|---|
| `~help` | Everyone | Show all commands |
| `~info` | Everyone | Show server setup (toggled channels, ignored bots, timer) |
| `~invite` | Everyone | Get bot invite link |
| `~vote` | Everyone | Vote on Top.gg |
| `~toggle` | Admin | Activate/deactivate auto-delete in current channel |
| `~timer <seconds>` | Admin | Set delete delay (1–300s) |
| `~ignore <@bot>` | Admin | Add/remove bot from whitelist |
| `~imgsnipe` | Admin | Toggle image sniping |
| `~togglesnipe` | Admin | Enable/disable snipe feature |
| `~snipe` | Admin/Sniper | View last deleted message in this channel |
| `~editsnipe` | Admin/Sniper | View last edited message in this channel |
| `~purge [count]` | Manage Messages | Delete bot messages (default: 300) |
| `~dctimer <time>` | Everyone | Auto-disconnect from voice (e.g. `30s`, `5m`, `1h`) |

## Setup

### Requirements

- Python 3.10+
- A Discord bot token with **Message Content Intent** enabled

### Installation

```bash
# clone
git clone https://github.com/namelessdevelopers/eliminabot.git
cd eliminabot

# create venv
python3 -m venv .venv
source .venv/bin/activate

# install
pip install -e .
```

### Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
BOT_TOKEN=your_bot_token
DB_URI=sqlite+aiosqlite:///elimina.sqlite3
SUPPORT_EMAIL=your@email.com
SUPPORT_SERVER_INVITE=https://discord.gg/your_invite
SUPPORT_SERVER_ID=your_server_id
JOIN_LEAVE_CHANNEL=your_channel_id
BOT_PREFIX="~"
GITHUB_URL=https://github.com/namelessdevelopers/eliminabot
TOP_GG_ID=your_bot_id
POLL_EMOTE_YES=emote_name:emote_id
POLL_EMOTE_NO=emote_name:emote_id
POLL_EMOTE_MAYBE=emote_name:emote_id
```

### Running

```bash
source .venv/bin/activate
python -m elimina
```

### Database Migrations

```bash
alembic upgrade head
```

## Tech Stack

- **discord.py** 2.x (hybrid commands + slash commands)
- **SQLAlchemy** 2.x (async via aiosqlite)
- **Pydantic** for config validation
- **Alembic** for database migrations
- **SQLite** (async via aiosqlite)

## Authors

- [ayamdobhal](https://github.com/AyamDobhal)
- [hyppytyynytyydytys](https://github.com/hyppytyynytyydytys)
- [moizmoizmoizmoiz](https://github.com/moizmoizmoizmoiz)

## Links

- [Invite Elimina](https://discord.com/api/oauth2/authorize?client_id=777575449957498890&permissions=17918992&scope=bot)
- [Support Server](https://discord.gg/vFmFTjPpZ4)
