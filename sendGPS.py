import machine

from Battery import battery
from common import *
from GPStracker import GPSsend, GPStracker
from Display import oled
from LightLora import loratool
import time


def startGPS(oled_display=False):

  machine.freq(40000000)

  _deepsleep = DEEPSLEEP
  _min_battery_level = MIN_BATTERY_LEVEL
  _precision = PRECISION
  _wait_for_gps = WAIT_FOR_GPS

  create_title = KOREK['title']

  if oled_display:
    display = oled.startDisplay(SCL,SDA,RST_SCREEN)
    oled.resetScreen(display)
    display.text("starting gps...", 0, 0)
    display.show()

  gps_module = GPStracker.start_gps(RX)
  if oled_display:
    oled.resetScreen(display)
    display.text("pending gps data", 0, 0)
    display.show()
  # wait only 10 seconds for gps hot start
  # (ideally we need 40 seconds here but we need to send lora acks)
  time.sleep(_wait_for_gps)

  lora_counter = 0
  lora_counter_failure = 0
  failures = 10 # keep tracking signal for 3 min 30 seconds
  gps_timeout = 60000 * 5 # wait for gps during 5 mins

  aes_key = create_title

  start_time = time.ticks_ms()

  while True:

    elapsed_time = time.ticks_ms() - start_time

    battery_level = battery.read_battery_level()
    print("battery_level:" + str(battery_level))

    gps = GPStracker.decode_gps(gps_module)
    print(gps)
    #gps = {"lat":7.101813, "lon":43.58843, "date": "300919", "precision":3.0}

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
      if loratool.syncSend(str(gps), aes_key):
        response = loratool.syncRead(aes_key)
        if response:
          if response['message'] == 'ok':
            lora_counter += 1
            lora_counter_failure = 0
            if _deepsleep > 0:
              if oled_display:
                oled.resetScreen(display)
                display.text("lora packet sent!", 0, 0)
                display.text("sleeping...", 0, 10)
                display.show()

              print('entering deepsleep mode!')
              time.sleep(1)
              GPStracker.stop_gps()
              machine.deepsleep(_deepsleep)
      else:
        if oled_display:
          display.text("lora not sent!", 0, 50)

        lora_counter_failure += 1
        if lora_counter_failure > failures:
          GPStracker.stop_gps()
          machine.deepsleep(_deepsleep)

      if oled_display:
        display.show()

    else:
      # Give some minutes to capture one gps position
      if type(gps) is dict and gps['precision'] < _precision*1.5:
        print('waiting for gps precision')
        lora_counter_failure = 0
        if (elapsed_time > gps_timeout):
          GPStracker.stop_gps()
          machine.deepsleep(_deepsleep)

      # Keep-alive
      print('sending acknowlegment')
      loratool.syncSend('ack', aes_key)

      if oled_display:
        oled.resetScreen(display)
        display.text("no gps precision", 0, 0)
        display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
        display.text("lora sent:" + str(lora_counter), 0, 20)
      if battery_level < _min_battery_level:
        loratool.syncSend('low', aes_key)
        if oled_display:
          display.text("low battery:" + str(battery_level), 0, 30)

      if oled_display:
        display.show()

      lora_counter_failure += 1
      if lora_counter_failure > failures:
        GPStracker.stop_gps()
        machine.deepsleep(_deepsleep)

    print("failures:" + str(lora_counter_failure))

    # wait before calling gps again
    time.sleep(_wait_for_gps)
