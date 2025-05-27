from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import requests
import time

# Load environment variables from .env
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Caching access token
cached_token = None
token_expiry = 0

app = FastAPI()

def get_access_token():
    global cached_token, token_expiry
    current_time = time.time()
    if cached_token and current_time < token_expiry:
        return cached_token

    token_url = "https://accounts.spotify.com/api/token"
    response = requests.post(
        token_url,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get access token")

    data = response.json()
    cached_token = data["access_token"]
    token_expiry = current_time + data["expires_in"] - 60  # Refresh 1 minute early

    return cached_token

@app.get("/album-art")
def get_album_art(title: str, artist: str):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    query = f"track:{title} artist:{artist}"
    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params={"q": query, "type": "track", "limit": 1}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Spotify API error")

    results = response.json()["tracks"]["items"]
    if not results:
        raise HTTPException(status_code=404, detail="Track not found")

    track = results[0]
    album = track["album"]
    image_url = album["images"][0]["url"]

    return JSONResponse({
        "track": track["name"],
        "artist": artist,
        "album": album["name"],
        "image_url": image_url
    })
