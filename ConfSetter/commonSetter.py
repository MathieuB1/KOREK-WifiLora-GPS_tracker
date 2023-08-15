
def setCommon(dict_res):
  file = open("../common_tmp.py", "r")
  default_conf = file.read()
  file.close()

  file = open("../common.py", "w")
  file.write(default_conf)
  file.write('DEEPSLEEP=%s\n' % (str(int(dict_res.get("frequency", 0))*1000)))
  file.write('AES="%s"\n' % (str(dict_res.get("aes", ""))))
  tuple_korek = (dict_res["korek_host"], dict_res["korek_username"], dict_res["korek_password"], dict_res["title"],)
  file.write('KOREK={"korek_host":"%s", "korek_username":"%s", "korek_password":"%s", "title":"%s" }\n' % tuple_korek)
  tuple_wifi = (dict_res["essid"], dict_res["wifi_pass"],)
  file.write('WIFI={"essid":"%s", "pass":"%s"}\n' % tuple_wifi)
  tuple_wifi2 = (dict_res["essid2"], dict_res["wifi_pass2"],)
  file.write('WIFI2={"essid":"%s", "pass":"%s"}\n' % tuple_wifi2)
  file.close()

  return True

