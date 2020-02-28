import machine
import GPStracker
import GPSsend
from Display import oled
from common import *

def startGPS():
  
  started = False
  product_id = False
  create_title = ""

  display = oled.startDisplay(SCL,SDA,RST_SCREEN)
  oled.resetScreen(display)
  display.text("starting gps...", 0, 0)
  display.show()

  gps_module = GPStracker.start_gps(RX)
  oled.resetScreen(display)
  display.text("pending gps data", 0, 0)
  display.show()  

  counter = 0

  while True:
    gps = GPStracker.decode_gps(gps_module)
    #gps = {"lat":7.101813, "lon":43.58843, "date": "300919", "precision":3.0}
    
    if gps['lat'] != 0 and gps['lon'] != 0 and gps['precision'] < PRECISION:

      oled.resetScreen(display)
      display.text("tracking " + KOREK["title"], 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("sent: " + str(counter), 0, 20)
      display.show()

      if not GPSsend.connect_wifi(WIFI['essid'], WIFI['pass']):
          display.text("!!wifi not found!!", 0, 30)
          display.show()

      if not started:
        product_id, create_title = GPSsend.create_product(gps['date'], KOREK)
        started = True

      sent = GPSsend.update_position(create_title, product_id, gps['lon'],gps['lat'], KOREK)
      if sent:
        counter += 1

    else:
      oled.resetScreen(display)
      display.text("no gps precision", 0, 0)
      display.text("gps:" + str(100 - gps['precision']) + "%", 0, 10)
      display.text("sent: " + str(counter), 0, 20)
      display.show()

    #machine.deepsleep(30000)
