from Display import oled
from common_tmp import *

try:
  import usocket as socket
except:
  import socket

from commonSetter import setCommon
import network
import json



import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'LOCAT-AP'
password = '12345678'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, authmode=network.AUTH_WPA_WPA2_PSK, password=password)

while ap.active() == False:
  pass

print('Connection successful')

def web_page(isSender):

  WIFI = {}
  KOREK = {}

  try:
    f = open('common.py', "r")
    content = f.read()
    for line in content.split('\n'):
      if len(line.split('=')) > 1:
        key = line.split('=')[0]
        val = line.split('=')[1]
        if key == 'WIFI':
          WIFI = json.loads(val)
        if key == 'KOREK':
          KOREK = json.loads(val)
    f.close
  except:
    pass


  html_receiver = """<p><span>Wifi Essid:</span>
  <input pattern=".{3,}" title="3 characters minimum" value="%s" name="essid" required/>
  <p/>
  <p>
  <span>Wifi Password:</span>
  <input pattern=".{3,}" title="8 characters minimum" value="%s" name="wifi_pass" required/>
  <p/>
  <p/>
  <p>
  <span>Korek User:</span>
  <input pattern=".{3,}" title="3 characters minimum" value="%s" name="korek_username" required/>
  <p/>
  <p>
  <span>Korek Password:</span>
  <input pattern=".{4,}" title="4 characters minimum" value="%s" name="korek_password" required/>
  <p/>""" % (WIFI.get("essid", ""), WIFI.get("pass",""), KOREK.get("korek_username",""), KOREK.get("korek_password",""),)


  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
  <body><h1>Welcome to Korek Tracking!</h1>
  <form action="save_locat" method="post">
  <p>
  <span>Cat Name:</span>
  <input pattern=".{2,}" title="2 characters minimum" value="%s" name="title" required/>
  <p/>
  <p/>""" % (KOREK.get("title",""),)

  html_sender = """<p>
  <span>Frequency:</span>
   <select name="frequency" required>
    <option value="0">no sleep</option>
    <option value="10">each 10 seconds</option>
    <option value="30">each 30 seconds</option>
    <option value="60">each minute</option>
    <option value="3600">hourly</option>
    <option value="86400">daily</option>
  </select> 
  <p/>"""

  html += html_receiver if not isSender else html_sender
  
  html += """<input type="submit" value="Send" />
  </form>
  </body></html>"""

  return html

def confirm():
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
            <body><h1>Korek Tracking Configured!</h1></body></html>"""
  return html

def startWebServer(isSender=False):

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(('', 80))
  s.listen(5)
  #s.settimeout(timeout)

  display = oled.startDisplay(SCL,SDA,RST_SCREEN)
  oled.resetScreen(display)
  display.text("starting webserver...", 0, 0)
  display.text("connect to:", 0, 10)
  display.text(str(ap.ifconfig()[0]), 0, 20)
  display.show()

  while True:

    conn, addr = s.accept()

    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    str_req =  str(request)[1:-1]
    print('Content = %s' % str(request))
    res = str_req.split('\\n')[-1]

    try:
      dict_res = dict(i.split('=') for i in res.split('&'))
      print(setCommon(isSender, dict_res))

      response = confirm()
      conn.send(response)
      conn.close()

      oled.resetScreen(display)
      display.text("starting sender..." if isSender else "start receiver..." , 0, 0)
      display.show()

      return False
    except Exception as e: 
      print(e)

    response = web_page(isSender)
    conn.send(response)
    conn.close()
