from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import urllib2

from .models import Greeting

# Create your views here.
def index(request):
  urls = [
    'http://football21.myfantasyleague.com/2015/options?L=46044&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=26815&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=38385&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=59370&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=49255&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=45505&O=17'
  ]

  data = {}

  for url in urls:
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    rows = soup.find('table', {'class': 'report'}).find_all('tr')
    for row in rows:
      try:
        player = row.find('td', {'class': 'player'}).find('a').text
        dp = int(row.find_all('td', {'class': 'rank'})[1].text.replace('.', ''))
        data.setdefault(player, []).append(dp)
      except:
        pass

  newdata = []

  for p, dps in data.iteritems():
    adp = sum(dps) / float(len(dps))
    newdata.append({'player': p, 'dps': dps, 'adp': adp})

  response = '<table><thead><tr><td>Player Name</td><td>ADP</td><td>Draft Positions</td></tr></thead><tbody>'

  for d in sorted(newdata, key=lambda x: x['adp']):
    row = '<tr><td>{}</td><td>{:.2f}</td><td>{}</td></tr>'.format(d['player'], d['adp'], d['dps'])
    response += row

  response += '</tbody></table>'

  return HttpResponse(response)


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

