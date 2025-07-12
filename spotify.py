from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
import base64
from PIL import Image
from io import BytesIO

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

@app.get("/cover.bmp")
def get_album_cover_bmp(track: str = Query(...), artist: str = Query(...)):
    token = get_spotify_token()
    search_url = "https://api.spotify.com/v1/search"
    query = f"track:{track} artist:{artist}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 1}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Spotify search failed")

    results = response.json().get("tracks", {}).get("items")
    if not results:
        raise HTTPException(status_code=404, detail="No track found")

    cover_url = results[0]["album"]["images"][0]["url"]

    img_response = requests.get(cover_url)
    if img_response.status_code != 200:
        raise HTTPException(status_code=img_response.status_code, detail="Failed to fetch album cover")

    img = Image.open(BytesIO(img_response.content)).convert("RGB")
    img = img.resize((128, 128), Image.LANCZOS)

    bmp_io = BytesIO()
    img.save(bmp_io, format="BMP")
    bmp_bytes = bmp_io.getvalue()

    return Response(content=bmp_bytes, media_type="image/bmp")
