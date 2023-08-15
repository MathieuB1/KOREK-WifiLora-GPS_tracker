from ConfSetter.LoraSetter import associate_to_sender_lora
from Display import oled
from common_tmp import *

try:
  import usocket as socket
except:
  import socket

from ConfSetter.commonSetter import setCommon
import machine, network
import json
from time import sleep
import urandom
import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'LOCAT-AP'
password = '123456789'

def random_string_size(size):
  random_string = ""
  for x in range(size):
    random_string += urandom.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890')
  return random_string

def web_page():

  WIFI = {}
  WIFI2 = {}
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
        if key == 'WIFI2':
          WIFI2 = json.loads(val)
        if key == 'KOREK':
          KOREK = json.loads(val)
    f.close
  except:
    pass


  html_receiver = """
    <p>
    <span>Wifi1 Essid:</span>
    <input pattern=".{3,}" title="3 characters minimum" value="%s" name="essid" required/>
    <p/>
    <p>
    <span>Wifi1 Password:</span>
    <input pattern=".{3,}" title="8 characters minimum" value="%s" name="wifi_pass" required/>
    <p/>
    
    <hr/>

    <p>
    <span>Wifi2 Essid (Optional Your Mobile AP):</span>
    <input pattern=".{3,}" title="3 characters minimum" value="%s" name="essid2"/>
    <p/>
    <p>
    <span>Wifi2 Password:</span>
    <input pattern=".{3,}" title="8 characters minimum" value="%s" name="wifi_pass2"/>
    <p/>
  
    <hr/>

    <p>
    <span>Korek Website (Optional):</span>
    <input value="%s" name="korek_host"/>
    <p/>
    <p>
    <span>Korek User (Optional):</span>
    <input pattern=".{4,}" title="4 characters minimum" value="%s" name="korek_username"/>
    <p/>
    <p>
    <span>Korek Password (Optional):</span>
    <input pattern=".{4,}" title="4 characters minimum" value="%s" name="korek_password"/>
    </p>
  
    <hr/>

    <p>
    <span>Frequency:</span>
     <select name="frequency" required>
      <option value="60">1 minute sleep (4 hours battery)</option>
      <option value="120">2 minutes sleep (6 hours battery)</option>
      <option value="300">5 minutes sleep (12 hours battery)</option>
      <option value="600">10 minutes sleep (2 days battery)</option>
      <option value="1800">30 minutes sleep (5 days battery)</option>
      <option value="3600">1 hour sleep (10 days battery)</option>
      <option value="7200">2 hour sleep (18 days battery)</option>
      <option value="21600">6 hour sleep (54 days battery)</option>
    </select>
    <p/>""" % (WIFI.get("essid", ""), WIFI.get("pass",""), WIFI2.get("essid", ""), WIFI2.get("pass",""), KOREK.get("korek_host",""), KOREK.get("korek_username",""), KOREK.get("korek_password",""),)


  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
  <body><h1>Welcome to Korek Tracking!</h1>
  <form action="save_locat" method="post">
  <p>
  <span>Cat Name:</span>
  <input pattern=".{4,}" title="4 characters minimum" value="%s" name="title" required/>
  <p/>
  <hr/>""" % (KOREK.get("title",""),)

  html += html_receiver
  
  html += """<input type="submit" value="Send" />
  </form>
  </body></html>"""

  return html

def confirm():
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
            <body><h1>Korek Tracking Configured!</h1></body></html>"""
  return html

def startWebServer(oled_display):

  ap = network.WLAN(network.AP_IF)
  ap.active(True)
  ap.config(essid=ssid, authmode=network.AUTH_WPA_WPA2_PSK, password=password)

  while ap.active() == False:
    pass

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(('', 80))
  s.listen(5)
  #s.settimeout(timeout)

  if oled_display:
    display = oled.startDisplay(SCL,SDA,RST_SCREEN)
    oled.resetScreen(display)
    display.text("starting webserver...", 0, 0)
    display.text("connect to:", 0, 10)
    display.text(str(ap.ifconfig()[0]), 0, 20)
    display.show()

  while True:

    print('Connection successful')
    conn, addr = s.accept()

    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    str_req = str(request)[1:-1]
    print('Content = %s' % str(request))
    res = str_req.split('\\n')[-1]

    try:
      dict_res = dict(i.split('=') for i in res.split('&'))

      # Generate aes and send it to the sender
      aes_pass = str(random_string_size(16))
      dict_res.update({"aes": aes_pass})

      print(setCommon(dict_res))

      response = confirm()
      conn.send(response)
      conn.close()

      if oled_display:
        oled.resetScreen(display)
        display.text("start receiver...", 0, 0)
        display.show()

      # Send conf to sender
      if oled_display:
        display.text("pairing...", 0, 10)
        display.show()
      associate_to_sender_lora(dict_res.get("title"), dict_res.get("aes"), dict_res.get("frequency"))
      if oled_display:
        oled.resetScreen(display)
        display.text("pairing ok", 0, 10)
        display.show()

      sleep(1)
      machine.reset()

      return False
    except Exception as e: 
      print(e)

    response = web_page()
    conn.send(response)
    conn.close()
