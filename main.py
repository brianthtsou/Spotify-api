from dotenv import load_dotenv
from playlists import create_new_playlist
import os
import requests
import json

# load in .env file
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_id = os.getenv("USER_ID")

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST request to retrieve access token
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

# get the header that must be included in API calls
def get_auth_header(token):
    header = {
        "Authorization": f"Bearer {token}"
    }
    return header

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    header = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = requests.get(query_url, headers=header)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist found with that name.")
        return None

    return json_result[0]

def get_artist_top_tracks(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    header = get_auth_header(token)
    result = requests.get(url, headers=header)
    json_result = json.loads(result.content)["tracks"]

    if len(json_result) == 0:
        print("No top tracks available.")
        return None

    return json_result
def get_artist_id(token, artist_name):
    return search_for_artist(token, artist_name)["id"]

def get_user_playlists(token):
    url =f"https://api.spotify.com/v1/users/{user_id}/playlists"
    header = get_auth_header(token)
    result = requests.get(url, headers=header)
    json_result = json.loads(result.content)

    if len(json_result) == 0:
        print("No playlists available.")
        return None

    return json_result
# drake_id = (get_artist_id(access_token, "Drake"))
# songs = get_artist_top_tracks(access_token, drake_id)
#
# for i, song in enumerate(songs):
#     print(f"{i+1}. {song['name']}")

##for reading json
#print(json.dumps(get_artist_top_tracks(access_token, drake_id), indent=2))

def create_new_playlist(token):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    temp_header = {}
    temp_header["Content Type"] = "application/json"
    header = get_auth_header(token)
    temp_header.update(header)
    print(temp_header)
    request_body = json.dumps({
        "name": "New Playlist",
        "description": "New playlist description",
        "public": False
    })
    result = requests.post(url = url, data = request_body, headers = temp_header)
    return result


def create_playlist_test(token):
    user_id = "hiitsbriant"
    endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    request_body = json.dumps({
        "name": "Indie bands like Franz Ferdinand but using Python",
        "description": "My first programmatic playlist, yooo!",
        "public": True  # let's keep it between us - for now
    })
    response = requests.post(url=endpoint_url, data=request_body, headers={"Content-Type": "application/json",
                                                                           "Authorization": f"Bearer {token}"})
    print(response)

def get_user_id(token):
    url = "https://api.spotify.com/v1/me"
    header = get_auth_header(token)
    result = requests.get(url, header)
    json_result = json.loads(result.content)
    return json_result


create_playlist_test(access_token)
