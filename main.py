import sendGPS, receiveGPS
from ConfSetter.LoraSetter import associateLora
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
        ## Choose lora or wifi for the association
        association_mode = "lora"

        print("starting in sender mode!")
        if default_conf > 0:
            print("conf loaded!")
        else:
            if association_mode == "wifi":
                # Prepare webserver to receive a POST for association
                # Only available on ESP chips
                startWebServer(isSender=True, oled_display=oled_display)
            else:
                # Prepare Lora to receive a message for association
                associateLora()

        sendGPS.startGPS(oled_display=oled_display)

if __name__ == '__main__':
  main()
