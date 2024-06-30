import os
import json    
import requests
     
class Utils:
    def __init__(self):
        self.read_settings()
        self.get_files()
    
    def read_settings(self):
        with open("settings.json") as f:        
            self.settings = json.load(f)
            f.close()
            self.path = self.settings['path']
            self.archive_path = self.settings['archive_path']
        return self.settings
        
    def get_files(self):
        self.read_settings()
        self.files = []
        for filename in os.listdir(self.path):
            self.files.append({
                'name': filename,
                'id': filename.split('.')[0]
            })
        print(self.files)
        return self.files
    
    def move_file(self,filename):    
        os.rename(os.path.join(self.path, filename), os.path.join(self.archive_path, filename))
        print(f"{filename} dosyasi arsiv klasorune taşındı")
    
    def get_body_from_api(self,file):        
        url = f"https://ksv.mintyazilim.com/api/course/program/?id={file['id']}"   
        print(url) 
        body = None    
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for key, value in data.items():
                print(f"{key}: {value}")
            body = {
                "snippet": {
                    "title": data["title"],
                    "description": data["description"], 
                    "keywords" : data["tag"],
                    "file": os.path.join(self.path, file['name']), 
                    "category": data["categoryId"],
                    
                },
                "status": {
                    "privacyStatus": "unlisted",
                }
            }
            
        else:        
            print(f"Error: {response.status_code}")
            print("Yükleme işlemi başarısız oldu")   
        
        return body
    

  
utils=Utils()