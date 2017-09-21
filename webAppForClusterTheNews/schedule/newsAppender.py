from datetime import datetime, timezone, timedelta

from webAppForClusterTheNews.crawl.daumNewsParser import DaumNewsParse
from webAppForClusterTheNews.models import NewsArticle
from webAppForClusterTheNews.mongoHandler import MongoHandler


def appender():
    print('appender start!')
    mongo = MongoHandler()
    parser = DaumNewsParse()
    newsList = mongo.getNoArticleNewsList()
    print(datetime.now())
    for news in newsList:
        article = parser.parseArticle(url=news.link)
        news.article = article
    mongo.appendNewsArticle(newsList)
    print('appender end!')

def newsMaker():
    parser = DaumNewsParse()
    mongo = MongoHandler()
    article = mongo.getLatestArticleWrote()
    article = NewsArticle(**article)
    if article.wrote_date == '':
        article.wrote_date = datetime(2015,12,31)
    latestDate = article.wrote_date + timedelta(days=1)
    nowPresent = datetime.now(timezone(timedelta(hours=9)))
    if latestDate.strftime('%Y%m%d') > nowPresent.strftime('%Y%m%d'):
        return
    urlList = parser.parseUrlList(paramDate=latestDate.strftime('%Y%m%d'))
    newsLinkList = []
    for urlObject in urlList:
        urlObject['link'] = urlObject['href']
        newsLinkList.append(vars(NewsArticle(**urlObject)))

    mongo.saveNewsList(newsLinkList)