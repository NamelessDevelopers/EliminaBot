from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from elimina.entities.base import Base


class Guild(Base):
    """
    Database Entity for a Discord Guild.

    Attributes
    -----------
        id : int
            The id of the Guild.
        name : str
            The id of the Guild.
        delete_delay : int
            The amount of seconds to wait before deleting a message sent by a bot in a `toggled_channel`.
        toggled_channels : List[int]
            A list of channel ids in which the bot should function.
        ignored_bots : List[int]
            A list of user ids for bots that the bot should ignore.
        image_snipe: bool
            Whether the image snipe feature is enabled or not.
    """

    __tablename__ = "guild"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    delete_delay: Mapped[int] = mapped_column(default=5)
    toggled_channels: Mapped[List[int]] = mapped_column(default=[])
    ignored_bots: Mapped[List[int]] = mapped_column(default=[])
    image_snipe: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Guild(id={self.id!r}, name={self.id!r}, delete_delay={self.delete_delay!r})"