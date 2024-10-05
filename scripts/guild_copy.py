import json
from typing import List

from sqlalchemy import JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


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
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    delete_delay: Mapped[int] = mapped_column(default=5)
    toggled_channels: Mapped[List[int]] = mapped_column(JSON, default=json.dumps([]))
    ignored_bots: Mapped[List[int]] = mapped_column(JSON, default=json.dumps([]))
    image_snipe: Mapped[bool] = mapped_column(default=False)
    snipe_enabled: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Guild(id={self.id!r}, name={self.name!r}, delete_delay={self.delete_delay!r})"
