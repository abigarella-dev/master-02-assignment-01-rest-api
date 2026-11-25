# Manage a user's favorite streamers
from fastapi import APIRouter, HTTPException
import mysql.connector

from configuration.database import get_connection
from models.favorites import FavoriteCreate, FavoriteResponse
from services.twitch_client import TwitchError, streamer_exists

router = APIRouter(
    prefix = "/users/{user_id}/favorites",
    tags = ["Favorites"]
)

# Check that the user exists
def ensure_user_exists(cursor, user_id: int):
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code = 404, detail = "User not found")

# Add a favourite streamer to a user
@router.post("", response_model = FavoriteResponse, status_code = 201)
def add_favorite(user_id: int, favorite: FavoriteCreate):
    # 'favourite' is converted to lower case for security reasons
    login = favorite.twitch_login.lower()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        ensure_user_exists(cursor, user_id)

        # If Twitch reports a message stating that the streamer does not exist, a 404 message is sent
        try:
            exists = streamer_exists(login)
        except TwitchError as error:
            raise HTTPException(status_code = 502, detail = str(error))
        
        if not exists:
            raise HTTPException(status_code = 404, detail = "Streamer not found on Twitch")

        # The favourite is saved alongside the user id
        cursor.execute(
            "INSERT INTO favorite_streamers (user_id, twitch_login) VALUES (%s, %s)",
            (user_id, login)
        )
        conn.commit()

        cursor.execute(
            "SELECT * FROM favorite_streamers WHERE id = %s",
            (cursor.lastrowid,)
        )
        return cursor.fetchone()

    # If a streamer is already saved as a favourite, a 409 error message appears
    except mysql.connector.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code = 409,
            detail = "This streamer is already in the user's favourites"
        )

    finally:
        cursor.close()
        conn.close()

# Lists the user’s favourites by date
@router.get("", response_model = list[FavoriteResponse])
def list_favorites(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        ensure_user_exists(cursor, user_id)

        cursor.execute(
            "SELECT * FROM favorite_streamers WHERE user_id = %s ORDER BY created_at",
            (user_id,)
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

# Remove a favourite
@router.delete("/{twitch_login}", status_code = 204)
def remove_favorite(user_id: int, twitch_login: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        ensure_user_exists(cursor, user_id)

        cursor.execute(
            "DELETE FROM favorite_streamers WHERE user_id = %s AND twitch_login = %s",
            (user_id, twitch_login.lower())
        )
        conn.commit()

        # If the number of rows deleted is 0, it is because the favorite did not exist and a message appears
        if cursor.rowcount == 0:
            raise HTTPException(status_code = 404, detail = "Favourite not found")

    finally:
        cursor.close()
        conn.close()
        