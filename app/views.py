from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import urllib2
import numpy
from django.template.defaulttags import register

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
    values = []
    x = {}
    for i in range(0, len(urls)):
      dp = dps.get(i)
      if dp is not None:
        x[i] = dp
        values.append(dp)
      elif isDraftDone[i] and useDefault[i]:
        x[i] = defaultPickNum
        values.append(defaultPickNum)
      else:
        x[i] = None
    adp = sum(values) / float(len(values))
    std = numpy.std(values)
    p = player.rsplit(' ', 2)
    x['player'] = p[0]
    x['position'] = p[2]
    x['team'] = p[1]
    x['adp'] = adp
    x['std'] = std
    newdata.append(x)

  context = {
    'picks': newdata,
    'mockNums': range(0, len(urls)),
    'urls': urls
  }
  return context

dynastyff_urls = [
  'http://football2.myfantasyleague.com/2014/options?L=73465&O=17',
  'http://football2.myfantasyleague.com/2014/options?L=79019&O=17'
]

dynastyff_2qb_urls = [
  'http://football2.myfantasyleague.com/2015/options?L=70578&O=17',
  'http://football2.myfantasyleague.com/2015/options?L=65917&O=17',
  'http://football2.myfantasyleague.com/2015/options?L=62878&O=17',
  'http://football2.myfantasyleague.com/2015/options?L=79056&O=17',
  'http://football2.myfantasyleague.com/2015/options?L=53854&O=17'
]

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
  return render(request, 'index.html')

def dynastyffonly(request):
  context = get_data(dynastyff_urls)
  context['title'] = '/r/DynastyFF Mock Draft Results'
  return render(request, 'table.html', context)

def dynastyff2qb(request):
  context = get_data(dynastyff_2qb_urls)
  context['title'] = '/r/DynastyFF 2 QB Mock Draft Results'
  return render(request, 'table.html', context)

def dlf(request):
  context = get_data(dlf_urls)
  context['title'] = ""
  return render(request, 'table.html', context)

