#!/usr/bin/python

import httplib2
import os
import random
import sys
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

watchdog_dict = {}
uploaded_ID = {}
# Define event handler for file creation events
class VideoHandler(FileSystemEventHandler):
  def on_created(self, event):
    if event.is_directory:
      return

    file_path = event.src_path
    file_name = os.path.basename(file_path)
    id = file_name.split("/")[-1].split('.')[0]
    print(file_path)
   
    if id in uploaded_ID:
      return
    uploaded_ID[id] = True
   
    if id not in watchdog_dict:
      watchdog_dict[id] = {
        'path': file_path,
        'created_at': time.time()
      }
  

httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
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

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube,file, body):
  tags = None
  if body.keywords:
    tags = body.keywords.split(",")

  # Call the API's videos.insert method to create and upload the video.
  #body ile birlikte API anahtarını keys içerisinde almamız gerekiyor. Bunu djangodaki servise hard code olarak 
  #eklemek lazım.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

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
  path='//home/mint/mustafa2/youtubeapi/videolar'
  event_handler = VideoHandler()
  observer = Observer()
  observer.schedule(event_handler, path, recursive=True)
  observer.start()
  # Keep the script running to continue monitoring
  try:
    while True:
      time.sleep(600) # 10 dk de bir kontrol edecek
  except KeyboardInterrupt:
  # Stop the observer if the script is interrupted
    observer.stop()

# Wait for the observer to finish
  observer.join()
  
  #body diğer servisten obje olarak gelecek
  #bu objenin attribute lerine (body.file, body.description, body.keywords vs.) ulasabiliriz 
  url='https://ksv.mintyazilim.com/api/course/program/?format=json&id=' + id
  response=requests.get(url)
  #if response is None:
  # exit("Istenen ders bilgileri alınamadı")
  
  if response.status_code != 200:
    exit("Istenen ders bilgileri alınamadı")

  try:
    body = response.json()
    #burada file bir video dosyasını ifade ediyor, bu video klasörünün yeri de response dan alınıyor.
    #Halbuki klasöre erişen biz bu script ile erişiyoruz, path işini burda çözüp sadece id ile bilgileri alsak?
    #Video klasörünün yeri sabit olacağı için bunu hard code ile belirtebiliriz.

    #Video_directory = "/videolar/"
    #file = Video_directory + filename
    
    file = body.file
    #id sadece istek gönderirken lazım, file ise video dosyasının tam adı. 
    #filename = id
    id = body.file.split("/")[-1].split('.')[0]
  except ValueError:
    exit("Gelen veri formatı hatalı")
  
  """body = response.json()
  id=filename=body.file.split("/")[-1].split('.')[0] 
  file = body.file"""
  
  if not os.path.exists(file):
    exit("Istenen video bulunamadı")

  youtube = get_authenticated_service()
  try:
    initialize_upload(youtube,file,body)
  except HttpError as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

  