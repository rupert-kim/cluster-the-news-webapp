import datetime
import random

from clusterTheArticle.articleCluster import ArticleCluster
from django.http import JsonResponse
from django.shortcuts import render


from webAppForClusterTheNews.mongoHandler import MongoHandler
from webAppForClusterTheNews.schedule.newsAppender import newsMaker, appender


def run(request):
    mongo = MongoHandler()
    newsList = mongo.getNewsOfDay(datetime.datetime(2016,1,1))
    newsCluster = ArticleCluster()
    articleList = []
    for newsArticle in newsList:
        articleList.append(newsArticle.article)
        del newsArticle.article
        del newsArticle.id
    newsClusterList = newsCluster.runOfKMeans(articleList,extraList=newsList)
    for cluster in newsClusterList:
        cluster['date'] = datetime.datetime(2016,1,1)

    mongo.saveClusterList(newsClusterList)
    return JsonResponse({'response':200})

def articleAppender(request):

    # appender()
    response = render(request, 'index.html', {'request': request})


    return response


def getArticleGraph(request):
    def transElement(newsNodeDict,index,**kwargs):
        newsNodeDict['index'] = index
        newsNodeDict['id'] = index
        newsNodeDict.update(newsNodeDict['extra'])
        del newsNodeDict['extra']
        newsNodeDict['level'] = random.randrange(1,3)
        newsNodeDict['score'] = 7
        del newsNodeDict['tfMap']

        newsNodeDict['links'] = []
        if kwargs.get('links') is not None:
            newsNodeDict['links'] = kwargs.get('links')
        return newsNodeDict

    mongo = MongoHandler()
    list = []
    for element in mongo.getClustersOfDay(datetime.datetime(request.GET.get('y',2016),request.GET.get('m',1),request.GET.get('d',1))):
        del element['centroid']['article']
        element['date'] = (element['date'].strftime('%Y%m%d'))
        list.append(element)


    nodes = []
    links = []

    for cluster in list:
        cluster['elementList'] = sorted(cluster['elementList'], key=lambda element: element['simValue'])

    for cluster in list:
        centroid = cluster['centroid']
        centroid['article'] = cluster['elementList'][-1]['article']
        centroidIdx = nodes.__len__()
        centroid['id'] = centroidIdx
        cent = transElement(centroid,nodes.__len__())
        cent['level'] = 1
        cent['score'] = 10
        nodes.append(cent)
        for element in cluster['elementList']:
            eIndex = nodes.__len__()
            nodes[centroidIdx]['links'].append(eIndex)
            nodes.append(transElement(element,eIndex,links=[centroidIdx]))

            link = {}
            link['source'] = eIndex
            link['target'] = centroidIdx
            link['weight'] = pow(element['simValue'],2)*10
            links.append(link)

    # for cluster in list:
    #     centroid = cluster['centroid']
    #     for anotherCluster in list:
    #         if cluster == anotherCluster:
    #             continue
    #         sim = newsCluster.getSimilarity(centroid,anotherCluster['centroid'])
    #         link = {}
    #         link['source'] = centroid['id']
    #         link['target'] = anotherCluster['centroid']['id']
    #         link['weight'] = pow(sim, 2) * 10
    #         links.append(link)
    responseData = {'nodes':nodes,'links':links}

    return JsonResponse(responseData,safe=False)