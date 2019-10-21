import machine
import GPStracker
import GPSsend
import oled


def startGPS():

  # Display Pins
  SCL=15
  SDA=4
  RST_SCREEN=16

  # Pin where my GPS is connected
  RX=17
  PRECISION=4.5

  # Box settings
  ESSID="Livebox-0AD4"
  PASS="7374C542512D9137949155E7E6"

  # Korek settings
  KOREK = { "korek_host": "https://korek.ml", 
            "korek_username":"toto", 
            "korek_password":"toto",
            "title": "poppiz",
            }
  
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

      if not GPSsend.connect_wifi(ESSID, PASS):
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
