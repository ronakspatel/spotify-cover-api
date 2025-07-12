import requests
from urllib.parse import quote
from PIL import Image
from io import BytesIO

def get_album_art(track, artist, api_base_url):
    query = f"{api_base_url}?track={quote(track)}&artist={quote(artist)}"
    response = requests.get(query)

    if response.status_code == 200:
        try:
            data = response.json()
            cover_url = data.get("cover_url")
            if not cover_url:
                print("No 'cover_url' in response.")
                return None
            
            # Fetch the actual image
            image_response = requests.get(cover_url)
            if image_response.status_code == 200:
                img = Image.open(BytesIO(image_response.content))
                img = img.resize((128, 128), Image.Resampling.LANCZOS)  # Use modern Pillow resampling
                return img
            else:
                print(f"Failed to fetch image: {image_response.status_code}")
                return None
        except Exception as e:
            print("Error parsing JSON or fetching image:", e)
            return None
    else:
        print(f"API error {response.status_code}: {response.text}")
        return None

# ==== Test the API ====
if __name__ == "__main__":
    api_url = "https://spotify-cover-api.onrender.com/cover"
    track = input("Enter track title: ")
    artist = input("Enter artist name: ")

    album_cover = get_album_art(track, artist, api_url)
    if album_cover:
        album_cover.show()