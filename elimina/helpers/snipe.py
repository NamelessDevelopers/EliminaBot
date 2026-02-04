from typing import Optional

from discord import Message


class Snipe:
    """
    Class representing a temporarily stored message.

    Attributes
    ----------
        message : Optional[discord.Message]
            An optional discord.Message object stored temporarily in memory.
    """

    def __init__(self) -> None:
        self.message: Optional[Message] = None
    
    def __repr__(self) -> str:
        if not self.message:
            return "Empty"
        return (
            f"Message(id={self.message.id}, "
            f"content={self.message.content[:8]}..., "
            f"author={self.message.author.display_name}, "
            f"guild={self.message.guild.name}, "
            f"channel={self.message.channel}, "
            f"attachment={'Yes' if self.message.attachments else 'No'})"
        )

class EditSnipe(Snipe):
    """
    Edit Snipe class.
    Derives `Snipe`

    Attributes
    ----------
        edited_message: Optional[Message]
            An optional discord.Message object. This is the message object after the edit.
    """
    def __init__(self) -> None:
        super().__init__()
        self.edited_message: Optional[Message] = None
    
    def __repr__(self) -> str:
        msg = super().__repr__()
        if not self.edited_message:
            return msg
        return msg[:-1] + f", edited_content={self.edited_message.content[:8]}...)"
