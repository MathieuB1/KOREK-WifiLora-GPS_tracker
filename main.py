import sendGPS, receiveGPS
from Web.Webserver import startWebServer
import os, machine

def reset_conf_file ():
    # PRG button pressed
    button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP).value()
    if button == 0:
        print("reset button pressed")
        os.remove("common.py")
        file = open("common.py", "w")
        file.write("")
        file.close()
        machine.reset()

def main():
    # Board is the Sender by Default
    receiver = False

    print("start korek tracking...")
    default_conf = 0

    reset_conf_file()

    try:
        file = open("common.py", "r")
        default_conf = len(file.read()[:128])
        file.close()
    except:
        pass

    if receiver:
        print("starting in receiver mode!")
        print("conf loaded!") if default_conf > 0 else startWebServer(isSender=False, oled_display=True)
        receiveGPS.receiveGPS()
    else:
        oled_display = False
        print("starting in sender mode!")
        print("conf loaded!") if default_conf > 0 else startWebServer(isSender=True, oled_display=oled_display)
        sendGPS.startGPS(oled_display=oled_display)

if __name__ == '__main__':
  main()
