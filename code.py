from machine import Pin, I2C, RTC
import ssd1306
import utime

# ESP32 Pin assignment 
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Create RTC object
rtc = RTC()

# Đặt thời gian hiện tại (2024-04-02 15:30:00)
rtc.datetime((2024, 4, 2, 0, 15, 30, 0, 0))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

menu = 0

# Kết nối wifi
# WiFi setup
wifi_ssid = "YOUR_WIFI_SSID"
wifi_password = "YOUR_WIFI_PASSWORD"

# NTP server setup
ntp_server = "pool.ntp.org"
ntp_api = "http://worldtimeapi.org/api/timezone"

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("Connecting to WiFi...")
        wifi.connect(wifi_ssid, wifi_password)
        while not wifi.isconnected():
            pass
    print("WiFi connected:", wifi.ifconfig())

def get_current_time():
    connect_wifi()
    response = urequests.get(ntp_api)
    time_data = response.json()
    response.close()
    return time_data["unixtime"]

# Hiển thị giờ
def display_date(x, y):
    current_time = rtc.datetime()
    day_of_week = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")[current_time[3]]
    date_str = "{:02d}/{:02d}".format(current_time[2], current_time[1])
    time_str = "{:02d}:{:02d}:{:02d}".format(current_time[4], current_time[5], current_time[6])
    # Display time
    oled.text(time_str, x, y )
    # Display date
    oled.text(date_str, x, y + 10)
    # Display day of the week
    oled.text(day_of_week, x + 43, y + 10)
# Hiện pin
def display_battery(x, y):
    # Draw outer border of the battery icon (17x8)
    for i in range(x, x + 17):
        oled.pixel(i, y, 1)
        oled.pixel(i, y + 7, 1)
    oled.pixel(x-1,y+3,1)
    oled.pixel(x-1,y+4,1)
    for j in range(y + 1, y + 7):
        oled.pixel(x, j, 1)
        oled.pixel(x + 16, j, 1)

    # Draw three solid battery cells (4x8) inside the border
    for i in range(3):
        x_offset = x + 2 + i * 5
        for j in range(y + 2, y + 6):
            for k in range(x_offset, x_offset + 3):
                oled.pixel(k, j, 1)
# Cột sóng
# x và y là tọa độ x và y của cột sóng trên màn hình OLED.
# bars là số lượng thanh cột sóng cần hiển thị.
# bar_width là chiều rộng của mỗi thanh cột sóng.
# gap là khoảng cách giữa các thanh cột sóng.
def display_signal_strength(x, y, bars, bar_width, gap):
    # Draw signal strength bars
    for i in range(bars):
        bar_x = x + i * (bar_width + gap)
        bar_height = (i + 1)  # Tăng chiều cao dần
        for j in range(bar_height):
            for k in range(bar_width):
                oled.pixel(bar_x + k, y + bars - j, 1)


# Main loop
while True:
    if menu == 0:
        oled.fill(0)
        display_date(15,30)
        display_battery(110,0)
        display_signal_strength(5, 3, 4, 1, 1)
        # Show the display
        oled.show()    
        utime.sleep(1)
    
