from mqtt_as import MQTTClient, config, RP2
if RP2:
    from sys import implementation
from config import wifi_led, blue_led
import uasyncio as asyncio
import network

from sensor_data import SensorDATA
from OLED_2inch23 import OLED_2inch23

# MQTT Topic init
TOPIC = 'sensor_d'  # For demo publication and last will use same topic

# Sensor data class
sensors = SensorDATA()

# LCD Screen
lcd = OLED_2inch23()
lcd.fill(0x0000)
lcd.show()

def update_lcd():
    lcd.fill(0x0000)
    lcd.show()
    lcd.text('Temp:   ' + sensors.get_temp(),1,2,lcd.white)
    lcd.text('Press.: ' + '1078.00',1,12,lcd.white)
    lcd.text('Light:  ' + sensors.get_light(),1,22,lcd.white)
    lcd.show()

async def pulse():  # This demo pulses blue LED each time a subscribed msg arrives.
    blue_led(True)
    await asyncio.sleep(1)
    blue_led(False)

def sub_cb(topic, msg, retained):
    print(f'{msg.decode()}')
    sensors.parse_msg(msg.decode())
    #asyncio.create_task(pulse())
    update_lcd()

# The only way to measure RSSI is via scan(). Alas scan() blocks so the code
# causes the obvious uasyncio issues.
async def get_rssi():
    global rssi
    s = network.WLAN()
    ssid = config['ssid'].encode('UTF8')
    while True:
        try:
            rssi = [x[3] for x in s.scan() if x[0] == ssid][0]
        except IndexError:  # ssid not found.
            rssi = -199
        await asyncio.sleep(30)

async def wifi_han(state):
    global outages
    wifi_led(not state)  # Light LED when WiFi down
    if state:
        print('We are connected to broker.')
    else:
        #outages += 1
        print('WiFi or broker is down.')
    await asyncio.sleep(1)

async def conn_han(client):
    await client.subscribe('foo_topic', 1)

async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        return

    while True:
        await asyncio.sleep(2)
        await client.subscribe(TOPIC, 1)


# Define configuration
config['port'] = 1883
config['user'] = 'pico'
config['password'] = '@tlas'
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['will'] = (TOPIC, 'Goodbye cruel world!', False, 0)
config['clean'] = True


# Set up client. Enable optional debug statements.
MQTTClient.DEBUG = True
client = MQTTClient(config)

# Currently (Apr 22) this task causes connection periodically to be dropped on Arduino Nano Connect
# It does work on Pico W
if not RP2 or 'Pico W' in implementation._machine:
    asyncio.create_task(get_rssi())
try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    blue_led(True)
    asyncio.new_event_loop()

