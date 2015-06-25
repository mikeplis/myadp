import logging
import os
import redis as _redis
import urllib2

# TODO: fix duplicate code 

logger = logging.getLogger('testlogger')
print(os.environ)
# redis = _redis.utils.from_url(os.environ['REDIS_URL'])

# def download_draft(year, league_id, division_id):
#   url = 'http://football.myfantasyleague.com/{}/options?L={}&O=17&DISPLAY=DIVISION{}'.format(year, league_id, division_id)
#   page = urllib2.urlopen(url).read()

#   key = '_'.join([str(year), str(league_id), str(division_id)])

#   #redis.set(key, page)
#   logger.info(key)
#   logger.info(page)

# years = [2015]
# league_ids = [63005, 75504, 56539, 57897, 66231, 59129]
# division_ids = ['00', '01', '02', '03', '04']

# for (year, league_id, division_id) in zip(years, league_ids, division_ids):
#   download_draft(year, league_id, division_id) 

