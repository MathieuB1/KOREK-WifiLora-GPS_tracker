import time
from LightLora import lorautil, crypt

lr = lorautil.LoraUtil()

def syncSend(txt, aes_key):
  try:
    crypted = crypt.cryptdata(txt, aes_key)
    print('sending lora packet')
    lr.sendPacket(0xff, 0x41, crypted)
    sendTime = 0
    while not lr.isPacketSent() :
      time.sleep(.1)
      # after 2 seconds of waiting for send just give up
      sendTime += 1
      if sendTime > 19 :
        return False
  except Exception as e:
    print(str(e))
    return False
  return True

def syncRead(aes_key, sleep=10):
  print('reading lora packet')
  waitingTime = 0
  while not lr.isPacketAvailable():
    time.sleep(1)
    waitingTime += 1
    if waitingTime > sleep: # wait 10 seconds for receiving the packet
      return False
  try:
    packet = lr.readPacket()
    if packet and packet.msgTxt:
      if syncSend("ok", aes_key):
        return { "message": crypt.decryptdata(packet.msgTxt, aes_key).decode("utf-8").strip(), "signal_strengh": packet.rssi}
      else:
        return False
  except Exception as e:
    print(str(e))
    return False
