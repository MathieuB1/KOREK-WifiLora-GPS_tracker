from machine import ADC, Pin

def read_battery_level():
    adc = ADC(Pin(36))          # create ADC object on ADC pin
    adc.atten(ADC.ATTN_11DB)    # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
    adc.width(ADC.WIDTH_9BIT)   # set 9 bit return values (returned range 0-511)
    value = adc.read()                  # read value using the newly configured attenuation and width
    return round((value * 3.6) / 511, 2)

