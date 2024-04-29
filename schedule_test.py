import os
import schedule as sch
import time
from upload_video import get_authenticated_service, get_video_info, initialize_upload
import upload_video as up
"""
path = '/home/mint/mustafa2/youtubeapi/video'
for filename in os.listdir(path):
    print(filename)
"""
def job():
    print("I'm working...")
    check_files()
def schedule():
    sch.every(10).seconds.do(job)

    while True:
        sch.run_pending()
        time.sleep(1)
        

if __name__ == '__main__':
    schedule()

def check_files():
    path = '/home/mint/mustafa2/youtubeapi/videolar'
    uploaded_path='/home/mint/mustafa2/youtubeapi/yüklenen_videolar'
    for filename in os.listdir(path):
        id = filename.split('.')[0]
        print(id)
        if not os.path.exists(os.path.join(uploaded_path, filename)):     
            
            youtube = up.get_authenticated_service()
            video_info = up.get_video_info(os.path.join(path, filename), title='Ders 1', description="Bu bir ders videosu " + id)        
            up.initialize_upload(youtube, video_info)
            os.rename(os.path.join(path, filename), os.path.join(uploaded_path, filename))     
            print("Video yüklendi")
        else:
            print(f"Dosya {filename} zaten yüklenmişti.")