from typing import Dict, Optional
from pydantic import BaseModel


class GuildItem(BaseModel):
    id: str
    name: str
    icon: Optional[str]
    permissions: int


class GuildConfigIn(BaseModel):
    prefix: str
    automod_enabled: bool
    logging_channel_id: Optional[str] = None
    raid_mode: bool
    settings: Dict = {}


class GuildConfigOut(GuildConfigIn):
    guild_id: str
