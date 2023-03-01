import telebot
import random
import json

import paho.mqtt.client as mqtt


# Read configurations
with open("settings.json", "r", encoding="utf8") as f:
    settings = json.loads(f)

broker = settings['broker']['ip']
port = settings['broker']['port']
# topic = "tele/tasmota_462B25/SENSOR"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = settings['broker']['username']
password = settings['broker']['password']
# bot information
token = settings['telegram']['token']
chatID = settings['telegram']['chat_id']

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))


def on_message(client, obj, msg):
    data = json.loads(msg.payload)
    try:
        cursor = mycol.find({'TasmotaName': (str(msg.topic).split("/")[1])})
        for sensor in cursor:
            notify = ''
            S = data['SI7021']
            STemp = float(S['Temperature'])                 # Nhiệt độ từ cảm biến gởi lên
            SHum = float(S['Humidity'])                     # Độ ẩm từ cảm biến gởi lên
            STTempMin = float(sensor['MinTempThresh'])      # Ngưỡng nhiệt độ thấp từ DB
            STTempMax = float(sensor['MaxTempThresh'])      # Ngưỡng nhiệt độ cao từ DB
            STHumMin = float(sensor['MinHumThresh'])        # Ngưỡng độ ẩm thấp từ DB
            STHumMax = float(sensor['MaxHumThresh'])        # Ngưỡng độ ẩm cao từ DB

            if(STemp >= STTempMax):
                notify += 'nóng '
            elif (STemp <= STTempMin):
                notify += 'lạnh '

            if (SHum >= STHumMax):
                notify += 'ẩm '
            elif (SHum <= STHumMin):
                notify += 'khô '

            if(notify != ''):
                mydb['logs'].insert_one(data)
                sendMessage("<b>CẢNH BÁO</b>\n{} tại {} đang {} hơn ngưỡng!!".format(sensor['SensorUName'], sensor['Location'], notify))
            # print("<b>CẢNH BÁO</b>\n{} tại {} đang {} hơn ngưỡng!!".format(sensor['SensorUName'], sensor['Location'], notify))
    except Exception as e:
        print(e)



def on_publish(client, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(client, obj, level, string):
    print(string)


def sendMessage(message):
    bot = telebot.TeleBot(token)
    try:
        bot.send_message(chatID, message, parse_mode="HTML")
    except Exception as e:
        print(e)


mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#mqttc.on_log = on_log


# Connect
mqttc.username_pw_set(username, password)
mqttc.connect(broker, port)

# Start subscribe, with QoS level 0
try:
    cursor = mycol.find()
    for i in cursor:
        topic = "tele/"+str(i['TasmotaName'])+"/SENSOR"
        mqttc.subscribe(topic, 0)
except Exception as e:
    print(e)

# Publish a message
# mqttc.publish(topic, "my message")

# Continue the network loop, exit when an error occurs
rc = 0
while rc == 0:
    rc = mqttc.loop()
print("rc: " + str(rc))
