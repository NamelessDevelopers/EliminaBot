import time
from collections import defaultdict
from typing import Dict, Optional, Tuple

from discord import Message


class Snipe:
    """
    Stores a deleted message with a timestamp for TTL expiry.
    """

    __slots__ = ("message", "timestamp")

    def __init__(self, message: Optional[Message] = None) -> None:
        self.message: Optional[Message] = message
        self.timestamp: float = time.monotonic() if message else 0.0

    def __repr__(self) -> str:
        if not self.message:
            return "Snipe(empty)"
        return (
            f"Snipe(id={self.message.id}, "
            f"author={self.message.author.display_name}, "
            f"channel={self.message.channel.id})"
        )


class EditSnipe:
    """
    Stores a before/after edit pair with a timestamp for TTL expiry.
    """

    __slots__ = ("before", "after", "timestamp")

    def __init__(
        self,
        before: Optional[Message] = None,
        after: Optional[Message] = None,
    ) -> None:
        self.before: Optional[Message] = before
        self.after: Optional[Message] = after
        self.timestamp: float = time.monotonic() if before else 0.0

    def __repr__(self) -> str:
        if not self.before:
            return "EditSnipe(empty)"
        return (
            f"EditSnipe(id={self.before.id}, "
            f"author={self.before.author.display_name}, "
            f"channel={self.before.channel.id})"
        )


class SnipeManager:
    """
    Manages snipe and editsnipe storage per-guild, per-channel with TTL.

    Storage: {guild_id: {channel_id: Snipe/EditSnipe}}
    """

    DEFAULT_TTL = 60  # seconds

    def __init__(self, ttl: int = DEFAULT_TTL) -> None:
        self.ttl = ttl
        self._snipes: Dict[int, Dict[int, Snipe]] = defaultdict(dict)
        self._edit_snipes: Dict[int, Dict[int, EditSnipe]] = defaultdict(dict)

    def _is_expired(self, timestamp: float) -> bool:
        return (time.monotonic() - timestamp) > self.ttl

    # -- snipe --

    def store_snipe(self, guild_id: int, channel_id: int, message: Message) -> None:
        self._snipes[guild_id][channel_id] = Snipe(message)

    def get_snipe(self, guild_id: int, channel_id: int) -> Optional[Message]:
        snipe = self._snipes.get(guild_id, {}).get(channel_id)
        if not snipe or not snipe.message:
            return None
        if self._is_expired(snipe.timestamp):
            self._snipes[guild_id].pop(channel_id, None)
            return None
        return snipe.message

    def clear_snipe(self, guild_id: int, channel_id: int) -> None:
        if guild_id in self._snipes:
            self._snipes[guild_id].pop(channel_id, None)

    # -- editsnipe --

    def store_edit_snipe(
        self, guild_id: int, channel_id: int, before: Message, after: Message
    ) -> None:
        self._edit_snipes[guild_id][channel_id] = EditSnipe(before, after)

    def get_edit_snipe(
        self, guild_id: int, channel_id: int
    ) -> Optional[Tuple[Message, Message]]:
        edit = self._edit_snipes.get(guild_id, {}).get(channel_id)
        if not edit or not edit.before or not edit.after:
            return None
        if self._is_expired(edit.timestamp):
            self._edit_snipes[guild_id].pop(channel_id, None)
            return None
        return (edit.before, edit.after)

    def clear_edit_snipe(self, guild_id: int, channel_id: int) -> None:
        if guild_id in self._edit_snipes:
            self._edit_snipes[guild_id].pop(channel_id, None)

    # -- guild cleanup --

    def clear_guild(self, guild_id: int) -> None:
        self._snipes.pop(guild_id, None)
        self._edit_snipes.pop(guild_id, None)
