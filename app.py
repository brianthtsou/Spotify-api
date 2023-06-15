from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
from dotenv import load_dotenv
import json

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'Spotify App'
TOKEN_INFO = "token_info"
user_id = os.getenv("USER_ID")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("index", _external=True))

@app.route('/getTopTracks')
def getTopTracks():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for("login", _external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    result = sp.current_user_top_tracks(limit=5, offset=0, time_range='short_term')
    tracks = []
    for track in range(5):
         print(str(result['items'][track]['name']))
         tracks.append(str(result['items'][track]['name']))

    return render_template('userTopTracks.html', tracks = tracks)


@app.route('/createPlaylist')
def createPlaylist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for("login", _external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.user_playlist_create(user_id, "New Playlist", public=True, collaborative=False, description="test")
    return "Playlist successfully created!"

@app.route('/CrPlaylistSelectionPage')
def CrPlaylistSelectionPage():
    return render_template('playlistSelection.html')

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=url_for("redirectPage", _external=True),
        scope=("user-library-read, playlist-modify-public, user-top-read")
        #playlist-modify-public
    )

