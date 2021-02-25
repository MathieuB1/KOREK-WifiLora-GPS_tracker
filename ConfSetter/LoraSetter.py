# Do it in lora instead of wifi
from ConfSetter.commonSetter import setCommon
from LightLora import loratool
import machine, time

password = '123456789'
confirmation = 'init:ok'

def associate_to_sender_lora (title, aes_pass, frequency):
    print("Pending association...")
    data = "title=" + title + "&frequency=" + str(int(frequency)*1000) + "&aes=" + aes_pass
    lora_init = "init:" + data
    while True:
        loratool.syncSend(lora_init, password)
        response = loratool.syncRead(password)
        if response and response['message'] == confirmation:
            break
    print("Initialization Done!")


def associateLora ():
    print("Associating...")
    res = ""
    while True:
        response = loratool.syncRead(password)
        print(response)
        init_message = response['message'].split(":") if response else None
        if init_message and init_message[0] == 'init':
            res = init_message[1]
            break
    dict_res = dict(i.split('=') for i in res.split('&'))
    setCommon(True, dict_res)

    # Wait until RX on the receiver
    time.sleep(1)
    # Send confirmation on receiver!
    # As we take 2 seconds max for sending data send it 3 times at 1 second interval
    for i in range(3):
        loratool.syncSend(confirmation, password)
        time.sleep(1)

    print("Association Done!")
    machine.reset()
