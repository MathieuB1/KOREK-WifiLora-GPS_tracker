import machine

from Battery import battery
from common import *
from GPStracker import GPSsend, GPStracker
from Display import oled
from LightLora import loratool
from time import sleep



def startGPS():

  machine.freq(40000000)

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

  lora_counter = 0
  lora_counter_failure = 0
  failures = 5

  battery_level = 0

  aes_key = KOREK['title']
 
  while True:
    battery_level = battery.read_battery_level()
    print("battery_level:" + str(battery_level))

    gps = GPStracker.decode_gps(gps_module)
    #gps = {"lat":7.101813, "lon":43.58843, "date": "300919", "precision":3.0}
    
    if type(gps) is dict and gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < PRECISION:

      oled.resetScreen(display)
      display.text("tracking " + KOREK["title"], 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("lora sent:" + str(lora_counter), 0, 20)
      if battery_level < MIN_BATTERY_LEVEL:
        display.text("low battery:" + str(battery_level), 0, 30)
      display.show()

      display.text("using lora!", 0, 40)
      gps['title'] = KOREK['title']
      if loratool.syncSend(str(gps), aes_key):
        response = loratool.syncRead(aes_key)
        if response:
          if response['message'] == 'ok':
            lora_counter += 1
            lora_counter_failure = 0
            if DEEPSLEEP > 0:
              oled.resetScreen(display)
              display.text("lora packet sent!", 0, 0)
              display.text("sleeping...", 0, 10)
              display.show()

              print('entering deepsleep mode!')
              sleep(1)
              GPStracker.stop_gps()
              machine.deepsleep(DEEPSLEEP)
      else:
        display.text("lora not sent!", 0, 50)
        lora_counter_failure += 1
        if lora_counter_failure > failures:
          GPStracker.stop_gps()
          machine.deepsleep(DEEPSLEEP)
      display.show()

    else:
      # Keep-alive
      print('sending acknowlegment')
      loratool.syncSend('ack', aes_key)
       
      oled.resetScreen(display)
      display.text("no gps precision", 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("lora sent:" + str(lora_counter), 0, 20)
      if battery_level < MIN_BATTERY_LEVEL:
        display.text("low battery:" + str(battery_level), 0, 30)
      display.show()

      lora_counter_failure += 1
      if lora_counter_failure > failures:
        GPStracker.stop_gps()
        machine.deepsleep(DEEPSLEEP)

    print("failures:" + str(lora_counter_failure))

    # wait before calling gps again
    sleep(WAIT_FOR_GPS)
