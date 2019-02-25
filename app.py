import requests
from optimizely import optimizely
from functools import reduce

DATAFILE_URL = 'https://cdn.optimizely.com/datafiles/VNYQTnLwCpMS1m1YxrQ1f5.json'


def get_daily_deal(visitor):
  datafile = requests.get(DATAFILE_URL).text
  optimizely_client = optimizely.Optimizely(datafile, skip_json_validation=True)
  enabled = optimizely_client.is_feature_enabled('sale_price', visitor['userId'])

  if enabled:
    return 'Daily Deal: a bluetooth speaker for only $29!'
  else:
    return 'Daily Deal: a bluetooth speaker for $99!'


def main():
  visitors = [
    { 'userId': 'alice',   },
    { 'userId': 'bob',     },
    { 'userId': 'charlie', },
    { 'userId': 'don',     },
    { 'userId': 'eli',     },
    { 'userId': 'fabio',   },
    { 'userId': 'gary',    },
    { 'userId': 'helen',   },
    { 'userId': 'ian',     },
    { 'userId': 'jill',    },
  ]

  print('Welcome to Daily Deal, we have great deals!')
  print('Let\'s see what the visitors experience!\n')

  deals = [ get_daily_deal(visitor) for visitor in visitors ]
  experiences = ['Visitor #%s: %s' % (i, deal) for i, deal in enumerate(deals)]

  print('\n'.join(experiences))
  print()

  def count_frequency(accum, text):
    accum[text] = accum[text] + 1 if text in accum.keys() else 1
    return accum

  frequency_map = reduce(count_frequency, deals, {})

  total = len(visitors)
  for text, _ in frequency_map.items():
    perc = round(frequency_map[text] / total * 100)
    print("%s visitors (~%s%%) got the experience: '%s'" % (frequency_map[text], perc, text))


main()
