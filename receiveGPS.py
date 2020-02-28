import machine, json
from common import *
from GPStracker import GPStracker
from GPStracker import GPSsend
from Display import oled
from LightLora import loratool

def receiveGPS():

  #machine.freq(160000000)

  started = False
  product_id = False
  create_title = KOREK['title']

  display = oled.startDisplay(SCL,SDA,RST_SCREEN)
  oled.resetScreen(display)
  display.show()

  wifi_counter = 0
  lora_counter = 0
  failure_counter = 0
  
  tracking_date = ""

  aes_key = KOREK['title']

  lora_signal = -999
  
  while True:
    gps = {"lat": 0, "lon": 0, "precision": 100}

    try:
      response = loratool.syncRead(aes_key)
      if response:
        lora_signal = response['signal_strengh']
        display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)
        display.show()

        if response['message'] == "ok" or response['message'] == "ack":
          # Save battery
          print('lora received')
        else:
          lora_counter += 1 
          gps = json.loads(response['message'].replace("'","\""))
          KOREK['title'] = gps['title']
    except Exception as e:
      print(str(e))
      print('Nope this is not our Lora packet!')
      continue

    if type(gps) is dict and gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < PRECISION:

      oled.resetScreen(display)
      display.text("tracking " + KOREK["title"], 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("wifi sent: " + str(wifi_counter), 0, 20)
      display.text("lora read:" + str(lora_counter), 0, 30)
      display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)
      display.show()

      if tracking_date != gps['date']:
        tracking_date = gps['date']
        started = False

      if not GPSsend.connect_wifi(WIFI['essid'], WIFI['pass']):
        display.text("wifi not found!", 0, 50)
        display.show()
      else:  
        display.show()
        if not started:
          product_id, create_title = GPSsend.create_product(gps['date'], KOREK)
          started = True
        sent = GPSsend.update_position(create_title, product_id, gps['lon'],gps['lat'], KOREK)
        if sent:
          wifi_counter += 1
        else:
          failure_counter += 1
          if failure_counter > 3:
            started = False
            failure_counter = 0
    else:
      oled.resetScreen(display)
      display.text("no gps precision", 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("wifi sent: " + str(wifi_counter), 0, 20)
      display.text("lora read:" + str(lora_counter), 0, 30)
      display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)
      display.show()

