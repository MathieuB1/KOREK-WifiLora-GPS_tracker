import machine
import os
from Battery import battery
from common import *
from GPStracker import GPStracker
from Display import oled
from LightLora import loratool
import time

def removeCounterFile():
  try:
    os.remove("counter.txt")
  except:
    pass

def deepSleep(sleep):
  print('entering deepsleep mode!')
  GPStracker.stop_gps()
  machine.deepsleep(sleep)

def startGPS(oled_display=False):

  machine.freq(40000000)


  _one_minute = 60000
  _wakeup_time = _one_minute * 5
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
  gps_timeout = 60000 * 5 # wait for gps during 5 mins

  aes_key = _aes

  start_time = time.ticks_ms()

  trigger_gps_counter = ""

  # Each minute we write a counter
  if _deepsleep > 60000:
    print("writing counter")
    with open("counter.txt", "a") as file:
      for i in range(int(_wakeup_time / _one_minute)):
        file.write("1")
    with open("counter.txt", "r") as file:
      trigger_gps_counter = file.read()
      print(trigger_gps_counter)

  whisper_time = None

  while True:

    # TO REMOVE
    battery_level = battery.read_battery_level()
    #print("battery_level:" + str(battery_level))
    #file = open("batt_level.txt", "a")
    #file.write(str(battery_level) + ";" + str(battery_level) + "\n")
    #file.close()

    if battery_level < _min_battery_level:
      print("send battery level")
      loratool.syncSend('low-' + str(battery_level), aes_key)

    # Activate only when we are not in real tracking mode
    if _deepsleep > 60000:

      print("counter: " + str(len(str(trigger_gps_counter)) * 60000))
      print("frequency: " + str(_deepsleep))

      response = loratool.syncRead(aes_key)
      # This is the pet call
      if response and response['message'] == 'po':
          print("pet call received!")
          failures = 10
          whisper_time = time.ticks_ms()
          # Ensure that we send the ack
          # As we take 2 seconds max for sending data send it 3 times at 1 second interval
          for i in range(3):
            loratool.syncSend("pi", aes_key)
            time.sleep(1)

      # This is the normal usage
      if len(str(trigger_gps_counter)) * 60000 >= _deepsleep or whisper_time :
        print("starting gps...")
        removeCounterFile()
      else:
        deepSleep(_wakeup_time)

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

      # The most important thing in this page
      # As we take 2 seconds max for sending data send it 3 times at 1 second interval
      for i in range(3):
        loratool.syncSend(str(gps), aes_key)
        time.sleep(1)

      if whisper_time:
        elaspsed_whisper = (time.ticks_ms() - whisper_time)
        print("elaspsed whisper time: " + str(elaspsed_whisper))
        if elaspsed_whisper > gps_timeout:
          GPStracker.stop_gps()
          deepSleep(_wakeup_time)
      else:
        GPStracker.stop_gps()
        deepSleep(_wakeup_time)

      if oled_display:
        display.show()

    else:
      # Give some minutes to capture one gps position
      if type(gps) is dict and gps['precision'] < _precision*1.5:
        print('waiting for gps precision')
        lora_counter_failure = 0
        if (elapsed_time > gps_timeout):
          deepSleep(_wakeup_time)

      # Keep-alive
      print('sending acknowlegment')
      loratool.syncSend('ack', aes_key)

      if oled_display:
        oled.resetScreen(display)
        display.text("no gps precision", 0, 0)
        display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
        display.text("lora sent:" + str(lora_counter), 0, 20)

      if battery_level < _min_battery_level:
        if oled_display:
          display.text("low battery:" + str(battery_level), 0, 30)

      if oled_display:
        display.show()

      lora_counter_failure += 1
      if lora_counter_failure == failures:
        deepSleep(_wakeup_time)

    print("failures:" + str(lora_counter_failure))

    # wait before calling gps again
    time.sleep(_wait_for_gps)
