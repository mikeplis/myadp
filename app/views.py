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

# TODO: move these model classes to their own file
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

# TODO: move these model classes to their own file
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

  def __str__(self):
    return 'LiveMFLSource(year={}, league_id={})'.format(self.year, self.league_id)

  def get_picks(self):
    page = urllib2.urlopen(self.url).read()
    return MFLSource.get_picks(self, page)


def create_context(sources):
  api_data = {
    'years': [x[0] for x in sources],
    'league_ids': [x[1] for x in sources]
  }
  context = {
    'num_mocks': len(sources),
    'api_data': json.dumps(api_data)
  }
  return context


def index(request):
  return render(request, 'index.html')

def dynastyffonly(request):
  sources = [
    (2014, 73465),
    (2014, 79019)
  ]
  context = create_context(sources)
  return render(request, 'table.html', context)

def dynastyff2qb(request):
  sources = [
    (2015, 70578),
    (2015, 62878),
    (2015, 79056),
    (2015, 53854),
    (2015, 66771),
    (2015, 71287)
  ]
  context = create_context(sources)
  return render(request, 'table.html', context)

def nasty26(request):
  sources = [
    (2015, 71481),
    (2015, 72926),
    (2015, 78189),
    (2015, 75299),
    (2015, 76129),
    (2015, 69009),
    (2015, 60806)
  ]
  context = create_context(sources)
  return render(request, 'table.html', context)

def dynastyffmixed(request):
  messages.add_message(request, messages.INFO, "The dynastyffmixed page has been removed")
  return redirect('index')

def generate_report(request):
  years = map(int, request.GET.getlist('years[]'))
  league_ids = map(int, request.GET.getlist('league_ids[]'))
  sources = [LiveMFLSource(year, league_id) for (year, league_id) in zip(years, league_ids)]
  data = Report(sources).generate()
  return HttpResponse(json.dumps({'data': data}), content_type="application/json")

def test(request):
  return redirect('index')
