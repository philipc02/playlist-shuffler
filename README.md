# Spotify Playlist Shuffler

This is a Flask application that allows users to create a shuffled playlist from their existing Spotify playlists.

## Setup Instructions

1. **Clone the Repository**
    ```sh
    git clone https://github.com/philipc02/playlist-shuffler.git
    ```

2. **Install Dependencies**
    ```sh
    -
    ```

3. **Create a .env File**

    Create a `.env` file in the root directory of the project and add your Spotify API credentials:
    ```env
    CLIENT_ID=your_spotify_client_id
    CLIENT_SECRET=your_spotify_client_secret
    REDIRECT_URI=http://localhost:5000/callback
    ```

4. **Run the Application**
    ```sh
    flask run
    ```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`.
2. Log in with your Spotify account and authorize the application.
3. Enter the IDs of the playlists you want to shuffle.
4. Submit the form to create a new shuffled playlist.

## Disclaimer

This application is for educational purposes only. Please ensure that your usage complies with Spotify's API Terms of Service.

## License

This project is licensed under the GNU General Public License - see the [LICENSE](LICENSE) file for details.