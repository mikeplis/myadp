from bs4 import BeautifulSoup
import urllib2
import numpy

def main():
  urls = [
    'http://football21.myfantasyleague.com/2015/options?L=46044&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=26815&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=38385&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=59370&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=49255&O=17',
    'http://football21.myfantasyleague.com/2015/options?L=45505&O=17'
  ]
  defaultPickNum = 241
  currentPicks = [defaultPickNum] * len(urls)
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
        currentPicks[i] = j
        break

  newdata = []
  for player, dps in data.iteritems():
    adp = sum(dps.values()) / float(len(dps))
    std = numpy.std(dps.values())
    x = {'player': player, 'adp': adp, 'std': std}
    for i in range(0, len(urls)):
      x[i] = dps.get(i, defaultPickNum)
    newdata.append(x)
  print(currentPicks)

if __name__ == '__main__':
  main()
