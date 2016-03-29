'''
Created on Nov 3, 2015

@author: lin
'''
import json
from apiclient.discovery import build
from apiclient.errors import HttpError
from exception import *

DEVELOPER_KEY = 'AIzaSyBv2jojAGWOiyZINpty3X_hdAwL2b84zE0'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
class ApiSession():

    
    def __init__(self, dbSession = None):
        
        self.apiSession = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                             developerKey = DEVELOPER_KEY)
        self.dbSession = dbSession
    
    def get_comments_from_video(self, video_id):
        
        try:
            results = self.apiSession.commentThreads().list(
                                        part = "id,snippet",
                                        videoId = video_id,
                                        textFormat = "plainText" ,
                                        maxResults = 100,
                                            ).execute()
        except HttpError as detail:
            # some videos no longer exist
            print "video not exist :%s" % video_id
            return
                
            except_stop()
                
        data = json.loads(json.dumps(results, indent = 4))
        if 'nextPageToken' not in data:
            return

        _page_token = data['nextPageToken']
        count = data['pageInfo']['totalResults'];
        commentList = []
        commentList.extend(data['items'])
        

        while True:
            results = self.apiSession.commentThreads().list(
                                            part = "id,snippet",
                                            videoId = video_id,
                                            textFormat = "plainText" ,
                                            maxResults = 100,
                                            pageToken = _page_token,
                                                ).execute()
                                                
                                                
            data = json.loads(json.dumps(results, indent = 4))
            commentList.extend(data['items'])
            try:
                count += data['pageInfo']['totalResults']
            except KeyError as detail:
                print data
                print detail
            if 'nextPageToken' not in data:
                print "insert final"
                self.dbSession.insert_comments(commentList)
                break
            if count >= 10000:
                print "insert 10000"
                self.dbSession.insert_comments(commentList)
            _page_token = data['nextPageToken'] 
            
            
if __name__ == "__main__":
    d = {u'snippet':0}
    print d['snippet']
























