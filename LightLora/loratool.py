import time, binascii
from LightLora import lorautil, crypt

lr = lorautil.LoraUtil()

def syncSend(txt, aes_key):
  try:
    crypted = crypt.cryptdata(txt, aes_key)
    print('sending lora packet')
    lr.sendPacket(0xff, 0x41, binascii.b2a_base64(crypted, newline=False))
    sendTime = time.ticks_ms()
    while not lr.isPacketSent():
      if (time.ticks_ms() - sendTime) > 100:  # send during 100 ms the message
        return False
  except Exception as e:
    print(str(e))
    return False
  return True

def syncRead(aes_key):
  print('reading lora packet')
  waitingTime = time.ticks_ms()
  while not lr.isPacketAvailable():
    if (time.ticks_ms() - waitingTime) > 2000:  # wait 2s second for receiving the packet
      return False
  try:
    packet = lr.readPacket()
    if packet and packet.msgTxt:
      return {"message": crypt.decryptdata(binascii.a2b_base64(packet.msgTxt)[1:], aes_key).decode("utf-8").strip(),
              "signal_strengh": packet.rssi}
  except Exception as e:
    print(str(e))
    return False