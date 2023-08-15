import os, machine
import receiveGPS
from Web.Webserver import startWebServer
from Web.Trackerserver import run_web_server

import _thread



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

    print("start korek tracking...")
    oled_display = True

    reset_conf_file()

    default_conf = 0
    try:
        file = open("common.py", "r")
        default_conf = len(file.read()[:128])
        file.close()
    except:
        pass

    if default_conf > 0:
        print("conf loaded!")
    else:
        startWebServer(oled_display)

    # Start the web server thread
    _thread.start_new_thread(run_web_server, ())

    # Start the receiver thread
    _thread.start_new_thread(receiveGPS.receiveGPS(oled_display), ())

    # Keep the main thread running
    while True:
        pass


if __name__ == '__main__':
  main()
