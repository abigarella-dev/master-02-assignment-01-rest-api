# Manage users
from fastapi import APIRouter, HTTPException
import mysql.connector

from configuration.database import get_connection
from models.users import UserCreate, UserUpdate, UserResponse

# Create the user router
router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)

# Register a new user
@router.post("", response_model = UserResponse, status_code = 201)
def create_user(user: UserCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)", 
            (user.username, user.email)
        )
        conn.commit()

        cursor.execute(
            "SELECT * FROM users WHERE id = %s", 
            (cursor.lastrowid,)
        )
        return cursor.fetchone()

    # If the user already exists, the action is undone and a conflict message is displayed 
    except mysql.connector.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code = 409,
            detail = "The username or email address already exists"
        )

    finally:
        cursor.close()
        conn.close()

# List all users
@router.get("", response_model = list[UserResponse])
def list_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try: 
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

# Get a single user
@router.get("/{user_id}", response_model = UserResponse)
def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if user is None:
            raise HTTPException(status_code = 404, detail = "User not found")
        
        return user

    finally:
        cursor.close()
        conn.close()

# Update a user
@router.patch("/{user_id}", response_model = UserResponse)
def update_user(user_id: int, user: UserUpdate):
    # Only the changes sent by the client are updated, e.g. email
    changes = user.model_dump(exclude_unset = True, exclude_none = True)

    # If the client does not send anything
    if not changes:
        raise HTTPException(status_code = 400, detail = "No fields to update")

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        # A check is carried out to see if the user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code = 404, detail = "User not found")

        # The update is generated using only the fields received
        set_clause = ", ".join(f"{field} = %s" for field in changes)
        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE id = %s",
            (*changes.values(), user_id)
        )
        conn.commit()

        # The updated user is returned
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()

    # If the user already exists, the action is undone and a conflict message is displayed 
    except mysql.connector.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code = 409,
            detail = "The username or email address already exists"
        )

    finally:
        cursor.close()
        conn.close()

# Delete a user
@router.delete("/{user_id}", status_code = 204)
def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        # If the number of rows deleted is 0, it is because the user did not exist and a message appears
        if cursor.rowcount == 0:
            raise HTTPException(status_code = 404, detail = "User not found")

    finally:
        cursor.close()
        conn.close()
