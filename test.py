import json

data = {'Time': '2022-09-06T07:46:06', 'SI7021-01': {'Temperature': 29.0, 'Humidity': 69.4, 'DewPoint': 22.8},
        'SI7021-03': {'Temperature': 14.4, 'Humidity': 100.0, 'DewPoint': 14.4}, 'ESP32': {'Temperature': 35.6}, 'TempUnit': 'C'}
SensorName = 'SI7021-01'
print(data[SensorName])