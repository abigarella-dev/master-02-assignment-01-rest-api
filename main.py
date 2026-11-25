from fastapi import FastAPI
from routers import users, streamers, twitch

# Create the app
app = FastAPI(
    title = "Twitch API",
    description = "REST API for managing users and their favourite streamers via Twitch",
)

# Register the endpoints for each router within the app
app.include_router(users.router)
app.include_router(streamers.router)
app.include_router(twitch.router)

# Initial welcome endpoint
@app.get("/")
def root():
    return{
        "message": "Welcome to the Twitch API",
    }
