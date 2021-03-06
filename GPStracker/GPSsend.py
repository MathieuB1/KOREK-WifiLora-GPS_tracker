import network
import urequests
import time
import socket

def connect_wifi(essid, password):
  wifi_timeout = 10
  try:
    station = network.WLAN(network.STA_IF)
    if station.isconnected():
      return 'wifi already connected!'
    station.active(True)
    station.connect(essid, password)
    counter = 0
    while station.isconnected() == False:
      time.sleep(1)
      counter += 1
      if counter > wifi_timeout:
        return False
    return 'wifi successfuly connected!'
  except:
    print('Cannot connect to wifi!')
    return False

def disconnect():
    station = network.WLAN(network.STA_IF)
    station.disconnect()
    station.active(False)
    return 'wifi disconnected!'

def associate_to_sender(ap_name, ap_password, title, aes_pass, frequency):
  print("Enable Wifi")
  station = network.WLAN(network.STA_IF)
  station.active(True)
  password_set = False
  while not password_set:
    print("Scan ESSIDS")
    time.sleep(1)
    aps = station.scan()
    for i in aps:
      print(i)
      if(i[0].startswith(ap_name)):
        print("Connect to AP")
        connect_wifi(i[0], ap_password)
        addr_info = socket.getaddrinfo("192.168.4.1", 80)[0][-1]
        s = socket.socket()
        s.connect(addr_info)
        print("Send Post")
        data = "title=" + title + "&frequency=" + frequency + "&aes=" + aes_pass
        s.send(bytes('POST / HTTP/1.0\r\nHost: %s\r\n\r\n%s' % (addr_info, data), 'utf8'))
        s.close()
        print("Post Sent!")
        password_set = True
        break

def existing_product(create_title, korek):
  try:
    url = korek["korek_host"] + "/products/?search=" + create_title + "&zip=true"
    headers = {'Content-Type': "application/json", 'Authorization': 'Bearer ' + str(get_token(korek))}
    response = urequests.request("GET", url, headers=headers)
    if response.status_code == 200:
      res = response.json()
      if res['count'] > 0:
        product_id = res['results'][0]['id']
        response.close()
        return product_id
      else:
        return False
    else:
      return False
  except:
    print('cannot check existing product!')
    return False

def create_product(creation_date, korek):
  try:
    url = korek["korek_host"] + "/products/?zip=true"
    create_title = korek["title"] + "-" + str(creation_date)

    # Check if products exists
    product_id = existing_product(create_title, korek)
    if product_id:
      return (product_id,create_title,)

    # Create a new product
    payload = "{\"title\":\"" + create_title + "\",\"subtitle\":\"gps tracking\"}"
    headers = {'Content-Type': "application/json", 'Authorization': 'Bearer ' + str(get_token(korek))}
    response = urequests.request("POST", url, data=payload, headers=headers)
    if response.status_code == 201:
      product_id = str(response.json()['id'])
      print("product was created!")
      res = (product_id,create_title,)
      response.close()
      return res
    else:
      print("please create the korek user before sending data!")
      return False
  except:
    print('cannot create product!')
    return False


def refresh_token(korek):
  token = ""
  try:
    url = korek["korek_host"] + "/api-token-refresh/"
    payload = "{\"token\":\"" + token + "\"}"
    headers = {'Content-Type': "application/json"}
    response = urequests.request("POST", url, data=payload, headers=headers)
    if response.status_code == 200:
      token = response.json()['token']
    response.close()
  except:
    print('token refresh failed!')
    pass
  return token


def get_token(korek):
  token = ""
  try:
    url = korek["korek_host"] + "/api-token-auth/"
    payload = "{\"username\":\"" + korek["korek_username"] + "\",\"password\":\"" + korek["korek_password"] + "\"}"
    headers = {'Content-Type': "application/json"}
    response = urequests.request("POST", url, data=payload, headers=headers)
    print("Token response: " + str(response.status_code))
    if response.status_code == 200:
      token = response.json()['token']
    response.close()
  except:
    print('token generation failed!')
    pass
  return token

def update_position(create_title, product_id, lon, lat, korek):
  updated = False
  try:
    url = korek["korek_host"] + "/products/" + str(product_id) + "/"
    payload = "{\"title\": \"" + create_title + "\",\"locations\": [{\"coords\": [" + str(lon) + ", " + str(lat) + "]}]}"
    headers = {'Content-Type': "application/json", 'Authorization': 'Bearer ' + str(get_token(korek))}
    response = urequests.request("PUT", url, data=payload, headers=headers)
    if response.status_code == 200:
      updated = True
      print(create_title + ' article was updated!')
      response.close()
  except:
    print('cannot update product!')
    pass
  return updated
