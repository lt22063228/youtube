'''
Created on Nov 2, 2015

@author: lin
'''

import json
from apiclient.discovery import build
from apiclient.errors import HttpError
# from oauth2client import argparser

DEVELOPER_KEY = 'AIzaSyBv2jojAGWOiyZINpty3X_hdAwL2b84zE0'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VIDEO_ID = ['eBTADWQKB7w',
'xhS_CjECO90',
'lqlrru1V69E',
'VTwbKryrhks',
'0skAEQb07jw']

def get_comment_threads(youtube, video_id):
    results = youtube.commentThreads().list(
                                        part = "id",
                                        videoId = video_id,
                                        textFormat = "plainText" ,
                                        maxResults = 100,
                                            ).execute()
    
    data = json.loads(json.dumps(results, indent = 4))
    _page_token = data['nextPageToken']
    count = 100;
    while _page_token != None or len(_page_token) == 0:
        results = youtube.commentThreads().list(
                                        part = "id",
                                        videoId = video_id,
                                        textFormat = "plainText" ,
                                        maxResults = 100,
                                        pageToken = _page_token,
                                            ).execute()
        data = json.loads(json.dumps(results, indent = 4))
        count += data['pageInfo']['totalResults']
        print count
        if 'nextPageToken' not in data:
            break
        _page_token = data['nextPageToken']

    
def build_youtube():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey = DEVELOPER_KEY)
    return youtube

def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey = DEVELOPER_KEY)
    
    # call the search.list method to retrieve results matching the specified
    # query term
    video_response = youtube.videos().list(
        part = 'id,snippet, statistics',
        chart = 'mostPopular',
        maxResults = 5,
                                            ).execute()
                                            
    videos = []
    
    print json.dumps(video_response, indent=4)

    
if __name__ == "__main__":
    youtube_search()
#     youtube = build_youtube()
#     for i in range(5):
#         get_comment_threads(youtube, VIDEO_ID[i])
#         print "............................................................."