import machine
from common import *
from GPStracker import GPSsend, GPStracker
from Display import oled
from LightLora import loratool
from time import sleep

machine.freq(80000000)

def startGPS():

  started = False
  product_id = False
  create_title = KOREK['title']

  display = oled.startDisplay(SCL,SDA,RST_SCREEN)
  oled.resetScreen(display)
  display.text("starting gps...", 0, 0)
  display.show()

  gps_module = GPStracker.start_gps(RX)
  oled.resetScreen(display)
  display.text("pending gps data", 0, 0)
  display.show()  

  wifi_counter = 0
  lora_counter = 0
  failure_counter = 0

  aes_key = KOREK['title']

  wifi_activate = True
  GPSsend.connect_wifi(ESSID, PASS)
 
  while True:
    gps = GPStracker.decode_gps(gps_module)
    #gps = {"lat":7.101813, "lon":43.58843, "date": "300919", "precision":3.0}
    
    if type(gps) is dict and gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < PRECISION:

      oled.resetScreen(display)
      display.text("tracking " + KOREK["title"], 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("wifi sent: " + str(wifi_counter), 0, 20)
      display.text("lora sent:" + str(lora_counter), 0, 30)
      display.show()

      if not wifi_activate:

        display.text("using lora!", 0, 40)
        gps['title'] = KOREK['title']
        if loratool.syncSend(str(gps), aes_key):
          response = loratool.syncRead(aes_key)
          if response:
            if response['message'] == 'ok':
              lora_counter += 1
              if lora_counter % WIFI_REACTIVATE == 0:
                GPSsend.connect_wifi(ESSID, PASS)
                wifi_activate = True
                #machine.deepsleep(DEEPSLEEP)
        else:
          display.text("lora not sent!", 0, 50)
        display.show()

      else:
        display.text("using wifi!", 0, 40)
        display.show()
        if not started:
          print(gps)
          product_id, create_title = GPSsend.create_product(gps['date'], KOREK)
          started = True

        sent = GPSsend.update_position(create_title, product_id, gps['lon'],gps['lat'], KOREK)
        if sent:
          wifi_counter += 1
        else:
          failure_counter += 1
          if failure_counter > 3:
            started = True
            failure_counter = 0

        if wifi_counter > 0:
          wifi_activate = False
          GPSsend.disconnect()
        #machine.deepsleep(DEEPSLEEP)

    else:
      # Keep-alive
      print('sending acknowlegment')
      loratool.syncSend('ack', aes_key)
       
      oled.resetScreen(display)
      display.text("no gps precision", 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("wifi sent: " + str(wifi_counter), 0, 20)
      display.text("lora sent:" + str(lora_counter), 0, 30)
      display.show()
    
    # wait before calling gps again
    sleep(WAIT_FOR_GPS)
