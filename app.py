# Daily Deal
# Supports python v3

import requests
import json
from functools import reduce
from optimizely import optimizely
from threading import Timer
import logging
from optimizely import logger

#orig
#DATAFILE_URL = 'https://cdn.optimizely.com/onboarding/M-i3QLN-T--EuXrlmVXQXQ.json'
DATAFILE_URL =  "https://cdn.optimizely.com/datafiles/MgkBhsPjNM1knSUn4HUNkY.json"
DEBUG_TEXT_ON = '[DEBUG: Feature [36mON[0m]'
DEBUG_TEXT_OFF = '[DEBUG: Feature [33mOFF[0m]'

#userId is a reserve term don't use for attributes! 
#we have some sample apps on github more fleshed out ... another question is to look at how to bring sample apps closer into the docs
# look at the github library
# 

'''
attributes = 
[
  {us_based:True},
  {us_based:True},
  {us_based:True},
  {us_based:True},
  {us_based:True},  
  {us_based:False},
  {us_based:False},
  {us_based:False},
  {us_based:False},
  {us_based:False},
]
}
'''


def get_daily_deal(optimizely, visitor):

  #kody not sure if python would let you put json in a funct call <

  # buckets first based on deterministically hashing the userID and feature Enabled, and then it does audience on top of that
  #so if a bunch of differnte mobile, tv, and etc apps that don't talk to eac other,
  #they'll still be bucketed the same (yeah, pseudo random # geneartor)


  #you have to pass in a key-value pair for audience attr, not jus ta value
  #and I got lazy trying to figure out how to combine data structures such that each visitor has a {'us_based': object} (use json, maybe?)
  #so I just set us_based to true for everyone:
  enabled = optimizely.is_feature_enabled('purchase_option', visitor['userId'], {'us_based': True})
  print ('enabled? ' , visitor['userId'], enabled)

  if enabled:
    text = optimizely.get_feature_variable_string('purchase_option', 'message', visitor['userId'])

    if visitor.get('purchasedItem'):
      optimizely.track('purchase_item', visitor['userId'])
  else:
    text = 'feature purchase_option NOT enabled. Daily deal: A bluetooth speaker for $99!'

  return {
    'text': text,
    'is_enabled': enabled,
    'debug_text': DEBUG_TEXT_ON if enabled else DEBUG_TEXT_OFF,
  }



def main(datafile):
  optimizely_client_instance = optimizely.Optimizely(datafile=datafile, logger=logger.SimpleLogger(min_level=logging.INFO))

  visitors = [
    { 'userId': 'alice1'},
    { 'userId': 'alice2'}, 
    { 'userId': 'alice3'},
    { 'userId': 'alice4'}, 
    { 'userId': 'alice5'},
    { 'userId': 'alice6'}, 
    { 'userId': 'alice7'},
    { 'userId': 'alice8'}, 
    
  ]



  print("\n\nWelcome to Daily Deal, we have great deals for YOU!")
  print("Let's see what the visitors experience!\n")

  deals = [ get_daily_deal(optimizely_client_instance, visitor) for visitor in visitors ]
  on_variations = [ deal for deal in deals if deal['is_enabled'] ]
  if len(on_variations) > 0:
    experiences = ['Visitor #%s: %s %s' % (i, deal['debug_text'], deal['text']) for i, deal in enumerate(deals)]
  else:
    experiences = ['Visitor #%s: %s' % (i, deal['text']) for i, deal in enumerate(deals)]

  print("\n".join(experiences))
  print()

  def count_frequency(accum, value):
    text = value['text']
    accum[text] = accum[text] + 1 if text in accum.keys() else 1
    return accum

  frequency_map = reduce(count_frequency, deals, {})

  num_on_variations = len(on_variations)
  total = len(visitors)

  if len(on_variations) > 0:
    print("{0} out of {1} visitors (~{2}%) had the feature enabled\n".format(
        num_on_variations,
        total,
        round(num_on_variations / total * 100)
      )
    )

  total = len(visitors)
  for text, _ in frequency_map.items():
    perc = round(frequency_map[text] / total * 100)
    print("%s visitors (~%s%%) got the experience: '%s'" % (frequency_map[text], perc, text))


class DatafilePoller():
  def __init__(self, callback=None, **kwargs):
    self.current_datafile = '{"revision": "0"}'
    self.is_running = False
    self._timer = None
    self.callback = callback

  def request_datafile(self, timeout=None):
    datafile_response = requests.get(DATAFILE_URL, timeout=timeout)
    if not datafile_response.status_code == 200:
      return

    datafile=datafile_response.json()
    latest_datafile = json.dumps(datafile)
    if latest_datafile != self.current_datafile:
      self.current_datafile = latest_datafile
      self.callback(latest_datafile)

  def run(self):
    self.is_running = False
    self.start()
    self.request_datafile()

  def start(self, interval=1):
    if not self.is_running:
      self._timer = Timer(interval, self.run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False


def start_app():
  datafile_poller = DatafilePoller(callback=main)
  datafile_poller.start()


if __name__ == "__main__":
  start_app()