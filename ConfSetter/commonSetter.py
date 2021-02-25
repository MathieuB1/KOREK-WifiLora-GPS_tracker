
def setCommon(isSender, dict_res):
  file = open("../common_tmp.py", "r")
  default_conf = file.read()
  file.close()

  file = open("../common.py", "w")
  file.write(default_conf)
  file.write('DEEPSLEEP=%s\n' % (str(int(dict_res.get("frequency",0))*1000)))
  file.write('AES="%s"\n' % (str(dict_res.get("aes",""))))
  tuple_korek = (dict_res.get("korek_username",""),dict_res.get("korek_password",""),dict_res.get("title",""),) if isSender else (dict_res["korek_username"],dict_res["korek_password"],dict_res["title"],)
  file.write('KOREK={"korek_host":"https://korekk.ml", "korek_username":"%s", "korek_password":"%s", "title":"%s" }\n' % tuple_korek )
  tuple_wifi = (dict_res.get("essid",""),dict_res.get("wifi_pass",""),) if isSender else (dict_res["essid"],dict_res["wifi_pass"],)
  file.write('WIFI={"essid":"%s", "pass":"%s"}\n' % tuple_wifi )
  file.close()

  return True

