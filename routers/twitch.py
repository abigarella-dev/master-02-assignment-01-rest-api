# Indicate the streamer's status 
from fastapi import APIRouter, HTTPException, Path

from configuration.database import get_connection
from models.favorites import FavoriteStreamerInfo
from services.twitch_client import TwitchError, get_streamers_info

router = APIRouter(
    prefix = "/twitch",
    tags = ["Twitch"]
)

# Information about any streamer
@router.get("/streamers/{login}", response_model = FavoriteStreamerInfo)
def get_streamer(
    # Only 1 to 25 characters, letters, numbers and _ are permitted
    login: str = Path(min_length = 1, max_length = 25, pattern = r"^[A-Za-z0-9_]+$")
):
    # The system requests the information from Twitch, and if a 502 error is returned it is because the streamer does not exist
    try:
        info = get_streamers_info([login.lower()])
    except TwitchError as error:
        raise HTTPException(status_code = 502, detail = str(error))

    if not info:
        raise HTTPException(status_code = 404, detail = "Streamer not found on Twitch")

    # Otherwise, the single element is returned
    return info[0]

# Live status of all the favourites of a user
@router.get("/users/{user_id}/favorites", response_model=list[FavoriteStreamerInfo])
def get_favorites_status(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # The user is checked and their MySQL favourites are retrieved
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code = 404, detail = "User not found")

        cursor.execute(
            "SELECT twitch_login FROM favorite_streamers WHERE user_id = %s",
            (user_id,)
        )
        logins = [row["twitch_login"] for row in cursor.fetchall()]

    # The list is used to request information from Twitch about your favourite streamers
    finally:
        cursor.close()
        conn.close()

    # The list is used to request information from Twitch
    try:
        return get_streamers_info(logins)
    except TwitchError as error:
        raise HTTPException(status_code = 502, detail=str(error))
    