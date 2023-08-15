import urequests



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
    res = (None,None,)

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
      return res
  except:
    print('cannot create product!')
    return res


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
