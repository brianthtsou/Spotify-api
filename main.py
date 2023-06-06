from dotenv import load_dotenv
import os
import requests
import json

# load in .env file
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

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

drake_id = (get_artist_id(access_token, "Drake"))
songs = get_artist_top_tracks(access_token, drake_id)

for i, song in enumerate(songs):
    print(f"{i+1}. {song['name']}")

##for reading json
#print(json.dumps(get_artist_top_tracks(access_token, drake_id), indent=2))