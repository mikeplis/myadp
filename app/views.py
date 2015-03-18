from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.defaulttags import register
from django.templatetags.static import static
from fuzzywuzzy import fuzz, process
import csv
import json
import logging
import numpy
import os.path
import urllib
import urllib2
import warnings

logger = logging.getLogger('testlogger')
#logger.info('This is a simple log message')

# TODO: pickle this so I don't have to retrieve it every time
# def get_mfl_players():
#   params = {'TYPE': 'players', 'JSON': 1}
#   encoded_params = urllib.urlencode(params)
#   mfl_url = 'http://football.myfantasyleague.com'
#   year = 2015
#   mfl_export_url = '{}/{}/export'.format(mfl_url, year)
#   opener = urllib2.build_opener()
#   url = '{}?{}'.format(mfl_export_url, encoded_params)
#   resp = opener.open(url).read()
#   players = json.loads(resp)['players']['player']
#   d = {}
#   for player in players:
#     d[player['name']] = player
#   return d

class Report:

  def __init__(self, sources):
    self.players = {} # map of player name (string) to Player2(?)
    self.sources = sources
    self.source_lengths = [241] * len(sources) # 241 is default value

  #def process_sources(): ???
  def process_source(self, source):
    """ For a single source, iterate through the picks and update players. 

    Need to also figure out length of draft and update source_lengths when finished """
    pass

  def generate():
    """ Iterate through players and create a row for each of them """
    # TODO: figure out the minimal amount of information needed to create a row for a player
    #       add create a class containing that information. players will hold several instances
    #       of this class
    pass

  def add_pick(self, player, pick_num, source_num):
    """ Add a draft pick to a report

    If player exists in players:
      update player with new pick_num and source_num
    Else:
      add new entry to players with pick_num and source_num
    """
    pass


class Player2:

  def __init__(self, name, team, position):
    self.name = name
    self.team = team
    self.position = position
    self.draft_positions = {} # map from source_num (int) to draft_position (int)



class Player:
  #mfl_players = get_mfl_players()
  #mfl_players_keys = mfl_players.keys()

  def __init__(self, name, team=None, position=None, draft_positions=None):
    self.name = name
    if team is None:
      # get position from mfl_players
      self.team = ""
    else:
      self.team = team
    if position is None:
      # get position from mfl_players
      self.position = "" 
    else:
      self.position = position
    if draft_positions is None:
      self.draft_positions = []
    else:
      self.draft_positions = draft_positions

  def get_adp(self):
    return numpy.mean(filter(None, self.draft_positions))

  def get_std(self):
    return numpy.std(filter(None, self.draft_positions))

  def to_row(self):
    # placeholder value for 'Rank' in first column, which gets updated on FE
    return [0, self.name, self.position, self.team, self.get_adp(), self.get_std()] + self.draft_positions

class DataSource:
  pass

class MFLSource(DataSource):

  def __init__(self, year, league_id):
    self.year = year
    self.league_id = league_id

  def get_data(self, source):
    data = {}
    soup = BeautifulSoup(source)
    rows = soup.find('table', {'class': 'report'}).find_all('tr')[1:]
    for j, row in enumerate(rows):
      playerNode = row.find('td', {'class': 'player'})
      if playerNode is not None:
        try:
          player = playerNode.find('a').text.rsplit(' ', 2)
          d = {}
          player_name = player[0]
          d['position'] = player[2]
          d['team'] = player[1]
          # TODO: do I even need to parse out the draft_position? Can I just keep a counter of the players I view?
          d['draft_position'] = int(row.find_all('td', {'class': 'rank'})[1].text.replace('.', ''))
          data[player_name] = d
        except:
          # TODO: deal with this when calculating length of draft
          pass
    return data

class LiveMFLSource(MFLSource):
  kind = 'live_mfl'

  def __init__(self, year, league_id):
    MFLSource.__init__(self, year, league_id)
    self.url = 'http://football.myfantasyleague.com/{}/options?L={}&O=17'.format(year, league_id)

  def get_data(self):
    page = urllib2.urlopen(self.url).read()
    return MFLSource.get_data(self, page)

class DownloadedMFLSource(MFLSource):
  kind = 'dl_mfl'

  def __init__(self, year, league_id):
    MFLSource.__init__(self, year, league_id)
    # TODO: use correct file path
    self.filename = '{}_{}.html'.format(year, league_id)

  # TODO: download page and save to file
  def download_page():
    pass

  def get_data(self):
    if (not os.path.isfile(self.filename)):
      download_page()
    page = open(self.filename).read()
    return MFLSource.get_data(self, page)

