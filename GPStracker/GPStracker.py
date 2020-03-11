import machine, time
from GPStracker import PINtrigger


def start_gps(rx):
  #Vext
  PINtrigger.pull_up_pin(21)
  gps_module = machine.UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=rx)
  return gps_module

def stop_gps():
  PINtrigger.pull_down_pin(1)
  #Vext
  PINtrigger.pull_down_pin(21)

def get_decimals(data):
  try:
    Latitude = data[3:5]
    Longitude = data[5:7]
    decimal_lat = float(Latitude[0][0:2]) + (float(Latitude[0][2:])/60)
    decimal_lon = float(Longitude[0][0:3]) + (float(Longitude[0][3:])/60)
  
    if data[4] == "S":
      decimal_lat = -decimal_lat
    if data[6] == "W":
      decimal_lon = -decimal_lon
    return(decimal_lat, decimal_lon)
  except:
    print('Cannot decode gps position!')


def decode_gps(gps_module):

  data = {"lat": 0, 
           "lon":0, 
           "date":"", 
           "precision": 100}

  timeout = 10000
  start_time = time.ticks_ms()
  while True:
    try:
      line = gps_module.readline()
      elapsed_time = time.ticks_ms() - start_time
      if elapsed_time > timeout:
          return data
      if line and line.startswith("$GNRMC"):  # GPRMC
        gps = [x.rstrip() for x in line.decode("utf-8").split(",")]
        if gps[2] == "V":
          print('waiting for GPS data!')
          continue

        coordinates = get_decimals(gps)

        data["lat"] = coordinates[0]
        data["lon"] = coordinates[1]
        data["date"] = str(gps[9])

      if line and line.startswith("$GNGSA"): # GPGSA
        satellites = [x.rstrip() for x in line.decode("utf-8").split(",")]
        if satellites and len(satellites) > 15: #7
          data["precision"] = float(satellites[15]) #7

      if data["lat"] != 0 and data["lon"] != 0 and data["date"] != "" and data['precision'] != 100:
        return data

    except Exception as e:
      print('Cannot decode gps position!!!')
      print(str(e))
      return data
  return data
