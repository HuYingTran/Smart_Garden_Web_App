import time
import board
import busio
import digitalio
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from f_sql import *

def thread_sensor():
    # Khởi tạo giao tiếp I2C và module ADS1115
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

    # Khởi tạo cảm biến DHT22 (Nhiệt độ, Độ ẩm)
    dht22 = adafruit_dht.DHT22(board.D4)

    # Khởi tạo các kênh đọc tín hiệu từ ADS1115
    mq135 = AnalogIn(ads, ADS.P0)          # MQ-135 trên kênh A0
    soil_moisture = AnalogIn(ads, ADS.P1)  # Cảm biến độ ẩm đất trên kênh A1

    # Khởi tạo cảm biến ánh sáng (GPIO 17)
    light_sensor = digitalio.DigitalInOut(board.D17)
    light_sensor.direction = digitalio.Direction.INPUT

    # Relay
    pump = digitalio.DigitalInOut(board.D26)
    pump.direction = digitalio.Direction.OUTPUT

    fan = digitalio.DigitalInOut(board.D19)
    fan.direction = digitalio.Direction.OUTPUT

    led = digitalio.DigitalInOut(board.D13)
    led.direction = digitalio.Direction.OUTPUT

    while True:
        try:
            # Đọc dữ liệu từ MQ-135 (Cảm biến khí)
            mq135_value = mq135.value
            mq135_voltage = mq135.voltage

            # Đọc dữ liệu từ cảm biến độ ẩm đất
            soil_value = soil_moisture.value
            soil_voltage = soil_moisture.voltage

            # Đọc dữ liệu từ DHT22 (Nhiệt độ & Độ ẩm không khí)
            temperature_c = dht22.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dht22.humidity

            # Đọc dữ liệu từ cảm biến ánh sáng (0 hoặc 1)
            light_status = light_sensor.value  # 0 = Tối, 1 = Sáng

            # In kết quả ra màn hình
            print(f"🌿 MQ135 - Raw: {mq135_value}, Voltage: {mq135_voltage:.3f}V")
            print(f"💧 Soil Moisture - Raw: {soil_value}, Voltage: {soil_voltage:.3f}V")
            print(f"🌡️ Temp: {temperature_c:.1f}ºC / {temperature_f:.1f}ºF, Humidity: {humidity:.1f}%")
            print(f"💡 Light Sensor: {'Sáng' if light_status else 'Tối'} (Value: {light_status})")
            print("-" * 40)

        except RuntimeError as error:
            # DHT22 có thể bị lỗi, bỏ qua nếu không đọc được
            print(f"⚠️ DHT22 Error: {error.args[0]}")
            time.sleep(2.0)
            continue
        except Exception as error:
            dht22.exit()
            raise error

        # Thêm dữ liệu và database sqlite
        insert_table_sensor("temp", temperature_c)
        insert_table_sensor("humi", humidity)
        insert_table_sensor("soil", soil_value)
        insert_table_sensor("co2", mq135_value)
        insert_table_sensor("light", light_status)

        # Chờ 60 giây trước khi đo lại
        time.sleep(2.0)

def controll_relay(object_t, status_t):
    if object_t == "pump":
        if status_t == "ON":
            pump.status = True
        else:
            pump.status = False
    elif object_t == "fan":
        if status_t == "ON":
            fan.status = True
        else:
            fan.status = False
    elif object_t == "led":
        if status_t == "ON":
            led.status = True
        else:
            led.status = False
