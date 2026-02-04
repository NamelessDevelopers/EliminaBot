import json
from typing import Dict, List, Optional, Set

from sqlalchemy import select

from elimina import LOGGER
from elimina.db import async_session
from elimina.entities.guild import Guild
from elimina.exceptions.db_exceptions import *

# Simple in-memory cache with manual invalidation
_whitelist_cache: Optional[Dict[int, Dict[str, Set[int]]]] = None


def _invalidate_cache() -> None:
    global _whitelist_cache
    _whitelist_cache = None


async def get_whitelists() -> Optional[Dict[int, Dict[str, Set[int]]]]:
    global _whitelist_cache
    if _whitelist_cache is not None:
        return _whitelist_cache

    try:
        async with async_session() as session:
            result = await session.execute(
                select(Guild.id, Guild.toggled_channels, Guild.ignored_bots)
            )
            rows = result.all()
            m: Dict[int, Dict[str, Set[int]]] = {}
            if not rows:
                raise EntityNotFoundError()
            for _id, channels, bots in rows:
                channels = json.loads(channels)
                bots = json.loads(bots)
                if _id not in m:
                    m[_id] = {}
                m[_id]["channels"] = set(channels)
                m[_id]["bots"] = set(bots)
            _whitelist_cache = m
            return m

    except Exception as e:
        LOGGER.exception(f"Failed to get whitelists due to: {e}")
        return None


async def transform_lists(guilds: List[Guild]) -> List[Guild]:
    for i, guild in enumerate(guilds):
        channels = json.loads(guild.toggled_channels)
        bots = json.loads(guild.ignored_bots)
        guilds[i].toggled_channels = channels
        guilds[i].ignored_bots = bots
    return guilds


async def get_guild(id: Optional[int]) -> Optional[List[Guild]]:
    """
    Function to get Guilds in the database.

    Parameters
    ----------
        id : Optional[int]
            Returns the Guild that matches the `id` or all Guilds if no `id` is provided.
    Returns
    -------
        guilds : Optional[List[Guild]]
            An optional list of `Guild` objects.
    """
    try:
        async with async_session() as session:
            if id:
                result = await session.execute(
                    select(Guild).where(Guild.id == id)
                )
            else:
                result = await session.execute(select(Guild))
            guilds = list(result.scalars().all())
            return await transform_lists(guilds)
    except Exception as e:
        LOGGER.exception(f"Error getting guild: {e}")
        return None


async def create_guild(guild_id: int, guild_name: str, **kwargs) -> None:
    """
    Function to create a new Guild in the database.

    Parameters
    ----------
        guild_id : int
            The `id` of the Guild.
        guild_name : str
            The `name` of the Guild.
    Returns
    -------
        guild : Optional[Guild]
            An optional `Guild` object if the creation is successful. `None` otherwise.
    """
    try:
        async with async_session() as session:
            existing = await session.get(Guild, guild_id)
            if existing:
                raise PrimaryKeyViolationError()
            guild = Guild(id=guild_id, name=guild_name, **kwargs)
            session.add(guild)
            await session.flush()
            await session.commit()
            _invalidate_cache()
    except Exception as e:
        LOGGER.exception(f"Error creating guild: {e}")


async def update_guild(
    guild_id: int,
    guild_name: Optional[str] = None,
    delete_delay: Optional[int] = None,
    enabled_channel: Optional[int] = None,
    disabled_channel: Optional[int] = None,
    ignored_bot: Optional[int] = None,
    unignored_bot: Optional[int] = None,
    image_snipe: Optional[bool] = None,
    snipe_enabled: Optional[bool] = None,
) -> Optional[Guild]:
    """
    Function to update a Guild in the database.

    Parameters
    ----------
        guild_id : int
            The `id` of the Guild.
        guild_name : Optional[str]
            An optional `name` to be updated.
        delete_delay : Optional[int]
            An optional `delete_delay` to be updated.
        enabled_channel : Optional[int]
            An optional channel id to be appended to `toggled_channels`.
        disabled_channel : Optional[int]
            An optional channel id to be removed from `toggled_channels`.
        ignored_bot : Optional[int]
            An optional bot id to be appended to `ignored_bots`.
        unignored_bot : Optional[int]
            An optional bot id to be removed from `ignored_bots`.
        image_snipe : Optional[bool]
            An optional bool value to update `image_snipe`.
        snipe_enabled : Optional[bool]
            An optional bool value to update `snipe_enabled`.
    Returns
    -------
        guild : Optional[Guild]
            An optional `Guild` object if the updation is successful. `None` otherwise.
    """
    try:
        async with async_session() as session:
            guild: Guild | None = await session.get(Guild, guild_id)
            if not guild:
                raise EntityNotFoundError()
            if guild_name:
                guild.name = guild_name
            if delete_delay:
                guild.delete_delay = delete_delay
            if enabled_channel:
                channels = json.loads(guild.toggled_channels)
                if enabled_channel not in channels:
                    channels.append(enabled_channel)
                guild.toggled_channels = json.dumps(channels)
            if disabled_channel:
                channels = json.loads(guild.toggled_channels)
                if disabled_channel in channels:
                    channels.remove(disabled_channel)
                guild.toggled_channels = json.dumps(channels)
            if ignored_bot:
                bots = json.loads(guild.ignored_bots)
                if ignored_bot not in bots:
                    bots.append(ignored_bot)
                guild.ignored_bots = json.dumps(bots)
            if unignored_bot:
                bots = json.loads(guild.ignored_bots)
                if unignored_bot in bots:
                    bots.remove(unignored_bot)
                guild.ignored_bots = json.dumps(bots)
            if image_snipe is not None:
                guild.image_snipe = image_snipe
            if snipe_enabled is not None:
                guild.snipe_enabled = snipe_enabled
            await session.commit()
            _invalidate_cache()
            return guild
    except Exception as e:
        LOGGER.exception(f"Error updating guild: {e}")
        return None


async def delete_guild(guild_id: int) -> None:
    """
    Function to delete a Guild from the database.

    Parameters
    ----------
        guild_id : int
            The `id` of the Guild to be deleted.
    """
    try:
        async with async_session() as session:
            guild: Guild | None = await session.get(Guild, guild_id)
            if not guild:
                raise EntityNotFoundError()
            await session.delete(guild)
            await session.flush()
            await session.commit()
            _invalidate_cache()
    except Exception as e:
        LOGGER.exception(f"Error deleting guild: {e}")
