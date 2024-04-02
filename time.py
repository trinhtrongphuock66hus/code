from machine import Pin, I2C
import ssd1306
import network
import utime
import ntptime
import _thread

# ESP32 Pin assignment 
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# WiFi credentials
wifi_ssid = "Wokwi-GUEST"
wifi_password = ""

# Khai báo và cấu hình các chân GPIO cho nút bấm
button_pin1 = Pin(16, Pin.IN, Pin.PULL_UP)  # Chân GPIO 16
button_pin2 = Pin(17, Pin.IN, Pin.PULL_UP)  # Chân GPIO 17
button_pin3 = Pin(18, Pin.IN, Pin.PULL_UP)  # Chân GPIO 18

# Biến khoá để đồng bộ hóa quá trình đọc nút bấm
button_lock = _thread.allocate_lock()

ntp_synced = False
initial_time = 0
menu = 0

def connect_wifi(ssid, password):
    global ntp_synced, initial_time
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('WiFi connected')
    print('IP address:', wlan.ifconfig()[0])
    
    # Lấy thời gian từ NTP server
    ntptime.settime()
    initial_time = utime.time()
    ntp_synced = True

def get_elapsed_time():
    global initial_time
    return utime.time() - initial_time

def get_datetime():
    try:
        if ntp_synced:
            elapsed_time = get_elapsed_time()
            gmt7_time = initial_time + 25200 + elapsed_time
            vietnam_time = utime.localtime(gmt7_time)
            return vietnam_time
    except Exception as e:
        print("Error fetching datetime:", e)
        return None


def display_datetime(x, y):
    datetime_obj = get_datetime()
    if datetime_obj:
        year, month, day, hour, minute, second, *_ = datetime_obj
        date_str = "{:02d}-{:02d}-{:02d}".format(day, month, year)
        time_str = "{}:{:02d}:{:02d}".format(hour, minute, second)
        oled.text("{}".format(date_str), x, y+10)
        oled.text("{}".format(time_str), x, y)
    else:
        oled.text("Failed to fetch", x, y)
        oled.text("datetime", x, y+20)

def display_wifi():
    wlan = network.WLAN(network.STA_IF)
    # Hiển thị thông tin về mạng WiFi A
    ssid_A = "Wokwi-GUEST"
    connected_A = "connected" if wlan.isconnected() and wlan.config("essid") == ssid_A else "disconnected"
    wifi_info_A = "{}:{}".format(ssid_A, connected_A)
    oled.text(wifi_info_A, 0, 30)
    
    # Hiển thị thông tin về mạng WiFi B
    ssid_B = "tuthuoc"
    connected_B = "connected" if wlan.isconnected() and wlan.config("essid") == ssid_B else "disconnected"
    wifi_info_B = "{}:{}".format(ssid_B, connected_B)
    oled.text(wifi_info_B, 0, 40)

def display_table():

    # Định nghĩa các giá trị cho bảng dữ liệu
    table_data = {
        "tu1": "12:30",
        "tu2": "13:45",
        "tu3": "15:00",
        "tu4": "16:15"
    }
    # Hiển thị thông tin từ bảng dữ liệu
    row_height = 10  # Độ cao của mỗi dòng
    y_position = 20  # Vị trí y ban đầu
    for key, value in table_data.items():
        table_info = "{}: {}".format(key, value)
        oled.text(table_info, 0, y_position)
        y_position += row_height

    
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

# Hàm xử lý sự kiện nút bấm
def button1_press_handler():
    global menu
    while True:
        button_lock.acquire()
        if button_pin1.value() == 0:
            menu += 1
            print("Menu:", menu)
        button_lock.release()
        utime.sleep_ms(100)  # Debouncing delay

def button2_press_handler():
    global menu
    while True:
        button_lock.acquire()
        if button_pin2.value() == 0:
            menu += 1
            print("Menu:", menu)
        button_lock.release()
        utime.sleep_ms(100)  # Debouncing delay

def button3_press_handler():
    global menu
    while True:
        button_lock.acquire()
        if button_pin3.value() == 0:
            menu -= 1
            print("Menu:", menu)
        button_lock.release()
        utime.sleep_ms(100)  # Debouncing delay

# Bắt đầu các luồng xử lý sự kiện nút bấm
_thread.start_new_thread(button1_press_handler, ())
_thread.start_new_thread(button2_press_handler, ())
_thread.start_new_thread(button3_press_handler, ())

connect_wifi(wifi_ssid, wifi_password)

while True:
    if menu == 0:
        oled.fill(0)
        display_datetime(15,30)
        display_battery(110,0)
        display_signal_strength(5, 3, 4, 1, 1)
        # Show the display
        oled.show()    
    elif menu == 1:
        oled.fill(0)
        display_wifi()
        display_battery(110,0)
        display_signal_strength(5, 3, 4, 1, 1)
        # Show the display
        oled.show()  
    elif menu == 2:
        oled.fill(0)
        display_table()
        display_battery(110,0)
        display_signal_strength(5, 3, 4, 1, 1)
        # Show the display
        oled.show()  
