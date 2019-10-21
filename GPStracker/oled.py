from machine import Pin, I2C
import ssd1306

def startDisplay(scl,sda,rst):

  SCREEN_WIDTH = 128
  SCREEN_HEIGHT = 64

  rst=Pin(rst, Pin.OUT)
  rst.value(1)
  scl = Pin(scl, Pin.OUT, Pin.PULL_UP)
  sda = Pin(sda, Pin.OUT, Pin.PULL_UP)
  i2c = I2C(scl=scl, sda=sda)
  oled = ssd1306.SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c) # 128 x 64 pixels
  return oled

def resetScreen(oled):
    oled.fill(0)
    oled.show()
