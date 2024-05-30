import requests
from flask import Flask, request, redirect, session, jsonify, render_template
import os
import random
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Spotify app credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state playlist-modify-private'  

# Authorization endpoint
AUTH_URL = f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}'

# Token endpoint
TOKEN_URL = 'https://accounts.spotify.com/api/token'

@app.route('/')
def index():
    return redirect(AUTH_URL)

@app.route('/callback')
def callback():
    code = request.args.get('code')

    # Exchange authorization code for tokens
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    
    # Debugging: Print the response content
    print("Response from Spotify token exchange:", response.text)
    
    token_data = response.json()

    # Check if access_token is in the response
    if 'access_token' in token_data:
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        return redirect('/playlist')
    else:
        # Handle the error and provide feedback
        return jsonify({'error': 'Failed to retrieve access token', 'details': token_data}), 400

@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    if request.method == 'POST':
        access_token = session.get('access_token')

        if access_token:
            playlist_ids_input = request.form.get('playlist_ids')
            playlist_ids = playlist_ids_input.split(',')  # Split input by commas
            playlist_names = []
            if not playlist_ids:
                return jsonify({'error': 'No playlist IDs provided'})

            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            all_tracks = []
            for playlist_id in playlist_ids:
                response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id.strip()}', headers=headers)  # Trim whitespace around IDs
                data = response.json()
                playlist_name = data.get('name')
                playlist_names.append(playlist_name)
                if playlist_name:
                    tracks = [item['track']['uri'] for item in data['tracks']['items']]
                    all_tracks.extend(tracks)
                else:
                    return jsonify({'error': f'Error retrieving playlist with ID {playlist_id.strip()}'})

            random.shuffle(all_tracks)

            # Combine playlist names
            #playlist_names = [data.get('name') for data in playlist_data]
            new_playlist_name = ' x '.join(playlist_name for playlist_name in playlist_names)

            # Create a new playlist
            playlist_description = 'A playlist created by shuffling tracks from other playlists.'
            playlist_id = create_playlist(access_token, new_playlist_name, playlist_description)

            if playlist_id:
                # Add the shuffled tracks to the new playlist
                add_tracks_to_playlist(access_token, playlist_id, all_tracks)
                play_playlist(access_token, playlist_id)

                return jsonify({'message': 'Playlist created successfully'})
            else:
                return jsonify({'error': 'Error creating playlist'})
        else:
            return jsonify({'error': 'Access token not found. Please authorize your application.'})
    else:
        return render_template('playlist.html')


def play_playlist(access_token, playlist_id):
    context_uri = f'spotify:playlist:{playlist_id}'

    url = 'https://api.spotify.com/v1/me/player/play'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'context_uri': context_uri
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 204:
        print('Playback started successfully.')
    else:
        print(f'Error starting playback: {response.status_code}, {response.text}')

def create_playlist(access_token, name, description):
    url = 'https://api.spotify.com/v1/me/playlists'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': name,
        'description': description,
        'public': False,  # Change to True if you want the playlist to be public
        'preload_tracks': True  # Preload tracks when creating the playlist
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        playlist_id = response.json().get('id')
        return playlist_id
    else:
        error_message = f'Error creating playlist: {response.status_code}, {response.text}'
        print(error_message)  # Print error message for debugging
        return None

def add_tracks_to_playlist(access_token, playlist_id, tracks):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'uris': tracks
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 201

if __name__ == '__main__':
    app.run(debug=True)
