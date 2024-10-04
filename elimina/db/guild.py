from typing import List, Optional

from sqlalchemy.orm import Session

from elimina import LOGGER
from elimina.db import engine
from elimina.entities.guild import Guild
from elimina.exceptions.db_exceptions import *


def get_guild(id: Optional[int]) -> Optional[List[Guild]]:
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
        with Session(engine) as session:
            return (
                session.query(Guild).filter(Guild.id == id).all()
                if id
                else session.query().all()
            )
    except Exception as e:
        LOGGER.exception("Error getting guild: ", e)
        return None


def create_guild(
    guild_id: int,
    guild_name: str,
) -> Optional[Guild]:
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
        with Session(engine) as session:
            guild = get_guild(guild_id)
            if guild:
                raise PrimaryKeyViolationError()
            guild = Guild(
                guild_id,
                guild_name,
            )
            session.add(Guild)
            session.flush()
            session.commit()
            return guild
    except Exception as e:
        LOGGER.exception("Error creating guild: ", e)
        return None


def update_guild(
    guild_id: int,
    guild_name: Optional[str],
    delete_delay: Optional[int],
    toggled_channel: Optional[int],
    ignored_bot: Optional[int],
    image_snipe: Optional[bool],
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
        toggled_channel : Optional[int]
            An optional channel id to be appended to `toggled_channels`.
        ignored_bot : Optional[int]
            An optional bot id to be appended to `ignored_bots`.
        image_snipe : Optional[bool]
            An optional boolean value to update `image_snipe`.
    Returns
    -------
        guild : Optional[Guild]
            An optional `Guild` object if the updation is successful. `None` otherwise.
    """
    try:
        with Session(engine) as session:
            guild: Guild | None = session.query(Guild).get(guild_id)
            if not guild:
                raise EntityNotFoundError()
            if guild_name:
                guild.name = guild_name
            if delete_delay:
                guild.delete_delay = delete_delay
            if toggled_channel:
                guild.toggled_channels.append(toggled_channel)
            if ignored_bot:
                guild.ignored_bots.append(ignored_bot)
            if image_snipe is not None:
                guild.image_snipe = image_snipe
            session.commit()
            return guild
    except Exception as e:
        LOGGER.exception("Error updating guild: ", e)
        return None


def delete_guild(guild_id: int) -> None:
    """
    Function to delete a Guild from the database.

    Parameters
    ----------
        guild_id : int
            The `id` of the Guild to be deleted.
    """
    try:
        with Session(engine) as session:
            guild: Guild | None = session.query(Guild).get(guild_id)
            if not guild:
                raise EntityNotFoundError()
            session.delete(Guild)
            session.flush()
            session.commit()
    except Exception as e:
        LOGGER.exception("Error deleting guild: ", e)
