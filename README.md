# Mp3-File-Tagger
This windows desktop application written in Python is able to tag mp3 files with the year of the song and whether or not it is explicit using the Spotify API.
The application uses the title and artist on an mp3 file to search for the release year from the Spotify API.

You can browse through your computer's files and select multiple mp3 files to tag.
![img1](https://user-images.githubusercontent.com/51735830/211785025-65a8ce56-eeb4-4d8d-8138-b98c616c1293.png)

The application will ask you to confirm whether or not you want to tag those selected files or not.
![img2](https://user-images.githubusercontent.com/51735830/211785186-156827e4-a7ab-439d-a2ef-9e7400e88142.png)

The application will either show you a 100% success for tagged files:

![img3](https://user-images.githubusercontent.com/51735830/211785288-ac359fa6-957d-4900-8bf3-4a1184cae796.png)

or will show an error, the amount of successful and unsuccessful tags, and a list of the names of the songs that were unable to be tagged:
![img4](https://user-images.githubusercontent.com/51735830/211785315-350fb18a-b6d3-464b-bdfe-9d55d7c3badd.png)

During this project I got more practice with reading json data and understanding how to use the debugger to figure out what information I need when working with API responses.