class CSVMultiSource(DataSource):
  """ CSV file that contains results from several drafts

  Each row in the file should contain a player name and his draft positions
  """
  kind = 'multi_csv'

  def __init__(self, filename):
    self.filename = filename

  def get_data(self):
    with open(os.path.join('dynasty-mocks', 'static', 'data', self.filename), 'rU') as f:
      reader = csv.reader(f)
      rows = []
      for row in reader:
        draft_positions = []
        for i, draft_position in enumerate(row[1:], start=1):
          try:
            draft_positions.append(int(draft_position))
          except:
            draft_positions.append(None)
        player = Player(name=row[0], draft_positions=draft_positions)
        rows.append(player.to_row())
    return rows

class CSVSource(DataSource):
  kind = 'csv'

  def __init__(self, filename):
    self.filename = filename

  def get_data(self):
    pass

@register.filter
def get_item(dictionary, key):
  return dictionary[key]

@register.filter
def get_range(value):
  return range(value)

def combine_sources(sources):
  data = {}
  for i, source in enumerate(sources):
    for player, player_data in source.get_data().iteritems():
      if (player in data):
        data[player]['draft_positions'].append(player_data['draft_position'])
      else:
        data[player] = {}
        data[player]['draft_positions'] = [None] * i + [player_data['draft_position']]
        data[player]['team'] = player_data['team']
        data[player]['position'] = player_data['position']
    # TODO: fix this, it's inefficient
    for player, player_data in data.iteritems():
      if (len(player_data['draft_positions']) < i + 1):
        data[player]['draft_positions'].append(None)
  return data

def calculate_stats(data):
  for player, player_data in data.iteritems():
    player_data['adp'] = numpy.mean(filter(None, player_data['draft_positions']))
    player_data['std'] = numpy.std(filter(None, player_data['draft_positions']))
  return data

# TODO: probably could combine calculate_stats and convert_to_table to avoid extra passes
def convert_to_table(data):
  rows = []
  for player, player_data in data.iteritems():
    row = []
    row.append(0) # placeholder value for Rank; gets replaced on FE
    row.append(player)
    row.append(player_data['position'])
    row.append(player_data['team'])
    row.append(player_data['adp'])
    row.append(player_data['std'])
    for draft_position in player_data['draft_positions']:
      row.append(draft_position)
    rows.append(row)
  return rows

dynastyff_sources = [
  LiveMFLSource(2014, 73465),
  LiveMFLSource(2014, 79019)
]

dynastyff_2qb_sources = [
  LiveMFLSource(2015, 70578),
  LiveMFLSource(2015, 65917),
  LiveMFLSource(2015, 62878),
  LiveMFLSource(2015, 79056),
  LiveMFLSource(2015, 53854),
  LiveMFLSource(2015, 66771),
  LiveMFLSource(2015, 71287)
]

dlf_sources = [
  LiveMFLSource(2015, 46044),
  LiveMFLSource(2015, 26815),
  LiveMFLSource(2015, 38385),
  LiveMFLSource(2015, 59370),
  LiveMFLSource(2015, 49255),
  LiveMFLSource(2015, 45505)
]

nasty26_sources = [
  LiveMFLSource(2015, 71481),
  LiveMFLSource(2015, 72926),
  LiveMFLSource(2015, 78189),
  LiveMFLSource(2015, 75299),
  LiveMFLSource(2015, 76129)
]

dynastyff_rookie_source = CSVMultiSource('dynasty_ff_rookie.csv')

def index(request):
  return render(request, 'index.html')

def dynastyffonly(request):
  context = {
    'num_mocks': len(dynastyff_sources),
    'api_url': 'api/dynastyffonly'
  }
  return render(request, 'table.html', context)

def dynastyffonly_api(request):
  x = convert_to_table(calculate_stats(combine_sources(dynastyff_sources)))
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def dynastyff2qb(request):
  context = {
    'num_mocks': len(dynastyff_2qb_sources),
    'api_url': 'api/dynastyff2qb'
  }
  return render(request, 'table.html', context)

def dynastyff2qb_api(request):
  x = convert_to_table(calculate_stats(combine_sources(dynastyff_2qb_sources)))
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def dlf(request):
  context = {
    'num_mocks': len(dlf_sources),
    'api_url': 'api/dlf'
  }
  return render(request, 'table.html', context)

def dlf_api(request):
  x = convert_to_table(calculate_stats(combine_sources(dlf_sources)))
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def nasty26(request):
  context = {
    'num_mocks': len(nasty26_sources),
    'api_url': 'api/nasty26'
  }
  return render(request, 'table.html', context)

def nasty26_api(request):
  x = convert_to_table(calculate_stats(combine_sources(nasty26_sources)))
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
  x = CSVMultiSource('dynasty_ff_rookie.csv').get_data()
  return HttpResponse(json.dumps({'data': x}), content_type="application/json")

def test2(request):
  return render(request, 'test.html')

