# Favorite data validation
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# Information required to add a favourite
class FavoriteCreate(BaseModel):
    # Only 1 to 25 characters, letters, numbers and _ are permitted
    twitch_login: str = Field(min_length = 1, max_length = 25, pattern = r"^[A-Za-z0-9_]+$")

    # To ignore the distinction between upper and lower case for the same name
    @field_validator("twitch_login")
    @classmethod
    def to_lowercase(cls, value: str) -> str:
        return value.lower()

# Data returned by the API regarding a favourite
class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    twitch_login: str
    created_at: datetime

# Information about a streamer obtained from Twitch
class FavoriteStreamerInfo(BaseModel):
    twitch_id: str
    login: str
    display_name: str
    is_live: bool
    stream_title: str | None = None
    game_name: str | None = None
    viewer_count: int | None = None
    