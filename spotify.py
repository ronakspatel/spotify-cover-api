from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_spotify_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Missing Spotify credentials in .env")

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to authenticate with Spotify")

    return response.json()["access_token"]

@app.get("/cover")
def get_album_cover(track: str, artist: str):
    token = get_spotify_token()
    search_url = "https://api.spotify.com/v1/search"
    query = f"{track} {artist}"  # loosened query
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 1}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Spotify search failed")

    results = response.json().get("tracks", {}).get("items")
    if not results:
        print("Spotify search returned:", response.json())  # helpful for debugging
        raise HTTPException(status_code=404, detail="No track found")

    track_data = results[0]
    album = track_data["album"]
    return {
        "track": track_data["name"],
        "artist": track_data["artists"][0]["name"],
        "album": album["name"],
        "cover_url": album["images"][0]["url"],
        "duration_ms": track_data["duration_ms"]
    }
