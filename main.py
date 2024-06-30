import time
import schedule as sch
from utils import utils
from googleapiclient.errors import HttpError

from youtube_api import YoutubeService

youtube  = None
 
def job():  
    # utils.read_settings()     
    files = utils.get_files()
  
    if not files:
        print("Yüklenecek dosya bulunamadı")
        return
    
    for file in files:        
        body = utils.get_body_from_api(file)
        # utils.move_file(file['name'])
        if body and youtube:
            
            try:
                print ("Video yükleniyor...")
                youtube.upload_video(body)                                
                utils.move_file(file['name'])                                
                
            except HttpError as e:
                print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
       
            except:
                print("Video yüklenemedi")
            
def schedule(second):
    sch.every(second).seconds.do(job)
    while True:
        sch.run_pending()
        time.sleep(1)
        
        
if __name__ == '__main__':     
    youtube = YoutubeService()    
    result = youtube.get_videos()
    
    # schedule(10)