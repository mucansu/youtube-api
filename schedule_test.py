import os
import schedule as sch
import time
from upload_video import get_authenticated_service, get_video_info, initialize_upload
"""
path = '/home/mint/mustafa2/youtubeapi/video'
for filename in os.listdir(path):
    print(filename)
"""
path = '/home/mint/mustafa2/youtubeapi/videolar'
uploaded_path='/home/mint/mustafa2/youtubeapi/yüklenen_videolar'
def job():
    print("I'm working...")
    check_files()
def schedule():
    sch.every(10).seconds.do(job)

    while True:
        sch.run_pending()
        time.sleep(1)


def check_files():
    path = '/home/mint/mustafa2/youtubeapi/videolar'
    uploaded_path='/home/mint/mustafa2/youtubeapi/yüklenen_videolar'
    for filename in os.listdir(path):
        id = filename.split('.')[0]
        print(id)
        

def move_files():
    os.rename(os.path.join(check_files.path, check_files.filename), os.path.join(check_files.uploaded_path, check_files.filename))
    print("Dosya taşındı")