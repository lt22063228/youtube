'''
Created on Nov 2, 2015

@author: lin
'''

from sqlalchemy.schema import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

Base = declarative_base()


class Video(Base):
    __tablename__ = "cm_video"
    id = Column(Integer, Sequence("video_id_seq"), primary_key = True)
    videoId = Column(String(100))
    title = Column(String(100))
    category = Column(String(100))
    view_count = Column(Integer)
    comment_count = Column(Integer)
    published = Column(DateTime)
    
    def __repr__(self):
        return "<video %s %s>" % (self.videoId, self.title)
    
class CVideo(Base):
    __tablename__ = "c_video"
    videoId = Column(String(100), primary_key = True)
    
    def __repr__(self):
        return "<video %s %s>" % (self.videoId, self.title)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, Sequence("user_id_seq"), primary_key = True)
    userId = Column(String(100))
    name = Column(String(100))
    
#     def __init__(self, id = None, userId = None, name = None):
#         self.userId = userId
#         self.name = name
    
    
    def __repr__(self):
        return "<user %s %s>" % (self.userId, self.name)

class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, Sequence("comment_id_seq"), primary_key = True)
    commentId = Column(String(100))
    userId = Column(String(100))
    videoId = Column(String(100))
    content = Column(String(200))
    published = Column(DateTime)
    

    def __repr__(self):
        return "<comment %s %s>" % (self.id, self.content)
    
class Train(Base):
    __tablename__ = 'train'
    id = Column(Integer, primary_key = True)
    userId = Column(String(60))
    videoId = Column(String(60))
    published = Column(DateTime)
    

class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key = True)
    userId = Column(String(60))
    videoId = Column(String(60))
    published = Column(DateTime)



if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine("mysql://root:123456@localhost:3306/youtube?charset=utf8", echo=False)
    Base.metadata.create_all(engine)