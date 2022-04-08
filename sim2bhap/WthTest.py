import time
import struct
import math
import os
import re
import urllib.request
import json

urls = 'http://127.0.0.1:8111/state'
urli = 'http://127.0.0.1:8111/indicators'

counter = 0
while True:
  counter += 1
  startTime = time.time()
  response =  urllib.request.urlopen(urls)
  html = response.read()
  varDict = json.loads(html)
  response =  urllib.request.urlopen(urli)
  html = response.read()
  varDict.update(json.loads(html))
  print (varDict)
  elapsed = time.time() - startTime
  print (elapsed)
  if counter >= 1:
    break
