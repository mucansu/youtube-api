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
import requests
from oauth2client.client import HttpAccessTokenRefreshError

path = '/home/mint/mustafa2/youtubeapi/videolar'
uploaded_path='/home/mint/mustafa2/youtubeapi/yüklenen_videolar'
def job():
  global youtube
  filename, id = check_files()
  if filename is None:
   return
    
  url = 'https://ksv.mintyazilim.com/api/course/program/?format=json'
  if id is not None:
    url += '&id=' + id
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    for key, value in data.items():
        print(f"{key}: {value}")
    body = {
        "snippet": {
            "title": data["title"],
            "description": data["description"], 
            "keywords" : id,
            "file": os.path.join(path, filename), 
            "category": data["categoryId"],
            
             
        },
        "status": {
            "privacyStatus": "unlisted",
        }
    }
    upload_successful = False
    try:
        youtube = get_authenticated_service()      
        initialize_upload(youtube, body)
        upload_successful = True
    except HttpError as e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        
    if upload_successful:      
      move_files(filename)
  else:
      print(f"Error: {response.status_code}")      
def schedule():
    sch.every(70).minutes.do(job)

    while True:
        sch.run_pending()
        time.sleep(1)


def check_files():
    filename = id = None
    for filename in os.listdir(path):
        id = filename.split('.')[0]
        print(id)
    return filename,id
        

def move_files(filename):
    os.rename(os.path.join(path, filename), os.path.join(uploaded_path, filename))
httplib2.RETRIES = 1
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
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
    try:
        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                     http=credentials.authorize(httplib2.Http()))
    except HttpAccessTokenRefreshError:
        # token expired
        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)        
        storage.put(credentials)        
        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, body):
  tags = None
  if body['snippet']['keywords']:
    tags = body['snippet']['keywords'].split(",")
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
  print("something happening")
  schedule()
