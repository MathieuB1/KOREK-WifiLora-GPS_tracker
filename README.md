KOREK-WifiLora-GPS_tracker

Live GPS-tracker for KOREK

#### Hardware:

- Heltec V2 ESP32 Board with Wifi & Lora
- Pin 17 is used for capturing GPS data
- Consumption 0.713mW/h

#### Feature:

  - Capture gps data
  - Send data through Wifi & Lora
  - Track your pet using korek-react.ml

#### Installation

> Connect your Heltec chip

##### Configure your env & Copy micropython on Board
```
sudo apt-get install python3-pip
sudo pip3 install esptool rshell
wget https://micropython.org/resources/firmware/esp32-20190529-v1.11.bin
sudo esptool.py --port /dev/ttyUSB0 erase_flash
sudo esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash 0x1000 esp32-20190529-v1.11.bin
```

##### Copy files into Board
```
sudo rshell -p /dev/ttyUSB0
# Clone this repo & modify the common.py to add your KOREK credentials & Wifi aacount
cd KOREK-WifiLora-GPS_tracker/ && cp -r * /pyboard/
```

#### Debug
```
sudo rshell -p /dev/ttyUSB0
repl
```

