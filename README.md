# YouTube API Scheduler

## Description
This project is a Python script designed to automate the process of uploading videos to YouTube using the YouTube Data API. It allows users to schedule video uploads from a specified directory to their YouTube channel. The script retrieves video details from an external API, such as title, description, keywords, and category, and uploads the videos to YouTube with the specified privacy status.

## Features
- Automatic scheduling of video uploads.
- Retrieves video details from an external API.

## Installation
1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Install the required Python packages using the provided requirements file:

pip install -r requirements.txt

4. Obtain OAuth 2.0 credentials from the Google Cloud Console and save them as `client_secrets.json` in the project directory. Follow the instructions in the [Google API Client Library documentation](https://developers.google.com/api-client-library/python/guide/aaa_client_secrets) for more details.
5. Ensure that the directory paths for video files and uploaded videos are correctly set in the script (`path` and `uploaded_path` variables) in your own environment.

## Usage
1. Run the script by executing the following command in the terminal:

python youtube_api_scheduler.py

2. The script will continuously monitor the specified directory for video files.
3. When a new video file is detected, it retrieves details from the external API and uploads the video to YouTube with the specified privacy status (unlisted by default).
4. Uploaded videos are moved to the specified directory for uploaded videos.

**Note:** Ensure that the Google Cloud project associated with the OAuth 2.0 credentials has the YouTube Data API enabled. 


## References
- [Google API Client Library for Python Documentation](https://developers.google.com/api-client-library/python)
- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)  
