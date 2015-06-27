import itertools
import logging
import os
import redis as _redis
import urllib2

# TODO: fix duplicate code 

logger = logging.getLogger('testlogger')
redis = _redis.StrictRedis.from_url(os.environ['REDIS_URL'])
redis_timeout = int(os.environ['REDIS_TIMEOUT']) * 60 # minutes * seconds/minute

logger.info('caching scottfish leagues')

def download_draft(year, league_id, division_id):
  url = 'http://football.myfantasyleague.com/{}/options?L={}&O=17&DISPLAY=DIVISION{}'.format(year, league_id, division_id)
  page = urllib2.urlopen(url).read()

  key = '_'.join([str(year), str(league_id), str(division_id)])

  logger.info('setting cache for {}'.format(key))

  # using setex so app doesn't get stuck using stale results
  redis.setex(key, redis_timeout, page)

years = [2015]
league_ids = map(int, os.environ['CACHE_WHITELIST'].split(','))
division_ids = ['00', '01', '02', '03', '04']

for (year, league_id, division_id) in itertools.product(years, league_ids, division_ids):
  download_draft(year, league_id, division_id) 

