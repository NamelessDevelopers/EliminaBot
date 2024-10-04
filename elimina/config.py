from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    DB_URI: str
    SUPER_USERS: List[int]
    SUPPORT_EMAIL: str
    SUPPORT_SERVER_INVITE: str
    SUPPORT_SERVER_ID: int
    JOIN_LEAVE_CHANNEL: int
    BOT_PREFIX: str
    GITHUB_URL: str
    TOP_GG_ID: int
    POLL_EMOTE_YES: str
    POLL_EMOTE_NO: str
    POLL_EMOTE_MAYBE: str
