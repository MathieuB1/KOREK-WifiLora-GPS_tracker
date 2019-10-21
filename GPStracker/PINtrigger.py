import machine

def pull_up_pin(pin):
  led = machine.Pin(pin, machine.Pin.PULL_UP)

def pull_down_pin(pin):
  led = machine.Pin(pin, machine.Pin.PULL_DOWN)