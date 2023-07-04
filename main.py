import dht, ds18x20, time, onewire, ubinascii, machine, random
from machine import Pin, ADC
from umqttsimple import MQTTClient

# Adafrukt-info
CLIENT_ID = ubinascii.hexlify(machine.unique_id()) #To create an MQTT client, we need to get the PICOW unique ID
MQTT_BROKER = "io.adafruit.com" # MQTT broker IP address or DNS  
PORT = 1883
ADAFRUIT_USERNAME = "twero"
ADAFRUIT_PASSWORD = "aio_FtXu89rRKISPfUL3atROPlKwAE8P" 

#Feeds (topics)
topicCelsiusIn = b"twero/feeds/pico-w-dam.celsius-in" #inside measuring box, same sensor as humidity
topicCelsiusOut = b"twero/feeds/pico-w-dam.celsius-out" #outside..
topicHumidity = b"twero/feeds/pico-w-dam.humidity"
topicLight = b"twero/feeds/pico-w-dam.light"
topicEarthHum = b"twero/feeds/pico-w-dam.earth-humidity"
topicRainLevel = b"twero/feeds/pico-w-dam.rain"

#Non-implemented topics
topicWaterCels = b"twero/feeds/pico-w-dam"
topicBattery = b"twero/feeds/pico-w-dam"

# Set the led pin 
greenLed = Pin(2, Pin.OUT)
yellowLed = Pin(3, Pin.OUT)
redLed = Pin(4, Pin.OUT)
dhtSens = dht.DHT11(machine.Pin(16))     # DHT11 Constructor 
rainSens = ADC(Pin(26))
soilSens = ADC(Pin(27))
sunSens = ADC(Pin(28))
onBoardTemp = machine.ADC(4)  


min_moisture=19200
max_moisture=49300

readDelay = 0.5 # delay between readings

visibleTime = 0.2
measureTime = 5 # was 5
sleepTime = 600 #seconds 1 hour = 60 * 60 = 3600


#Reads humiditty and temperature and returns the valuem there of
def readHum(): 

    result = ""

    try:
        dhtSens.measure()
        temperature = dhtSens.temperature()
        humidity = dhtSens.humidity()
        result = "Temperature is {} degrees Celsius and Humidity is {}%".format(temperature, humidity)

    except OSError as e:
        redLed.toggle()
        time.sleep(visibleTime)
        redLed.toggle()
        result = 'Failed to read sensor.'
    return(temperature, humidity)
    
def readOnBoardTemp():
    try:
        conversion_factor = 3.3 / (65535)

        reading_times = 10
        count = 0
        readings = []

        while(count < reading_times):
            reading = onBoardTemp.read_u16() * conversion_factor
            readings.append(27 - (reading - 0.706)/0.001721)
            count += 1
            greenLed.toggle()
            time.sleep(1) 
            greenLed.toggle()
        summa = 0
        for double in readings:
            summa += double
        summa /= reading_times

        return summa
    except:
        return "error reading temperature"
#Reads photoresistor sensor-data. no idea how light level is calculated.
def readPhotosynt(): 

    result = ""

    try:
        light = sunSens.read_u16()
        darkness = round(light / 65535 * 100, 2)
        #Do something, like turning on some lights possibly
        result = "Darkness is {}%".format(darkness)
        
        #if darkness <= 1:

    except OSError as e:
        redLed.toggle()
        time.sleep(visibleTime)
        redLed.toggle()
        result = 'Failed to read sensor.'
    return(darkness)

#measures earth humidity
def readEarthHum():
    moisture = (max_moisture - soilSens.read_u16())*100/(max_moisture-min_moisture)
    #a = "moisture: " + "%.2f" % moisture +"% (adc: "+str(soilSens.read_u16())+")"
    return moisture

#30000 means its a little wet
#20000 means it's soaking
#10000 ???
#Some problem with adc measuring no matter if data pin is connected to it
def readRain():
    read_rain = rainSens.read_u16()
    return read_rain


#Publishes sensor data to adafruit
def publish_ada(topic, value):
    try:
        mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, PORT, ADAFRUIT_USERNAME, ADAFRUIT_PASSWORD, keepalive=60)
        mqttClient.connect()

        mqttClient.publish(topic, str(value).encode())
        last_publish = time.time()
        return 'Succesful publish'
    except OSError as e:
        print("Error: " + str(e))
        reset()

#resets pico w
def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()


#Yellow while meassuring turn it of while waiting for next measure
#Green while waiting or blinking for each measurement
yellowLed.value(1)
time.sleep(visibleTime)

#Reads humidity & temp and saves it into a sort of array, it could be 
#a tuple but it isn't that important to know in py as compared to other lang
humidity_temp = readHum()

#Part 1 shipment of dst11, temperature C
greenLed.toggle()
print("DHT temperature: ", humidity_temp[0])
print(publish_ada(topicCelsiusOut, humidity_temp[0]))
time.sleep(visibleTime)
greenLed.toggle()
time.sleep(measureTime)

#Part 2 shipment of dst11, humidity
greenLed.toggle()
print("DHT humidity: ", humidity_temp[1])
print(publish_ada(topicHumidity, humidity_temp[1]))
time.sleep(visibleTime)
greenLed.toggle()
time.sleep(measureTime)

#Reads photsynt (light level) which returns a string
greenLed.toggle()
lightVal = readPhotosynt()
print("Photosynth sensor: ", lightVal)
print(publish_ada(topicLight, lightVal))
time.sleep(visibleTime)
greenLed.toggle()
time.sleep(measureTime)

'''
#Reads on board MCP
greenLed.toggle()
onBoardTemp = readOnBoardTemp()
print("On board temp: ", onBoardTemp)
print(publish_ada(topicCelsiusIn, onBoardTemp))
time.sleep(visibleTime)
greenLed.toggle()
time.sleep(measureTime)
'''

#Reads earth humidity
greenLed.toggle()
earthHumidity = readEarthHum()
print("Earth humidity: ", earthHumidity)
print(publish_ada(topicEarthHum, earthHumidity))
time.sleep(visibleTime)
greenLed.toggle()
time.sleep(measureTime)

#Reads rain sensor
greenLed.toggle()
rainLevel = readRain()
print("Rain sensor value: ", rainLevel) 
print(publish_ada(topicRainLevel, rainLevel)) 
time.sleep(visibleTime)
greenLed.toggle()
time.sleep(measureTime)

yellowLed.value(0)
greenLed.toggle()
time.sleep(sleepTime)
greenLed.toggle() 

reset()


