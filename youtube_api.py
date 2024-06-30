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

class YoutubeService:
    def __init__(self):
        CLIENT_SECRETS_FILE = "client_secrets.json"
        YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
        YOUTUBE_SCOPES = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]

        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

        
        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,scope=YOUTUBE_SCOPES,message="Kimlik doğerulamada hata oluştu.")

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)
            try:
                return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,http=credentials.authorize(httplib2.Http()))
            except HttpAccessTokenRefreshError:
                # token expired, aynı giriş bilgileri ile refresh ediyoruz.
                http = credentials.authorize(httplib2.Http())
                credentials.refresh(http)

            # yenilenmiş token ile yeniden işleme devam ediyoruz
            storage.put(credentials)

        # servisi tekrar çalıştırıyoruz
        self.API =  build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,http=credentials.authorize(httplib2.Http()))
        print('self.API',self.API)
    
    def upload_video(self,body):
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

        insert_request = self.API.videos().insert(
            part=",".join(upload_body.keys()),
            body=upload_body,       
            media_body=MediaFileUpload(body['snippet']['file'], chunksize=-1, resumable=True)
        )

        self.resumable_upload(insert_request)

    def resumable_upload(self,insert_request):
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
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,e.content)
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
            
            
    
    def get_videos(self):     
        # search_response = self.API.search().list(
        #     q='KATI CUMA 19:00 ON',
        #     part='id,snippet',
        #     maxResults=100
        # ).execute()
            
        response = self.API.search().list(  
            forMine=True,
            part="id,snippet",            
            maxResults=50 ,
            type='video'
            
        ).execute()
        # response = search_response        
        print(f"response : {response}")
        for item in response['items']:
            # print(f"item : {item}")
            for key,value in item.items():
                print(f"{key}: {value}")
        
        return response
        # return self.get_videos_detail(response['items'])
        
