'''
Created on Nov 2, 2015

@author: lin
'''
import os
from db_session import *
from api_session import *
class Youtube():
    def __init__(self):
        self.dbSession = DbSession()
        self.apiSession = ApiSession(self.dbSession)

    def close(self):
        self.dbSession.close()

    def get_video_from_file(self, dirname):
        path = "../rc_todo"
        file_path_list = []
        for dirpath, dirnames, _ in os.walk(path):
            for dirname in dirnames:
                inner_path = dirpath + '/' + dirname
                for dpath, _, filenames in os.walk(inner_path):
                    for filename in filenames:
                        if filename == 'log.txt': continue
                        filepath = dpath + '/' + filename
                        file_path_list.append(filepath)
            
        for filepath in file_path_list:
            with open(filepath) as file:
                videos = []
                print filepath
                for line in file:
                    fields = line.split('\t')
                    if len(fields) != 29: continue
                    videoId = fields[0]
    #                title = fileds[]
                    category = fields[3]
                    view_count = fields[5]
                    comment_count = fields[8]
    
                    v = {}
                    v['videoId'] = videoId
                    v['category'] = category
                    v['view_count'] = view_count
                    v['comment_count'] = comment_count
                    v['title'] = None
                    v['published'] = None
                    videos.append(v)
        
                self.dbSession.insert_videos(videos)
    
    def get_comments_from_videos(self):
        videoIdList = self.dbSession.get_all_videos()
        cvideoIdList = self.dbSession.get_all_cvideos()
        print "cvideoIdList len:", len(cvideoIdList)
        for id in videoIdList:
            if id not in cvideoIdList:
                self.apiSession.get_comments_from_video(id)

        

if __name__ == "__main__":
    youtube = Youtube()
    youtube.get_comments_from_videos()
               
               
    