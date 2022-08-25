import machine, json
from common import *
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
  _deepsleep = DEEPSLEEP
  _korek = KOREK
  _wifi = WIFI
  _aes = AES

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

  aes_key = _aes

  lora_signal = -999

  battery_level = 0

  whistle = True

  while True:

    if _deepsleep > 60000 and whistle:
      loratool.syncSend('po', aes_key)
      display.text("whistle...", 0, 0)
      display.show()

    gps = {"date": "", "lat": 0, "lon": 0, "batt": 0, "precision": 100}

    try:
      response = loratool.syncRead(aes_key)
      print("received:" + str(response))
      if response:
        lora_signal = response['signal_strengh']
        display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)
        display.show()

        message = response['message']
        if message.startswith("ack"):
          print('lora received')
          battery_level = message.split("-")[1] if len(message.split("-")) > 1 else "N/A"
        elif message == "pi":
          whistle = False
          print('whistle sent!')
        elif message.startswith("low"):
          print("battery: " + str(message))
          battery_level = message.split("-")[1] if len(message.split("-")) > 1 else "N/A"
          activate_battery_led(low_battery_led)
        else:
          print("mess:" + str(message))
          lora_counter += 1
          gps = json.loads(message.replace("'","\""))
          _korek['title'] = gps['title']
    except Exception as e:
      print(str(e))
      print('Nope this is not our Lora packet!')
      continue

    print(gps)

    if type(gps) is dict \
            and gps.get('date') is not None \
            and gps.get('lat') is not None \
            and gps.get('lon') is not None \
            and gps.get('precision') is not None \
            and gps['date'] != "" and gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < _precision:

      whistle = False

      oled.resetScreen(display)
      display.text("tracking " + _korek["title"], 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("wifi sent: " + str(wifi_counter), 0, 20)
      display.text("lora read:" + str(lora_counter), 0, 30)
      display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)

      if gps['batt'] != 0:
        battery_level = gps['batt']
        display.text("batt:" + str(battery_level) + "%", 0, 50)

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
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("wifi sent: " + str(wifi_counter), 0, 20)
      display.text("lora read:" + str(lora_counter), 0, 30)
      display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)

      # CHECK HERE battery_level
      if battery_level != 0:
        display.text("batt:" + str(battery_level) + "%", 0, 50)

      display.show()

