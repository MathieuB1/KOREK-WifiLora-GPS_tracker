import sendGPS, receiveGPS
from Web.Webserver import startWebServer


def main():
    print("start korek tracking...")

    default_conf = 0
    receiver = False

    try:
        file = open("common.py", "r")
        default_conf = len(file.read())
        file.close()
    except:
        pass

    if receiver:
        print("starting in receiver mode!")
        print("conf loaded!") if default_conf > 0 else startWebServer(isSender=False)
        receiveGPS.receiveGPS()
    else:
        print("starting in sender mode!")
        print("conf loaded!") if default_conf > 0 else startWebServer(isSender=True)
        sendGPS.startGPS()

if __name__ == '__main__':
  main()
