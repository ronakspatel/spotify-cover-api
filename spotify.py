import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Get access token
def get_token():
    auth_url = "https://accounts.spotify.com/api/token"
    response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    response.raise_for_status()
    return response.json()['access_token']

# Get artist ID by name
def get_artist_id(token, artist_name):
    headers = {"Authorization": f"Bearer {token}"}
    search_url = f"https://api.spotify.com/v1/search"
    params = {'q': artist_name, 'type': 'artist', 'limit': 1}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    items = response.json()['artists']['items']
    return items[0]['id'] if items else None

# Get album cover art URLs
def get_album_art(token, artist_id):
    headers = {"Authorization": f"Bearer {token}"}
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        'include_groups': 'album,single',
        'limit': 10,
        'market': 'US'
    }

    seen = set()
    cover_urls = []

    while albums_url:
        response = requests.get(albums_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        for album in data['items']:
            name = album['name']
            if name not in seen:
                seen.add(name)
                image_url = album['images'][0]['url']  # Largest image
                cover_urls.append((name, image_url))

        albums_url = data.get('next')  # Handle pagination
        params = None  # only needed for first request

    return cover_urls

if __name__ == "__main__":
    token = get_token()
    artist_id = get_artist_id(token, "Travis Scott")
    if artist_id:
        albums = get_album_art(token, artist_id)
        for name, url in albums:
            print(f"{name}: {url}")
    else:
        print("Artist not found.")
