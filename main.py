# python3.6
import telebot
import random
import json
import pyodbc

import paho.mqtt.client as mqtt


broker = '10.91.13.222'
port = 1883
# topic = "tele/tasmota_462B25/SENSOR"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'vnptvlg'
password = 'vnptvlg'
# bot information
token = '5619717309:AAFaKhqzJKyJabl4AbHMEbnrbCI1Bna34RM'
chatID = -782522018
# database information
conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\\VNPT\\notification-via-telegram-with-mqtt\\THS.accdb;')

# Define event callbacks


def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))


def on_message(client, obj, msg):
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    data = json.loads(msg.payload)
    # print(data)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensors WHERE TasmotaName = ?", (str(msg.topic).split("/")[1]))
        for sensor in cursor.fetchall():
            notify = ''
            S = data[sensor[2]]
            STemp = float(S['Temperature'])  # Nhiệt độ từ cảm biến gởi lên
            SHum = float(S['Humidity'])      # Độ ẩm từ cảm biến gởi lên
            STTempMin = float(sensor[5])     # Ngưỡng nhiệt độ thấp từ DB
            STTempMax = float(sensor[6])     # Ngưỡng nhiệt độ cao từ DB
            STHumMin = float(sensor[7])      # Ngưỡng độ ẩm thấp từ DB
            STHumMax = float(sensor[8])      # Ngưỡng độ ẩm cao từ DB

            if(STemp >= STTempMax):
                notify += 'nóng '
            elif (STemp <= STTempMin):
                notify += 'lạnh '

            if (SHum >= STHumMax):
                notify += 'ẩm '
            elif (SHum <= STHumMin):
                notify += 'khô '

            sendMessage("<b>Cảnh báo</b>\nCảm biến {} tại {} đang {}hơn ngưỡng".format(sensor[3], sensor[4], notify))
    except Exception as e:
        print(e)
    # sensor = data['DHT11']

    # if(sensor['Temperature'] != None and sensor['Humidity'] != None):
    #     try:
    #         cursor = conn.cursor()
    #         cursor.execute(
    #             "SELECT * FROM sensors WHERE TasmotaName = ?", (str(msg.topic).split("/")[1]))

    #         for i in cursor.fetchall():
    #             if(float(sensor['Temperature']) >= float(i[4])):
    #                 sendMessage(
    #                     "<pre>Cảnh báo</pre>\nCảm biến <b>{}</b> tại <i>{}</i> vượt ngưỡng nhiệt độ.".format(i[2], i[3]))
    #     except Exception as e:
    #         print(e)


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
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM SENSORS')

    for i in cursor.fetchall():
        topic = "tele/"+str(i[1])+"/SENSOR"
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
