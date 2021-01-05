import machine
import os
from Battery import battery
from common import *
from GPStracker import GPSsend, GPStracker
from Display import oled
from LightLora import loratool
import time

# See if we got a whistle
#response = loratool.syncRead(aes_key)
#if response:
#  if response['message'] == 'up':
#    loratool.syncSend('up_ok', aes_key)
#    lora_counter_failure = -5

def deepSleep(sleep):
  print('entering deepsleep mode!')
  GPStracker.stop_gps()
  machine.deepsleep(sleep)

def startGPS(oled_display=False):

  machine.freq(40000000)

  _gps_sleep = 60000
  _deepsleep = DEEPSLEEP
  _min_battery_level = MIN_BATTERY_LEVEL
  _precision = PRECISION
  _wait_for_gps = WAIT_FOR_GPS
  _korek = KOREK
  _aes = AES

  create_title = _korek['title']

  lora_counter = 0
  lora_counter_failure = 0
  failures = 5 # keep tracking signal for 1 min 52 seconds
  gps_timeout = 60000 * 3 # wait for gps during 3 mins

  aes_key = _aes

  start_time = time.ticks_ms()

  print("writing counter")
  with open("counter.txt", "a") as file:
    file.write("1")
  file = open("counter.txt", "r")
  trigger_gps_counter = file.read()
  file.close()
  print(trigger_gps_counter)

  while True:

    # TO REMOVE
    #battery_level = battery.read_battery_level()
    #print("battery_level:" + str(battery_level))
    #file = open("batt_level.txt", "a")
    #file.write(str(battery_level) + "\n")
    #file.close()

    print("counter: " + str(len(str(trigger_gps_counter)) * 60000))
    print("frequency: " + str(_deepsleep))

    if _deepsleep > 60000:
      response = loratool.syncRead(aes_key)
      # This is the pet call
      if response:
        if response['message'] == 'po':
          print("pet call received!")
          failures = 10
          for i in range(3):
            loratool.syncSend("pi", aes_key)

      # This is the normal usage
      elif len(str(trigger_gps_counter)) * 60000 >= _deepsleep:
        print("starting gps...")
        try:
          os.remove("counter.txt")
        except:
          pass
      else:
        deepSleep(_gps_sleep)

    if oled_display:
      display = oled.startDisplay(SCL, SDA, RST_SCREEN)
      oled.resetScreen(display)
      display.text("starting gps...", 0, 0)
      display.show()

    gps_module = GPStracker.start_gps(RX)

    if oled_display:
      oled.resetScreen(display)
      display.text("pending gps data", 0, 0)
      display.show()
    # wait 25 seconds for gps start
    # (ideally we need 40 seconds here but we need to send lora acks)
    time.sleep(_wait_for_gps * 2.5)

    elapsed_time = time.ticks_ms() - start_time

    gps = GPStracker.decode_gps(gps_module)
    #gps = {"lat":7.101813, "lon":43.58843, "date": "300919", "precision":3.0}
    print(gps)

    if type(gps) is dict and gps['date'] != "" and gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < _precision:

      if oled_display:
        oled.resetScreen(display)
        display.text("tracking " + create_title, 0, 0)
        display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
        display.text("lora sent:" + str(lora_counter), 0, 20)
      if battery_level < _min_battery_level:
        if oled_display:
          display.text("low battery:" + str(battery_level), 0, 30)

      if oled_display:
        display.text("using lora!", 0, 40)
        display.show()

      gps['title'] = create_title
      response = False
      while not response:
        loratool.syncSend(str(gps), aes_key)
        print("sending position!")
        response = loratool.syncRead(aes_key)
        if response:
          if response['message'] == 'ok':
            print("position received!")
            lora_counter += 1
            lora_counter_failure = 0
            if _deepsleep > 0:
              if oled_display:
                oled.resetScreen(display)
                display.text("lora packet sent!", 0, 0)
                display.text("sleeping...", 0, 10)
                display.show()

              GPStracker.stop_gps()
              deepSleep(_gps_sleep)
      else:
        if oled_display:
          display.text("lora not sent!", 0, 50)

        lora_counter_failure += 1
        if lora_counter_failure == failures:
          deepSleep(_gps_sleep)

      if oled_display:
        display.show()

    else:
      # Give some minutes to capture one gps position
      if type(gps) is dict and gps['precision'] < _precision*1.5:
        print('waiting for gps precision')
        lora_counter_failure = 0
        if (elapsed_time > gps_timeout):
          deepSleep(_gps_sleep)

      # Keep-alive
      print('sending acknowlegment')
      loratool.syncSend('ack', aes_key)

      if oled_display:
        oled.resetScreen(display)
        display.text("no gps precision", 0, 0)
        display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
        display.text("lora sent:" + str(lora_counter), 0, 20)

      if battery_level < _min_battery_level:
        loratool.syncSend('low-' + str(battery_level), aes_key)
        if oled_display:
          display.text("low battery:" + str(battery_level), 0, 30)

      if oled_display:
        display.show()

      lora_counter_failure += 1
      if lora_counter_failure == failures:
        deepSleep(_gps_sleep)

    print("failures:" + str(lora_counter_failure))

    # wait before calling gps again
    time.sleep(_wait_for_gps)