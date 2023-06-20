from flask import Flask, request, url_for, session, redirect, render_template
from datetime import date
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

#login page that connects directly to spotify to get user permissions
@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

#
@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("index", _external=True))

@app.route('/getTopTracks', methods=['GET'])
def getTopTracks(scope="", num=0):
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for("login", _external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    global current_top_track_scope
    # num = 5 by default, 10/15/20 by user selection
    # scope = short_term by default, medium_term/long_term by user selection
    num = int(request.args.get('num'))
    scope = str(request.args.get('scope'))
    current_top_track_scope = scope
    # retrieve (limit) number of top tracks as a json, stored in result
    result = sp.current_user_top_tracks(limit=num, offset=0, time_range=scope)
    tracks = []
    final_list = get_top_tracks_and_artists(num=num, result=result) # for storing final 'song' : 'artist' dictionary
    return render_template('userTopTracks.html', tracks = final_list, current_scope = scope)


@app.route('/createEmptyPlaylist')
def createEmptyPlaylist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for("login", _external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.user_playlist_create(user_id, "New Playlist", public=True, collaborative=False, description="blank")
    return render_template('playlistCreated.html')

# !!!! this function needs to be completed!!! use recommend function using 'result' as seed, then add to playlist
@app.route('/createDiscoveryPlaylist')
def createDiscoveryPlaylist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for("login", _external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    today = str(date.today())
    sp.user_playlist_create(user_id, f"Discovery - {today}", public=True, collaborative=False, description=f"{today}")

    # pulls 20 short term top tracks from spotify as json, use as recommend function seeds
    result = sp.current_user_top_tracks(limit=20, offset=0, time_range="short_term")
    return render_template('playlistCreated.html')

@app.route('/CrPlaylistSelectionPage')
def CrPlaylistSelectionPage():
    return render_template('playlistSelection.html')

# retirieving authentication token
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

# creating spotify oauth authentication object
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=url_for("redirectPage", _external=True),
        scope=("user-library-read, playlist-modify-public, user-top-read")
        #playlist-modify-public
    )

# method that parses for track name and artists name from api json file, returns
# a dictionary of user's top tracks + associated artists
def get_top_tracks_and_artists(num, result):
    #result = json file from spotify
    final_list = {}
    for track in range(num):
        artist_list = result['items'][track]['artists']
        artists = []
        for artist in range(len(artist_list)):
            artists.append(artist_list[artist]["name"])

        all_artists = ', '.join(artists) #in case of multiple artists, all need to be on one string

        track_name = str(result['items'][track]['name'])
        final_list[track_name] = all_artists
    return final_list
