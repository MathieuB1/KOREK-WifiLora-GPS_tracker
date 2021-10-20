import time
from LightLora import lorautil, crypt

lr = lorautil.LoraUtil()

def syncSend(txt, aes_key):
  try:
    crypted = crypt.cryptdata(txt, aes_key)
    print('sending lora packet')
    lr.sendPacket(0xff, 0x41, crypted)
    sendTime = time.ticks_ms()
    while not lr.isPacketSent():
      if int((time.ticks_ms() - sendTime)/1000) > 1:  # send during 1 second the message
        return False
  except Exception as e:
    print(str(e))
    return False
  return True

def syncRead(aes_key, sleep=2):
  print('reading lora packet')
  waitingTime = time.ticks_ms()
  while not lr.isPacketAvailable():
    if int((time.ticks_ms() - waitingTime)/1000) > sleep:  # wait 2 seconds for receiving the packet
      return False
  try:
    packet = lr.readPacket()
    if packet and packet.msgTxt:
      return {"message": crypt.decryptdata(packet.msgTxt, aes_key).decode("utf-8").strip(),
              "signal_strengh": packet.rssi}
  except Exception as e:
    print(str(e))
    return False