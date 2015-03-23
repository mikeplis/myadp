from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.defaulttags import register
from django.templatetags.static import static
import logging
import csv
import json
import logging
import numpy
import os.path
import sys
import urllib
import urllib2
import warnings

logger = logging.getLogger('testlogger')

@register.filter
def get_item(dictionary, key):
  return dictionary[key]

@register.filter
def get_range(value):
  return range(value)

class Report:

  def __init__(self, sources):
    self.sources = sources

  def generate(self):
    (picks, undrafted_values) = self.aggregate_picks()
    players = {}
    for pick in picks:
      if pick.name in players:
        players[pick.name].add_pick(pick)
      else:
        player = Player(pick)
        players[pick.name] = player
    return self.create_rows(players.values(), undrafted_values)

  def aggregate_picks(self):
    picks = []
    undrafted_values = []
    for i, source in enumerate(self.sources):
      try:
        (source_picks, is_draft_finished) = source.get_picks()
      except AttributeError:
        logger.info(sys.exc_info())
        logger.info('problem processing source: {}'.format(source))
        continue
      for sp in source_picks:
        sp.source_num = i
      picks += source_picks
      if is_draft_finished:
        undrafted_values.append(len(source_picks))
      else:
        undrafted_values.append(None)
    return (picks, undrafted_values)

  def create_rows(self, players, undrafted_values):
    rows = []
    for player in players:
      draft_positions = []
      for source_num in range(len(self.sources)):
        if source_num in player.draft_positions:
          draft_positions.append(player.draft_positions[source_num])
        else:
          draft_positions.append(undrafted_values[source_num])
      adp = numpy.mean(filter(None, draft_positions))
      std = numpy.std(filter(None, draft_positions))
      row = [0, player.name, player.position, player.team, adp, std] + draft_positions
      rows.append(row)
    return rows

class Player:

  def __init__(self, pick):
    self.name = pick.name
    self.team = pick.team
    self.position = pick.position
    self.draft_positions = {pick.source_num: pick.pick_num}

  def add_pick(self, pick):
    self.draft_positions[pick.source_num] = pick.pick_num

class Pick:

  def __init__(self, name, pick_num, team="", position=""):
    self.name = name
    self.pick_num = pick_num
    self.team = team
    self.position = position

class DataSource:
  pass

class MFLSource(DataSource):

  def __init__(self, year, league_id):
    self.year = year
    self.league_id = league_id
    self.url = 'http://football.myfantasyleague.com/{}/options?L={}&O=17'.format(year, league_id)

  # TODO: why does this function need `source` passed in?
  def get_picks(self, source):
    picks = []
    soup = BeautifulSoup(source)
    rows = soup.find('table', {'class': 'report'}).find_all('tr')[1:]
    is_draft_finished = True
    for row in rows:
      player_data = row.find('td', {'class': 'player'})
      if player_data is None:
        is_draft_finished = False
        break
      player_name_node = player_data.find('a')
      if player_name_node is not None:
        player = player_name_node.text.rsplit(' ', 2)
      else:
        continue
      pick_num = len(picks) + 1
      pick = Pick(
        name=player[0],
        pick_num=pick_num,
        team=player[1],
        position=player[2])
      picks.append(pick)
    return (picks, is_draft_finished)

class LiveMFLSource(MFLSource):

  def __init__(self, year, league_id):
    MFLSource.__init__(self, year, league_id)
    #self.url = 'http://football.myfantasyleague.com/{}/options?L={}&O=17'.format(year, league_id)

  def __str__(self):
    return 'LiveMFLSource(year={}, league_id={})'.format(self.year, self.league_id)

  def get_picks(self):
    page = urllib2.urlopen(self.url).read()
    return MFLSource.get_picks(self, page)

class DownloadedMFLSource(MFLSource):
  def __init__(self, year, league_id):
    MFLSource.__init__(self, year, league_id)
    # TODO: use correct file path
    self.filename = 'mfl_year-{}_league-{}.html'.format(year, league_id)
    self.full_path = os.path.join(settings.BASE_DIR, 'static', 'data', self.filename)

  # TODO: download page and save to file
  def download_page(self):
    page = urllib2.urlopen(self.url).read()
    with open(self.full_path, 'w') as f:
      f.write(page)
    return page

  def get_picks(self):
    if not os.path.isfile(self.full_path):
      page = self.download_page()
    else:
      page = open(self.full_path).read()
    return MFLSource.get_picks(self, page)

