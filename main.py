import sys
import time
import requests
from PyQt5 import QtWidgets
import mutagen
from PyQt5.QtWidgets import QMessageBox


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = None

        self.setWindowTitle("MP3 File Browser")

        self.table_widget = QtWidgets.QTableWidget(0, 2)
        self.table_widget.setHorizontalHeaderLabels(["Title", "Artist"])
        self.setCentralWidget(self.table_widget)

        self.browse_button = QtWidgets.QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.on_browse)

        self.apply_button = QtWidgets.QPushButton("Apply", self)
        self.apply_button.clicked.connect(self.apply_tags)

        self.statusBar().addPermanentWidget(self.browse_button)
        self.statusBar().addPermanentWidget(self.apply_button)

        self.table_widget.setColumnWidth(0, 200)

    def on_browse(self):
        # Clear previously occupied rows
        while(self.table_widget.rowCount() > 0):
            self.table_widget.removeRow(0)

        # Allow user to select files
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select MP3 files", "",
                                                          "MP3 Files (*.mp3);;All Files (*)", options=options)
        # Display each mp3 file in rows
        if files:
            self.files = files
            for file in files:
                audio = mutagen.File(file, easy=True)
                artist = audio.get('artist', '')[0]
                title = audio.get('title', '')[0]
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                title_item = QtWidgets.QTableWidgetItem(title)
                self.table_widget.setItem(row, 0, title_item)
                artist_item = QtWidgets.QTableWidgetItem(artist)
                self.table_widget.setItem(row, 1, artist_item)

    def apply_tags(self):
        # Ask user for confirmation to apply tags
        q = QMessageBox()
        res = q.question(self, '', "Are you sure you would like to apply tags to " + str(len(self.files)) + " files?", q.Yes | q.No)
        if res == q.No:
            return

        client_id = 'b24805fd018e49baaa264c4ec5a3e589'
        client_secret = '28f8442ab43d4bcfb3be6cb95878effd'

        # Obtain an access token
        token_response = requests.post('https://accounts.spotify.com/api/token',
                                       data={'grant_type': 'client_credentials'},
                                       auth=(client_id, client_secret))

        access_token = token_response.json()['access_token']

        # Set the authorization header with the access token
        headers = {'Authorization': f'Bearer {access_token}'}

        # Some constants
        count = 0
        successful_tags = 0
        unsuccessful_tags = []

        for file_name in self.files:
            audio = mutagen.File(file_name, easy=True)

            # Extract the artist and title from the MP3 file metadata
            artist = audio.get('artist', '')[0]
            title = audio.get('title', '')[0]

            # Remove parenthesis, apostrophes, and "Ft." from title and artist
            pos1 = title.find("(")
            if pos1 != -1:
                title = title[:pos1]
            pos1 = artist.find("Ft.")
            if pos1 != -1:
                artist = artist[:pos1]
            artist = artist.replace("'", "")
            title = title.replace("'", "")

            # Send a request to the Spotify API to search for the song
            response = requests.get('https://api.spotify.com/v1/search', headers=headers, params={
                'q': f'track:{title} artist:{artist}',
                'type': 'track',
            })

            if response.status_code == 200:
                # Get the first result from the search IF spotify has the song
                if response.json()['tracks']['items']:
                    song_result = response.json()['tracks']['items'][0]
                    if song_result:
                        song_id = song_result['id']
                        response = requests.get(f'https://api.spotify.com/v1/tracks/{song_id}', headers=headers)
                        # Extract the release date and boolean value of explicit, and tag mp3 file.
                        explicit = response.json()['explicit']
                        release_date = response.json()['album']['release_date']
                        audio['date'] = release_date
                        if explicit:
                            audio["version"] = ["Explicit"]
                        else:
                            audio["version"] = ["Clean"]
                        audio.save()
                        successful_tags += 1
                    else:
                        unsuccessful_tags.append(title)
                else:
                    unsuccessful_tags.append(title)
            count += 1
            # Sleep to avoid "too many requests" error
            time.sleep(0.5)

            # Limit search to 100 files to avoid "too many requests" as well
            if count == 100:
                break
        if len(unsuccessful_tags) > 0:
            self.show_error_popup(unsuccessful_tags)
        else:
            self.show_success_popup(successful_tags)

    def show_error_popup(self, array):
        # Show dialog box for songs that were unable to be tagged
        msg = QMessageBox()
        msg.setWindowTitle("Mp3 Tagger")
        text_to_display = f"{len(array)} files were not able to be tagged while {len(self.files) - len(array)} were " \
                          f"successful, may be due to a misspelled song or not available through the Spotify API." \
                          f" Click more details to view untagged songs. \n"
        msg.setText(text_to_display)
        text_to_display = ""
        for name in array:
            text_to_display += name + "\n"

        msg.setDetailedText(text_to_display)

        x = msg.exec_()

    def show_success_popup(self, amount):
        # Show dialog box for 100% successful files tagged.
        msg = QMessageBox()
        msg.setWindowTitle("Mp3 Tagger")

        text_to_display = str(amount) + " files were added successfully!"
        msg.setText(text_to_display)

        x = msg.exec_()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Set window size to 900 x 500 and center it.
    screen_resolution = app.desktop().screenGeometry()
    screen_width = screen_resolution.width()
    screen_height = screen_resolution.height()
    window_width = 900
    window_height = 500
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2
    window = MainWindow()
    window.setGeometry(x_coordinate, y_coordinate, window_width, window_height)
    window.show()

    sys.exit(app.exec_())
