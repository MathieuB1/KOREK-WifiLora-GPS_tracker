from machine import ADC, Pin

def read_battery_level():
    battery_pin = 36
    adc = ADC(Pin(battery_pin))          # create ADC object on ADC pin
    adc.atten(ADC.ATTN_11DB)    # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
    adc.width(ADC.WIDTH_9BIT)   # set 9 bit return values (returned range 0-511)
    value = adc.read()                  # read value using the newly configured attenuation and width
    Pin(battery_pin, Pin.PULL_DOWN)
    return round((value * 3.6) / 511, 2) # Cannot read more than 3.6V (need to reduce voltage before)

