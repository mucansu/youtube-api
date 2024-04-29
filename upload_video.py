#!/usr/bin/python

import httplib2
import os
import random
import sys
import time
import schedule
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import schedule as sch


"""
path = '/home/mint/mustafa2/youtubeapi/video'
for filename in os.listdir(path):
    print(filename)
"""
path = '/home/mint/mustafa2/youtubeapi/videolar'
uploaded_path='/home/mint/mustafa2/youtubeapi/yüklenen_videolar'
def job():
    print("I'm working...")
    filename, id = check_files()
    body = {
        "snippet": {
            "file": os.path.join(path, filename), 
            "title": "Test Title",
            "description": "Test Description", 
            "keywords": "", 
            "category": "22" 
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    try:
        initialize_upload(youtube, body)
        print("Video uploaded")
    except HttpError as e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
    move_files(filename)
def schedule():
    sch.every(10).seconds.do(job)

    while True:
        sch.run_pending()
        time.sleep(1)


def check_files():
    for filename in os.listdir(path):
        id = filename.split('.')[0]
        print(id)
    return filename,id
        

def move_files(filename):
    os.rename(os.path.join(path, filename), os.path.join(uploaded_path, filename))
    print("Dosya taşındı")

"""
def get_video_info(file, title="Test Title", description="Test Description", category="22", keywords="egitim,bilgi", privacyStatus='public'):
    video_info = {
        "file": file,
        "title": title,
        "description": description,
        "category": category,
        "keywords": keywords,
        "privacyStatus": privacyStatus
    }
    return video_info"""

# Tekrar deneme işini kendimiz uygulamada yaptığımız için bu pakete kafasına göre ikinci kez deneme yapmamasını söylüyoruz
# Biz deneme mantığını kendimiz yapacağız.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.cloud.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, body):
  tags = None
  if body['snippet']['keywords']:
    tags = body['snippet']['keywords'].split(",")

# Bu kısımda video nesnesini oluşturuyoruz, ve bilgilerini de (başlık, acıklama, etiketler vs.) ekliyoruz.
# bu bilgileri client tarafından almış olmamız gerekiyor, client tarafında bu bilgilerin nasıl işlendiğini
# görmem lazım. 
  upload_body=dict( 
        snippet=dict(
            title=body['snippet']['title'],
            description=body['snippet']['description'],
            tags=tags,
            categoryId=body['snippet']['category']
        ),
        status=dict(
            privacyStatus=body['status']['privacyStatus']
        )
    )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(upload_body.keys()),
    body=upload_body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(body['snippet']['file'], chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print ("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print ("Video id '%s' was successfully uploaded." % response['id'])
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print (error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print ("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)
if __name__ == '__main__':
  path = '/home/mint/mustafa2/youtubeapi/videolar'
  uploaded_path='/home/mint/mustafa2/youtubeapi/yüklenen_videolar'
  body = {
        "snippet": {
            "file": path, 
            "title": "Deneme başlık",  
            "description": "Deneme açıklama",
            "keywords": "egitim,ders",
            "category": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

  if not os.path.exists(body['snippet']['file']):
    exit("Please specify a valid file using the --file= parameter.")

  youtube = get_authenticated_service()
  schedule()
  