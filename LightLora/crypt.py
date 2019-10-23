from ucryptolib import aes


def cryptdata(text, aes_key):
  division = len(text) / 16
  space_to_add = abs(16 - int((16 * float("0." + str(division).split(".")[1]))))
  spaceadded = " " * space_to_add
  crypto = aes(b"" + str(aes_key[0:4]) *4, 1)
  enc = crypto.encrypt(b"" + text + spaceadded)
  return enc

def decryptdata(text, aes_key):
  crypto = aes(b""+ str(aes_key[0:4]) *4, 1)
  return crypto.decrypt(text)
