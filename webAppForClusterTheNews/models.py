from datetime import datetime,timezone,timedelta


class NewsArticle():
    def __init__(self, **kwargs):
        tz = timezone(timedelta(hours=9))
        self.id = kwargs.get('_id','')
        self.article = kwargs.get('article','')
        self.title = kwargs.get('title','')
        self.thumb = kwargs.get('thumb','')
        self.link = kwargs.get('link','')
        self.created_date = kwargs.get('create_date',datetime.now(tz))
        self.wrote_date = kwargs.get('wrote_date','')


