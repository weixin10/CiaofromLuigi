''' The code for connecting to WiFi, callback functions and initialising the MQTT Client is adapted from https://learn.adafruit.com/quickstart-rp2040-pico-with-wifi-and-circuitpython/usage-with-adafruit-io'''

import time
import board
import busio
import digitalio
import analogio
import random
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT
import adafruit_dht

# List of daily motivational quotes
quotes = [
    "Believe you can and you're halfway there.",
    "The only way to do great work is to love what you do.",
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "Don't watch the clock; do what it does. Keep going.",
    "Tough times don't last, only tough people do",
]

#List of quotes when moisture level is low
hungryquotes=[
    "I am starving! Where is the food? 💧",
    "Italy will always have the best food. Now feed me, please!💧",
    "Life is a combination of magic and pasta. But since I am a plant, it is water. Please feed me!💧",
]

#Initialise LEDs, pump and sensors
ledR = digitalio.DigitalInOut(board.D5)
ledR.direction = digitalio.Direction.OUTPUT
ledG = digitalio.DigitalInOut(board.D6)
ledG.direction = digitalio.Direction.OUTPUT

pump = digitalio.DigitalInOut(board.D2)
pump.switch_to_output()

dht=adafruit_dht.DHT11(board.D7)
moisture = analogio.AnalogIn(board.A1)

# Initialise global variables
checked=False
watered=False
thankyoucount=0
quotecount=0
prv_refresh_time = 0.0
j=0

# Set thresholds
moist_threshold=20000
temp_threshold=30
humid_threshold=10

### WiFi ###

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Raspberry Pi RP2040
esp32_cs = digitalio.DigitalInOut(board.CS1)
esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")

# Obtain raw value from analog pin
def get_voltage(pin):
    return pin.value

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    print("Connected to Adafruit IO! ")

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")

def on_pump_msg(client, topic, message):
    # Method called whenever pump feed has a new value
    print("New message on topic {0}: {1} ".format(topic, message))
    if message == "ON":
        pump.value = True
    elif message == "OFF":
        pump.value = False
    else:
        print("Unexpected message on pump feed.")

# Turn on red LED when moisture level is low, otherwise turn on green LED
def led_control(moist):
    if moist<moist_threshold:
        ledR.value=True
        ledG.value=False
    else:
        ledG.value=True
        ledR.value=False

# Send message when temperature greater than set threshold
def handle_temp(temperature):
    if temperature>temp_threshold:
        io.publish("message", 'I am hotter than a chilli🌶️ Please put me somewhere colder!')

# Send message when humidity lower than set threshold
def handle_humid(humidity):
    if humidity<humid_threshold:
        io.publish("message", 'It needs to be humid like a pizzaria🍕, please put me somewhere humid or water me!')

# Initialize MQTT interface with the esp interface
MQTT.set_socket(socket, esp)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# Connect the callback methods defined above to Adafruit IO
io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe

# Set up a callback for the pump feed
io.add_feed_callback("pump", on_pump_msg)

# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()

# Subscribe to all messages on the pump feed
io.subscribe("pump")

while True:
    # Poll for incoming messages
    try:
        io.loop()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        wifi.connect()
        io.reconnect()
        continue

    # Send a new temperature, moisture and humidity reading to IO every 1 hr
    if (time.monotonic() - prv_refresh_time) > 3600 and not checked:

        # Reset global variables
        watered=False
        thankyoucount=0
        quotecount=0

        # Read temperature, moisture and humidity values
        moist=moisture.value
        temperature = dht.temperature
        humidity = dht.humidity

        # Publish readings
        io.publish("moisture", moist)
        io.publish("environment-temperature", temperature)
        io.publish("humidity", humidity)
        print("Published!")

        led_control(moist)
        handle_humid(humidity)
        handle_temp(temperature)

        j+=1
        if j%24==0 and quotecount==0:
            quote = random.choice(quotes)
            io.publish("message", quote)
            quotecount+=1
        if moist<moist_threshold:
            checked = True
        else:
            checked = False

    # Send reminder to water to IO every 10 min
    if (time.monotonic() - prv_refresh_time) > 600 and checked and not watered and moist<moist_threshold:
        hungryquote = random.choice(hungryquotes)
        io.publish("message", hungryquote)
        prv_refresh_time = time.monotonic()

    # Send thank you message to IO
    if pump.value==True and thankyoucount==0 and moist<moist_threshold:
        io.publish("message", 'Grazie!😙👌')
        thankyoucount+=1
        watered=True
    checked=False
