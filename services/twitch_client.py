# Communicate with Twitch’s external API and managing tokens
import time
import requests

from configuration.config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

# URL where the token is requested
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
# Starting addresses for the data API
API_URL = "https://api.twitch.tv/helix"
# Maximum wait time in seconds 
TIMEOUT = 10  
# Maximum number of logins per request
MAX_LOGINS = 100 

# Internal variables for storing the token
_token = None
_expires_at = 0.0

class TwitchError(Exception):
    """Raised when something goes wrong while talking to Twitch."""

# Get an app access token
def get_app_token(force_refresh: bool = False) -> str:
    global _token, _expires_at

    # If the credentials are missing from the .env file, it fails with an error message
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        raise TwitchError("Twitch credentials are not configured")

    # Request a new token when it is forced, when there is not yet one, or when there are less than 60 seconds remaining before it expires
    if force_refresh or _token is None or time.time() >= _expires_at - 60:
        try:
            response = requests.post(
                TOKEN_URL,
                data = {
                    "client_id": TWITCH_CLIENT_ID,
                    "client_secret": TWITCH_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                },
                timeout=TIMEOUT,
            )

        # If there is a network failure or the time runs out, a Twitch error is triggered
        except requests.RequestException:
            raise TwitchError("Could not reach Twitch to get an access token")

        # Any response other than 200 is treated as invalid credentials
        if response.status_code != 200:
            raise TwitchError("Twitch rejected the credentials")

        # The token is stored and the expiry time is calculated
        data = response.json()
        _token = data["access_token"]
        _expires_at = time.time() + data["expires_in"]

    return _token

# Send one GET request to the Twitch API with a given token
def _send(path: str, params: list, token: str):
    try:
        return requests.get(
            f"{API_URL}{path}",
            params=params,
            headers={
                "Authorization": f"Bearer {token}",
                "Client-Id": TWITCH_CLIENT_ID,
            },
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        raise TwitchError("Could not reach Twitch")

# The request is made using the current token and if Twitch returns a 401 response a new one is requested
def _twitch_get(path: str, params: list) -> list:
    response = _send(path, params, get_app_token())

    if response.status_code == 401:
        response = _send(path, params, get_app_token(force_refresh=True))

    if response.status_code != 200:
        raise TwitchError(f"Twitch returned status {response.status_code}")

    return response.json()["data"]

# Query an endpoint with many logins, in blocks of up to 100
def _get_by_logins(path: str, param_name: str, logins: list) -> list:
    results = []
    for i in range(0, len(logins), MAX_LOGINS):
        block = logins[i:i + MAX_LOGINS]
        params = [(param_name, login) for login in block]
        results.extend(_twitch_get(path, params))
    return results

# Check if the login exist on Twitch
def streamer_exists(login: str) -> bool:
    return len(_get_by_logins("/users", "login", [login])) > 0

# Profile and live status for a list of logins
def get_streamers_info(logins: list) -> list:
    # If the list is empty, it returns an empty list 
    if not logins:
        return []

    # ‘users’ displays each streamer’s profile, whilst ‘streamers’ only shows those who are currently live 
    users = _get_by_logins("/users", "login", logins)
    streams = _get_by_logins("/streams", "user_login", logins)

    # The list of live streams is converted into a dictionary so you can check whether a streamer is live by performing a direct search
    live = {stream["user_login"].lower(): stream for stream in streams}

    # For each user, the system checks whether there is a live stream and builds a dictionary containing the fields from 'FavoriteStreamerInfo'
    info = []
    for user in users:
        stream = live.get(user["login"].lower())
        info.append({
            "twitch_id": user["id"],
            "login": user["login"],
            "display_name": user["display_name"],
            "is_live": stream is not None,
            "stream_title": stream["title"] if stream else None,
            "game_name": stream["game_name"] if stream else None,
            "viewer_count": stream["viewer_count"] if stream else None,
        })
    return info
