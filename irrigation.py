import time
import Adafruit_DHT
import spidev
import RPi.GPIO as GPIO

# ---------------- GPIO SETUP ----------------
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

# ---------------- DHT SENSOR ----------------
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# ---------------- SPI SETUP (MCP3008) ----------------
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_moisture(channel=0):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# ---------------- THRESHOLDS ----------------
MOISTURE_THRESHOLD = 600   # higher = drier (adjust based on calibration)
TEMP_THRESHOLD = 30        # degrees Celsius

# ---------------- MAIN LOOP ----------------
try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        moisture_value = read_moisture()

        print(f"Temp: {temperature}°C  |  Moisture: {moisture_value}")

        if temperature is not None:
            if moisture_value > MOISTURE_THRESHOLD and temperature > TEMP_THRESHOLD:
                print("Soil dry & hot → Pump ON")
                GPIO.output(RELAY_PIN, GPIO.HIGH)
            else:
                print("Conditions normal → Pump OFF")
                GPIO.output(RELAY_PIN, GPIO.LOW)
        else:
            print("Sensor read failed")

        time.sleep(5)

except KeyboardInterrupt:
    print("System stopped")

finally:
    GPIO.cleanup()
    spi.close()