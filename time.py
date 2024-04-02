from machine import Pin, I2C
import ssd1306
import network
import utime
import ntptime

# ESP32 Pin assignment 
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# WiFi credentials
wifi_ssid = "Wokwi-GUEST"
wifi_password = ""

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('WiFi connected')
    print('IP address:', wlan.ifconfig()[0])

def get_datetime():
    try:
        # Sử dụng ntptime để lấy thời gian từ NTP server
        ntptime.settime()
        # Lấy thời gian UTC
        utc_time = utime.localtime()
        # Thêm 7 giờ (25200 giây) cho múi giờ GMT+7
        gmt7_time = utime.mktime(utc_time) + 25200
        # Chuyển đổi thời gian sang múi giờ GMT+7
        vietnam_time = utime.localtime(gmt7_time)
        return vietnam_time
    except Exception as e:
        print("Error fetching datetime:", e)
        return None


def display_datetime():
    datetime_obj = get_datetime()
    if datetime_obj:
        year, month, day, hour, minute, second, *_ = datetime_obj
        date_str = "{}-{:02d}-{:02d}".format(year, month, day)
        time_str = "{}:{:02d}:{:02d}".format(hour, minute, second)
        oled.fill(0)
        oled.text("Date: {}".format(date_str), 0, 0)
        oled.text("Time: {}".format(time_str), 0, 20)
        oled.show()
    else:
        oled.fill(0)
        oled.text("Failed to fetch", 0, 0)
        oled.text("datetime", 0, 20)
        oled.show()


connect_wifi(wifi_ssid, wifi_password)

while True:
    display_datetime()
    utime.sleep(10)  # Refresh datetime every 10 seconds
