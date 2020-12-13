KOREK-WifiLora-GPS_tracker

Live GPS-tracker for KOREK

#### Hardware:

- 1 Heltec V2 ESP32 Board with Wifi & Lora
- Average Consumption 0.08A max 0.27A
- 1 Heltec V2 ESP32 Board with Wifi & Lora & Pin 17 is used for capturing GPS data
- Average consumption 0.25A max 0.37A

#### Feature:

  - Capture gps data and send it to korek.ml
  - Send data using Wifi & Lora
  - Track your pet using korek-react.ml
  - Webserver for configuring your tracker
  - Battery level support

##### Configure your env & Copy micropython on Board
```
sudo apt-get install python3-pip
sudo pip3 install esptool rshell
wget https://micropython.org/resources/firmware/esp32-idf4-20191220-v1.12.bin
sudo esptool.py --port /dev/ttyUSB0 erase_flash
sudo esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash 0x1000 esp32-idf4-20191220-v1.12.bin
```

##### Installation
```
# 1. Clone this repo
# 2. Set receiver to True/False in main.py (Default is the Lora sender)
# 3. Upload to Heltec v2 board
sudo rshell -p /dev/ttyUSB0 -b 115200
cd KOREK-WifiLora-GPS_tracker/ && cp -r * /pyboard/
# 3. Reboot your board and connect to LOCAT-AP with ip address shown on your display board to add your korek-react.ml credentials & Wifi account
```
#### Web Server
essid: LOCAT-AP
pass: 123456789
webserver: http://192.168.4.1/
#### Debug
```
sudo rshell -p /dev/ttyUSB0
repl
```

