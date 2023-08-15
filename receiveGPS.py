import machine, json
from common import *
from GPStracker import GPSsend
from Wifi import wifi
from Display import oled
from LightLora import loratool
from Battery import battery
import time

def activate_battery_led(pin):
  onboard_led = machine.Pin(pin, machine.Pin.OUT)
  onboard_led.on()


def popfile(file_path, max_length=5):
  # Read the file contents
  with open(file_path, 'r') as file:
    lines = file.readlines()

  if len(lines) > max_length:
    # Remove the first line
    lines = lines[1:]
  
    # Overwrite the file with the modified contents
    with open(file_path, 'w') as file:
      for line in lines:
        file.write(line)


def check_korek_activated(korek):
  if korek["korek_host"] != "" and korek["title"] != "" and korek["korek_username"] != "" and korek["korek_password"] != "":
    return True
  return False

def receiveGPS(oled_display):

  low_battery_led = 25

  _precision = PRECISION

  _min_battery_level = MIN_BATTERY_LEVEL
  _deepsleep = DEEPSLEEP
  _korek = KOREK
  _positions_file = POSITIONS_FILE
  _aes = AES

  started = False
  product_id = False
  create_title = _korek['title']

  if oled_display:
    display = oled.startDisplay(SCL,SDA,RST_SCREEN)
    oled.resetScreen(display)
    display.show()

  wifi_counter = 0
  lora_counter = 0
  failure_counter = 0

  file_counter = 0

  aes_key = _aes

  lora_signal = -999

  battery_level = 0

  whistle = True

  while True:

    if _deepsleep > 60000 and whistle:

      loratool.syncSend('po', aes_key)
      print("whistle...")
      if oled_display:
        display.text("whistle...", 0, 0)
        display.show()

    gps = {"date": "", "lat": 0, "lon": 0, "batt": 0, "precision": 100}

    try:
      response = loratool.syncRead(aes_key)
      print("received:" + str(response))
      if response:
        lora_signal = response['signal_strengh']
        print("lora rssi:" + str(lora_signal) + 'dB')
        if oled_display:
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

    if type(gps) is dict \
            and gps.get('date') is not None \
            and gps.get('lat') is not None \
            and gps.get('lon') is not None \
            and gps.get('precision') is not None \
            and gps['date'] != "" and gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < _precision:

      print(gps)

      whistle = False

      print("tracking " + _korek["title"])
      print("gps:" + str(100 - gps['precision']) + "%")
      print("wifi sent: " + str(wifi_counter))
      print("lora read:" + str(lora_counter))
      print("lora rssi:" + str(lora_signal) + 'dB')

      if oled_display:
        oled.resetScreen(display)
        display.text("tracking " + _korek["title"], 0, 0)
        display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
        display.text("wifi sent: " + str(wifi_counter), 0, 20)
        display.text("lora read:" + str(lora_counter), 0, 30)
        display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)

      if gps['batt'] != 0:
        battery_level = gps['batt']
        print("batt:" + str(battery_level) + "%")
        if oled_display:
          display.text("batt:" + str(battery_level) + "%", 0, 50)

      if oled_display:
        display.show()

      if not wifi.connect_wifi():
        print("wifi not found!")
        if oled_display:
          display.text("wifi not found!", 0, 50)
          display.show()
      else:
        if oled_display:
          display.show()

        # Send to KOREK
        if check_korek_activated(_korek):
          if not started:
            insertdate = gps['date'][:2] + gps['date'][3:5] + gps['date'][8:10] # ddmmyy
            product_id, create_title = GPSsend.create_product(insertdate, _korek)
            started = True
          sent = GPSsend.update_position(create_title, product_id, gps['lon'], gps['lat'], _korek)

          if sent:
            wifi_counter += 1
          else:
            failure_counter += 1
            if failure_counter > 3:
              started = False
              failure_counter = 0

        else:
          # Save to file
          with open(_positions_file, 'a+') as file:
            file.write('{"date": "' + str(gps['date'].split(" ")[0]) + '", "time": "' + str(gps['date'].split(" ")[1]) + '" , "lat": ' + str(gps['lat']) + ', "lon": ' + str(gps['lon']) + ', "precision":' + str(100 - gps['precision']) + '}\n')
          popfile(_positions_file)
          file_counter += 1

    else:
      if oled_display:
        oled.resetScreen(display)
        display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
        if check_korek_activated(_korek):
          display.text("wifi sent: " + str(wifi_counter), 0, 20)
        else:
          display.text("file write: " + str(file_counter), 0, 20)
        display.text("lora read:" + str(lora_counter), 0, 30)
        display.text("lora rssi:" + str(lora_signal) + 'dB', 0, 40)

      # CHECK HERE battery_level
      if battery_level != 0:
        print("batt:" + str(battery_level) + "%")
        if oled_display:
          display.text("batt:" + str(battery_level) + "%", 0, 50)
      if oled_display:
        display.show()

    time.sleep(0.2)