# class CSVMultiSource(DataSource):
#   """ CSV file that contains results from several drafts

#   Each row in the file should contain a player name and his draft positions
#   """
#   kind = 'multi_csv'

#   def __init__(self, filename):
#     self.filename = filename

#   def get_data(self):
#     with open(os.path.join('dynasty-mocks', 'static', 'data', self.filename), 'rU') as f:
#       reader = csv.reader(f)
#       rows = []
#       for row in reader:
#         draft_positions = []
#         for i, draft_position in enumerate(row[1:], start=1):
#           try:
#             draft_positions.append(int(draft_position))
#           except:
#             draft_positions.append(None)
#         player = Player(name=row[0], draft_positions=draft_positions)
#         rows.append(player.to_row())
#     return rows

# class CSVSource(DataSource):
#   kind = 'csv'

#   def __init__(self, filename):
#     self.filename = filename

#   def get_data(self):
#     pass

dynastyff_report = Report([
  LiveMFLSource(2014, 73465),
  LiveMFLSource(2014, 79019)
])

dynastyff_2qb_report = Report([
  LiveMFLSource(2015, 70578),
  LiveMFLSource(2015, 62878),
  LiveMFLSource(2015, 79056),
  LiveMFLSource(2015, 53854),
  LiveMFLSource(2015, 66771),
  LiveMFLSource(2015, 71287)
])

dlf_report = Report([
  DownloadedMFLSource(2015, 46044),
  DownloadedMFLSource(2015, 26815),
  DownloadedMFLSource(2015, 38385),
  DownloadedMFLSource(2015, 59370),
  DownloadedMFLSource(2015, 49255),
  DownloadedMFLSource(2015, 45505)
])

nasty26_report = Report([
  DownloadedMFLSource(2015, 71481),
  DownloadedMFLSource(2015, 72926),
  DownloadedMFLSource(2015, 78189),
  DownloadedMFLSource(2015, 75299),
  DownloadedMFLSource(2015, 76129),
  LiveMFLSource(2015, 69009),
  LiveMFLSource(2015, 60806)
])

#dynastyff_rookie_source = CSVMultiSource('dynasty_ff_rookie.csv')

def index(request):
  return render(request, 'index.html')

def dynastyffonly(request):
  context = {
    'num_mocks': len(dynastyff_report.sources),
    'api_url': 'api/dynastyffonly'
  }
  return render(request, 'table.html', context)

def dynastyffonly_api(request):
  x = dynastyff_report.generate()
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def dynastyff2qb(request):
  context = {
    'num_mocks': len(dynastyff_2qb_report.sources),
    'api_url': 'api/dynastyff2qb'
  }
  return render(request, 'table.html', context)

def dynastyff2qb_api(request):
  x = dynastyff_2qb_report.generate()
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def dlf(request):
  context = {
    'num_mocks': len(dlf_report.sources),
    'api_url': 'api/dlf'
  }
  return render(request, 'table.html', context)

def dlf_api(request):
  x = dlf_report.generate()
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def nasty26(request):
  context = {
    'num_mocks': len(nasty26_report.sources),
    'api_url': 'api/nasty26'
  }
  return render(request, 'table.html', context)

def nasty26_api(request):
  x = nasty26_report.generate()
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def dynastyff_rookie(request):
  context = {
    'num_mocks': 6,
    'api_url': 'api/dynastyffrookie'
  }
  return render(request, 'table.html', context)

def dynastyff_rookie_api(request):
  x = dynastyff_rookie_source.get_data()
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def dynastyffmixed(request):
  messages.add_message(request, messages.INFO, "The dynastyffmixed page has been removed")
  return redirect('index')

def test(request):
  x = os.path.join(settings.BASE_DIR, 'assets', 'data', 'foobar.csv')
  if os.path.isfile(x):
    messages.add_message(request, messages.INFO, 'true')
  else:
    messages.add_message(request, messages.INFO, x)
  return render(request, 'index.html')

def test2(request):
  context = {
    'num_mocks': len(dynastyff_2qb_report),
    'api_url': 'test'
  }
  return render(request, 'table.html', context)

