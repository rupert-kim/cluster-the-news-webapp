import json

import datetime
import pymongo
from pymongo import MongoClient

from webAppForClusterTheNews.models import NewsArticle


class MongoHandler:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.database = client['cluster_the_news']

    def saveNews(self,newsArticle):
        newsCol = self.database['news']
        return newsCol.insert(vars(newsArticle))

    def saveNewsList(self,newsArticleList):
        newsCol = self.database['news']
        return newsCol.insert_many(newsArticleList)

    def getNoArticleNewsList(self):
        newsCol = self.database['news']
        newsList = []
        for news in newsCol.find({'article':''}).sort('created_date').limit(30):
            newsList.append(NewsArticle(**news))

        return newsList

    def appendNewsArticle(self, newsList):
        newsCol = self.database['news']
        for news in newsList:
            res = newsCol.update({'_id':news.id},{'$set':{'article':news.article}})

    def getLatestArticleWrote(self):
        newsCol = self.database['news']
        results = newsCol.find().sort([('wrote_date',pymongo.DESCENDING)]).limit(1)
        if results.count() == 0:
            return {}
        else:
            return results[0]
    def getNewsOfDay(self,dateValue):
        newsCol = self.database['news']
        newsList = []
        for news in newsCol.find({'wrote_date':{'$gte':dateValue,'$lt':dateValue+datetime.timedelta(days=1)}}).limit(500):
            newsList.append(NewsArticle(**news))
        return newsList

    def saveClusterList(self, newsClusterList):
        clusterCol = self.database['news_cluster']

        for cluster in newsClusterList:
            cluster['centroid'] = vars(cluster['centroid'])
            for idx, element in enumerate(cluster['elementList']):
                element.extra = vars(element.extra)
                cluster['elementList'][idx] = vars(element)

        clusterCol.insert_many(newsClusterList)

    def getClustersOfDay(self, date):
        newsCol = self.database['news_cluster']
        return newsCol.find({'date':date},{'_id': False,'id':False})


