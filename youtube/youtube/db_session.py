'''
Created on Nov 2, 2015

@author: lin
'''

from orm import *
from exception import *
from sqlalchemy.sql.expression import *
from exception import *
import json

class DbSession():
    def __init__(self):
        self.session = self.getSession()
    def close(self):
        self.session.close()
    
    def getSession(self):
        
        from sqlalchemy import create_engine
        
        engine = create_engine("mysql://root:123456@localhost:3306/youtube?charset=utf8", encoding="utf8", echo=False)
        
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
        
        
    def insert_video(self, video):
        
        v = Video(
                     videoId = video["videoId"], title = video['title'],
                     category = video['category'], view_count = video['view_count'],
                     comment_count = video['comment_count'], published = video['published'],
                     userId = video['userId']
                      )
        
        session.add(v)
        session.commit()
        
    def insert_videos(self, videos):
        
        videoList = []
        
        for video in videos:
            
            v = Video(
                     videoId = video["videoId"], title = video['title'],
                     category = video['category'], view_count = video['view_count'],
                     comment_count = video['comment_count'], published = video['published']
                      )
            self.session.add(v)
        
        self.session.commit()
        
    def get_all_videos(self):
        """
            return all videoId in the table 'video'
        """
        
        idList = [u[0] for u in self.session.query(Video.videoId).all()]
        return idList
    
    def get_all_cvideos(self):
        
        cidList = [u[0] for u in self.session.query(CVideo.videoId).all()]
        return cidList
    
    def insert_comments(self, comments):

        commentList = []
        for comment in comments:
            if 'snippet' not in comment:
                print 'ignore 1 comment'
                continue
            c = Comment(
                       commentId = comment['id'], userId = comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                       videoId = comment['snippet']['videoId'], content = comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                       published = comment['snippet']['topLevelComment']['snippet']['publishedAt'], 
                        )
            self.session.add(c)
            
        self.session.commit()
            
    def get_data(self, train_or_test):
        if train_or_test == "train":
            res = self.session.query(Train.userId, Train.videoId, Train.published).order_by(Train.userId,Train.published).all()
        elif train_or_test == "test":
            res = self.session.query(Test.userId, Test.videoId, Test.published).order_by(Test.userId,Test.published).all()
        else:
            print "wrong in get_data"
        return res 
            
            
        
if __name__ == "__main__":
    
    session = DbSession()
    session.get_all_videos()
        












































































