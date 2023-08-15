import network
import time
import json
from common import *

def getWifiConf():
  try:
    f = open('common.py', "r")
    content = f.read()
    for line in content.split('\n'):
      if len(line.split('=')) > 1:
        key = line.split('=')[0]
        val = line.split('=')[1]
        if key == 'WIFI':
          WIFI = json.loads(val)
        if key == 'WIFI2':
          WIFI2 = json.loads(val)
    f.close
    return [WIFI, WIFI2]
  except:
    print('Cannot get wifi conf!')
    return []

def disconnect():
  try:
    station = network.WLAN(network.STA_IF)
    station.disconnect()
    station.active(False)
  except:
    pass
  return 'wifi disconnected!'

def connect_wifi():
  wifi_timeout = 30
  wifi_confs = getWifiConf()
  for conf in wifi_confs:
    disconnect()
    try:
      station = network.WLAN(network.STA_IF)
      if station.isconnected():
        return 'WiFi already connected!'
      station.active(True)
      print("Connecting to " + str(conf['essid']))
      station.connect(conf['essid'], conf['pass'])
      counter = 0
      while not station.isconnected():
        time.sleep(1)
        counter += 1
        print("Attempt:" + str(counter))
        if counter > wifi_timeout:
          print('Cannot connect to WiFi: ' + str(conf['essid']))
          break
      if station.isconnected():
        return True
    except Exception as e:
      print('Cannot connect to WiFi:', str(e))
  return False