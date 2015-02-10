from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import urllib2
import numpy
from django.template.defaulttags import register

from .models import Greeting

@register.filter
def get_item(dictionary, key):
    return dictionary[key]

def get_data(urls, useDefault=None):
  if useDefault is None:
    useDefault = [True] * len(urls)
  defaultPickNum = 241
  isDraftDone = [True] * len(urls)
  data = {}

  for i, url in enumerate(urls):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    rows = soup.find('table', {'class': 'report'}).find_all('tr')[1:]
    for j, row in enumerate(rows):
      playerNode = row.find('td', {'class': 'player'})
      if playerNode is not None:
        player = playerNode.find('a').text
        dp = int(row.find_all('td', {'class': 'rank'})[1].text.replace('.', ''))
        if player in data:
          data[player][i] = dp
        else:
          data[player] = {i: dp}
      else:
        isDraftDone[i] = False
        break

  newdata = []
  for player, dps in data.iteritems():
    adp = sum(dps.values()) / float(len(dps))
    std = numpy.std(dps.values())
    x = {'player': player, 'adp': adp, 'std': std}
    for i in range(0, len(urls)):
      dp = dps.get(i)
      if dp is not None:
        x[i] = dp
      elif isDraftDone[i] and useDefault[i]:
        x[i] = defaultPickNum
      else:
        x[i] = None
    newdata.append(x)

  context = {
    'picks': newdata,
    'mockNums': range(0, len(urls)),
    'urls': urls
  }
  return context

dlf_urls = [
    'http://football21.myfantasyleague.com/2015/options?L=46044&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=26815&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=38385&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=59370&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=49255&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=45505&O=17'
  ]
# Create your views here.
def index(request):
  context = get_data(dlf_urls)
  return render(request, 'index.html', context)

def dynastyff(request):
  dynastyff_urls = [
    'http://football2.myfantasyleague.com/2014/options?L=73465&O=17',
    'http://football2.myfantasyleague.com/2014/options?L=79019&O=17'
  ]
  urls = dynastyff_urls + dlf_urls
  context = get_data(urls, [False]*len(dynastyff_urls) + [True]*len(dlf_urls))
  return render(request, 'index.html', context)

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

