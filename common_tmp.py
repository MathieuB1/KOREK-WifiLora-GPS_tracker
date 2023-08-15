# Screen Pins
# Heltec V2
SCL=15
SDA=4
RST_SCREEN=16


# LoRa Pins
# Heltec V2
PIN_ID_LORA_RESET = 14
PIN_ID_LORA_SS = 18
PIN_ID_SCK = 5
PIN_ID_MOSI = 27
PIN_ID_MISO = 19
PIN_ID_LORA_DIO0 = 26

# GPS acquisition settings
PRECISION=5

# Battery Alert
BATT=39
# Full Batt at 4.11V and at 3.35 V Heltec V2 cuts the power, drop discharge is comming at 3.55 V
MIN_BATTERY_LEVEL = 2.9 # With voltage reducer 10k 100k and battery 1000mAh

POSITIONS_FILE="locations.txt"

# Korek Tracking Web settings
