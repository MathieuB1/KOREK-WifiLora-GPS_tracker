import machine, json
from common import *
from GPStracker import GPStracker
from GPStracker import GPSsend
from Display import oled
from LightLora import loratool
from Battery import battery

def activate_battery_led(pin):
  onboard_led = machine.Pin(pin, machine.Pin.OUT)
  onboard_led.on()

def receiveGPS():

  #machine.freq(160000000)

  low_battery_led = 25

  _precision = PRECISION
  _min_battery_level = MIN_BATTERY_LEVEL
  _korek = KOREK
  _wifi = WIFI

  started = False
  product_id = False
  create_title = _korek['title']

  display = oled.startDisplay(SCL,SDA,RST_SCREEN)
  oled.resetScreen(display)
  display.show()

  wifi_counter = 0
  lora_counter = 0
  failure_counter = 0
  
  tracking_date = ""

  aes_key = create_title

  lora_signal = -999

  while True:

    battery_level = battery.read_battery_level()

    gps = {"date": "", "lat": 0, "lon": 0, "precision": 100}

    try:
      response = loratool.syncRead(aes_key)
      if response:
        lora_signal = response['signal_strengh']
        display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)
        display.show()

        if response['message'] == "ok" or response['message'] == "ack":
          print('lora received')
        elif response['message'] == "low":
          activate_battery_led(low_battery_led)
        else:
          lora_counter += 1 
          gps = json.loads(response['message'].replace("'","\""))
          _korek['title'] = gps['title']
    except Exception as e:
      print(str(e))
      print('Nope this is not our Lora packet!')
      continue

    print(gps)

    if type(gps) is dict and gps['date'] != "" and gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < _precision:

      oled.resetScreen(display)
      display.text("tracking " + _korek["title"], 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("wifi sent: " + str(wifi_counter), 0, 20)
      display.text("lora read:" + str(lora_counter), 0, 30)
      display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)
      if battery_level < _min_battery_level:
        display.text("voltage:" + str(battery_level) + "V", 0, 50)
      display.show()

      if tracking_date != gps['date']:
        tracking_date = gps['date']
        started = False

      if not GPSsend.connect_wifi(_wifi['essid'], _wifi['pass']):
        display.text("wifi not found!", 0, 50)
        display.show()
      else:
        display.show()
        if not started:
          product_id, create_title = GPSsend.create_product(gps['date'], _korek)
          started = True
        sent = GPSsend.update_position(create_title, product_id, gps['lon'],gps['lat'], _korek)
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
      if battery_level < _min_battery_level:
        display.text("voltage:" + str(battery_level) + "V", 0, 50)
      display.show()

