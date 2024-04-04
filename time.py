from machine import Pin, I2C, RTC
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
wifi_password = "00"

# Khai báo và cấu hình các chân GPIO cho nút bấm
button_pin1 = Pin(16, Pin.IN, Pin.PULL_UP)  # Chân GPIO 16
button_pin2 = Pin(17, Pin.IN, Pin.PULL_UP)  # Chân GPIO 17
button_pin3 = Pin(18, Pin.IN, Pin.PULL_UP)  # Chân GPIO 18

# Biến khoá để đồng bộ hóa quá trình đọc nút bấm
button_lock = _thread.allocate_lock()

ntp_synced = False
initial_time = 0
menu = 0
editing_state = None
alert = True

minute_incremented = False
hour_incremented = False
day_incremented = False
month_incremented = False
year_incremented = False
year = 2024
month = 4
day = 3
hour = 12
minute = 30
second = 0
# Create RTC object
rtc = RTC()
rtc.datetime((year, month, day, 0, hour, minute, second, 0))

def connect_wifi(ssid, password):
    global ntp_synced, initial_time
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        start_time = utime.time()
        while not wlan.isconnected():
            if utime.time() - start_time > 5:  # Nếu quá 5 giây mà vẫn không kết nối được, thoát ra khỏi vòng lặp
                print("Failed to connect to WiFi after 5 seconds.")
                return
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
    global year, month, day, hour, minute, second, blink_counter, minute_incremented, hour_incremented, day_incremented, month_incremented, year_incremented
    datetime_obj = get_datetime()
    if datetime_obj:
        year, month, day, hour, minute, second, *_ = datetime_obj
        date_str = "{:02d}-{:02d}-{:02d}".format(day, month, year)
        time_str = "{}:{:02d}:{:02d}".format(hour, minute, second)
    else:
        current_time = rtc.datetime()
        # Sử dụng thời gian được thiết lập sẵn
        if current_time[6] == 0:
            if not minute_incremented:
                minute = (minute + 1) % 60
                minute_incremented = True
            elif current_time[6] == 30:
                minute_incremented = False
            if minute == 0 and not hour_incremented:
                hour = (hour + 1) % 24
                hour_incremented = True
            elif minute == 30:
                hour_incremented = False
            if hour == 0 and not day_incremented:
                # Kiểm tra xem ngày hiện tại có bao nhiêu ngày
                days_in_month = 31  # Gán mặc định là 31 ngày
                if month in [4, 6, 9, 11]:
                    days_in_month = 30
                elif month == 2:
                    days_in_month = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
                day = (day % days_in_month) + 1
                day_incremented = True
                if day == 1 and not month_incremented:
                    month = (month % 12) + 1
                    month_incremented = True
                    if month == 1 and not year_incremented:
                        year += 1
                        year_incremented = True
                    elif month == 6:
                        year_incremented = False
                elif day == 15:
                    month_incremented = False
            elif hour == 12:
                day_incremented = False

        date_str = "{:02d}-{:02d}-{:02d}".format(day, month, year)
        time_str = "{:02d}:{:02d}:{:02d}".format(hour, minute, current_time[6])
        if menu == 0 and editing_state == 'hour':
            if blink_counter % 2 == 0:
                time_str = time_str[:2] + '_' + time_str[3:]
        elif menu == 0 and editing_state == 'minute':
            if blink_counter % 2 == 0:
                time_str = time_str[:5] + '_' + time_str[6:]
        if menu == 0 and editing_state == 'day':
            if blink_counter % 2 == 0:
                date_str = date_str[:2] + '_' + date_str[3:]
        elif menu == 0 and editing_state == 'month':
            if blink_counter % 2 == 0:
                date_str = date_str[:5] + '_' + date_str[6:]
        elif menu == 0 and editing_state == 'year':
            if blink_counter % 2 == 0:
                date_str = date_str + '_'
    oled.text("{}".format(date_str), x, y+10)
    oled.text("{}".format(time_str), x, y)
    blink_counter += 1



def display_wifi():
    wlan = network.WLAN(network.STA_IF)
    # Hiển thị thông tin về mạng WiFi A
    ssid_A = "Wokwi-GUEST"
    connected_A = "connected" if wlan.isconnected() and wlan.config("essid") == ssid_A else "disconnected"
    wifi_info_A = "{}".format(ssid_A)
    wifi_info_A1 = "{}".format(connected_A)
    oled.text(wifi_info_A, 0, 20)
    oled.text(wifi_info_A1, 0, 30)

    
    # Hiển thị thông tin về mạng WiFi B
    ssid_B = "tuthuoc"
    connected_B = "connected" if wlan.isconnected() and wlan.config("essid") == ssid_B else "disconnected"
    wifi_info_B = "{}".format(ssid_B)
    wifi_info_B1 = "{}".format(connected_B)
    oled.text(wifi_info_B, 0, 40)
    oled.text(wifi_info_B1, 0, 50)

# Danh sách các tủ và thông tin giờ và thuốc của chúng
tu_list = ["tu1", "tu2", "tu3", "tu4"]
tu_hours = {"tu1": 12, "tu2": 13, "tu3": 15, "tu4": 16}
tu_minutes = {"tu1": 30, "tu2": 45, "tu3": 0, "tu4": 15}
tu_doses_per_day = {"tu1": 3, "tu2": 2, "tu3": 1, "tu4": 4}  # Số lượng thuốc cần uống mỗi ngày
tu_remaining_doses = {"tu1": 3, "tu2": 2, "tu3": 1, "tu4": 4}  # Số lượng thuốc còn lại trong tủ

# Hàm để cập nhật giá trị của từng tủ từ biến cố định thành biến có thể thay đổi
def update_tu_info(tu_name, new_hour, new_minute, new_doses_per_day, new_remaining_doses):
    global tu_hours, tu_minutes, tu_doses_per_day, tu_remaining_doses
    tu_hours[tu_name] = new_hour
    tu_minutes[tu_name] = new_minute
    tu_doses_per_day[tu_name] = new_doses_per_day
    tu_remaining_doses[tu_name] = new_remaining_doses

blink_counter = 0

# Hàm để hiển thị thông tin từng tủ trên màn hình
def display_table():
    global blink_counter
    # Hiển thị thông tin từ bảng dữ liệu
    row_height = 10  # Độ cao của mỗi dòng
    y_position = 20  # Vị trí y ban đầu
    for i, tu_name in enumerate(tu_list):
        hour = tu_hours[tu_name]
        minute = tu_minutes[tu_name]
        doses_per_day = tu_doses_per_day[tu_name]
        remaining_doses = tu_remaining_doses[tu_name]
        table_info = "{}: {:02d}:{:02d}-{}/{}".format(tu_name, hour, minute, doses_per_day, remaining_doses)
        # Kiểm tra nếu tủ này đang được chỉnh sửa và chế độ là 'hour'
        if tu_counter == i + 1 and editing_state == 'hour':
            # Tạo hiệu ứng nhấp nháy bằng biến đếm
            if blink_counter % 2 == 0:
                table_info = table_info[:6] + "_" + table_info[7:]
        # Kiểm tra nếu tủ này đang được chỉnh sửa và chế độ là 'minute'
        elif tu_counter == i + 1 and editing_state == 'minute':
            # Tạo hiệu ứng nhấp nháy bằng biến đếm
            if blink_counter % 2 == 0:
                table_info = table_info[:9] + "_" + table_info[10:]
        # Kiểm tra nếu tủ này đang được chỉnh sửa và chế độ là 'perday'
        elif tu_counter == i + 1 and editing_state == 'perday':
            # Tạo hiệu ứng nhấp nháy bằng biến đếm
            if blink_counter % 2 == 0:
                table_info = table_info[:-3] + "_" + table_info[-2:]
        # Kiểm tra nếu tủ này đang được chỉnh sửa và chế độ là 'remain'
        elif tu_counter == i + 1 and editing_state == 'remain':
            # Tạo hiệu ứng nhấp nháy bằng biến đếm
            if blink_counter % 2 == 0:
                table_info = table_info[:-1] + "_"
        oled.text(table_info, 0, y_position)
        y_position += row_height
    # Tăng biến đếm thời gian mỗi lần hiển thị bảng
    blink_counter += 1


def check_medication_time():
    global tu_list, tu_hours, tu_minutes, hour, minute, oled

    current_hour = hour
    current_minute = minute
    message = "Time to take "
    message1 = "medicine from"
    blink_counter = 0  # Biến đếm cho việc nhấp nháy
    display_duration = 5  # Thời gian hiển thị thông báo (giây)

    for tu in tu_list:
        if tu_hours[tu] == current_hour and tu_minutes[tu] == current_minute:
            message2 =  "{}".format(tu)
            start_time = utime.time()  # Thời gian bắt đầu hiển thị thông báo

            while utime.time() - start_time < display_duration:  # Hiển thị trong thời gian quy định
                oled.fill(0)
                # Hiển thị thông báo nếu biến đếm là số lẻ, ngược lại không hiển thị
                if blink_counter % 2 == 0:
                    oled.text(message, 0, 0)
                    oled.text(message1, 0, 10)
                    oled.text(message2, 0, 20)
                oled.show()
                utime.sleep(1)
                blink_counter += 1
            break  # Thoát khỏi vòng lặp sau khi hiển thị xong thông báo

def check_time():
    global tu_list, tu_hours, tu_minutes, hour, minute, alert
    current_hour = hour
    current_minute = minute + 1
    for tu in tu_list:
        if tu_hours[tu] == current_hour and tu_minutes[tu] == current_minute:
            alert = True
    
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

# Biến đếm để chỉnh sửa giờ của các tủ
tu_counter = 1

# Hàm xử lý sự kiện nút bấm
def button1_press_handler():
    global menu, editing_state, tu_counter, year, month, day, hour, minute
    while True:
        button_lock.acquire()
        if button_pin1.value() == 0:
            if editing_state is None:
                if menu < 2:
                    menu += 1
                else:
                    menu -= 2
                print("Menu:", menu)
            if menu == 2:
                # Tăng giờ hoặc phút tùy theo trạng thái chỉnh sửa hiện tại
                if editing_state == 'hour':
                    tu_name = tu_list[tu_counter - 1]
                    tu_hours[tu_name] = (tu_hours[tu_name] + 1) % 24
                elif editing_state == 'minute':
                    tu_name = tu_list[tu_counter - 1]
                    tu_minutes[tu_name] = (tu_minutes[tu_name] + 1) % 60
                elif editing_state == 'perday':
                    tu_name = tu_list[tu_counter - 1]
                    tu_doses_per_day[tu_name] = (tu_doses_per_day[tu_name] + 1) % 99
                elif editing_state == 'remain':
                    tu_name = tu_list[tu_counter - 1]
                    tu_remaining_doses[tu_name] = (tu_remaining_doses[tu_name] + 1) % 99
            # elif menu == 1:
            #     # if editing_state == 'conectwifi':
            elif menu == 0:
                if editing_state == 'hour':
                    hour = (hour + 1) % 24
                elif editing_state == 'minute':
                    minute = (minute + 1) % 60
                elif editing_state == 'day':
                    # Kiểm tra xem tháng hiện tại có bao nhiêu ngày
                    days_in_month = 31  # Gán mặc định là 31 ngày
                    if month in [4, 6, 9, 11]:
                        days_in_month = 30
                    elif month == 2:
                        days_in_month = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28

                    day = (day + 1) % (days_in_month + 1)  # Điều chỉnh ngày, nếu vượt quá số ngày trong tháng, quay lại ngày 1
                    if day == 0:  # Nếu vượt qua ngày cuối cùng của tháng, quay lại tháng 1
                        month = (month % 12) + 1
                        if month == 1:  # Nếu quay lại tháng 1, tăng năm lên 1
                            year += 1
                elif editing_state == 'month':
                    month = (month % 12) + 1
                elif editing_state == 'year':
                    year += 1

        button_lock.release()
        utime.sleep_ms(100)  # Debouncing delay

def button2_press_handler():
    global editing_state, tu_counter, alert, menu
    while True:
        button_lock.acquire()
        if button_pin2.value() == 0:
            if menu == 2:
                # Khi nhấn nút 2, chuyển đổi giữa chỉnh sửa giờ và chỉnh sửa phút
                if editing_state is None:
                    editing_state = 'hour'
                    print("Editing hour")
                elif editing_state == 'hour':
                    editing_state = 'minute'
                    print("Editing minute")
                elif editing_state == 'minute':
                    editing_state = 'perday'
                    print("Editing perday")
                elif editing_state == 'perday':
                    editing_state = 'remain'
                    print("Editing remain")
                elif editing_state == 'remain':
                    if tu_counter == 4:
                        editing_state = None
                        print("Close editing")
                        tu_counter -= 3
                    else:
                        editing_state = 'hour'
                        print("Editing hour")
                        tu_counter += 1
            if menu == 0:
                if editing_state is None:
                    editing_state = 'hour'
                    print("Editing hour")
                elif editing_state == 'hour':
                    editing_state = 'minute'
                    print("Editing minute")
                elif editing_state == 'minute':
                    editing_state = 'day'
                    print("Editing day")
                elif editing_state == 'day':
                    editing_state = 'month'
                    print("Editing month")
                elif editing_state == 'month':
                    editing_state = 'year'
                    print("Editing year")
                elif editing_state == 'year':
                    print("Close editing")
                    editing_state = None
            if menu == 1:
                if editing_state is None:
                    editing_state = 'connectwifi'
                    print("Connect wifi")
                if editing_state == 'conectwifi':
                    editing_state == None
                    print("Close connectwifi")
            if menu == 3:
                alert = False
                print("Close alert")
                menu -= 3
        button_lock.release()
        utime.sleep_ms(100)  # Debouncing delay

def button3_press_handler():
    global menu, editing_state, tu_counter
    while True:
        button_lock.acquire()
        if button_pin3.value() == 0:
            if editing_state is None:
                if menu > 0: 
                    menu -= 1
                else:
                    menu += 2
                print("Menu:", menu)
            if menu == 2:
                # Giảm giờ hoặc phút tùy theo trạng thái chỉnh sửa hiện tại
                if editing_state == 'hour':
                    tu_name = tu_list[tu_counter - 1]
                    tu_hours[tu_name] = (tu_hours[tu_name] - 1) % 24
                elif editing_state == 'minute':
                    tu_name = tu_list[tu_counter - 1]
                    tu_minutes[tu_name] = (tu_minutes[tu_name] - 1) % 60
                elif editing_state == 'perday':
                    tu_name = tu_list[tu_counter - 1]
                    tu_doses_per_day[tu_name] = (tu_doses_per_day[tu_name] - 1) % 99
                elif editing_state == 'remain':
                    tu_name = tu_list[tu_counter - 1]
                    tu_remaining_doses[tu_name] = (tu_remaining_doses[tu_name] - 1) % 99
            # elif menu == 1:
            #     if editing_state == 'conectwifi':

            elif menu == 0:
                if editing_state == 'hour':
                    hour = (hour - 1) % 24  # Sửa dấu cộng thành dấu trừ
                elif editing_state == 'minute':
                    minute = (minute - 1) % 60  # Sửa dấu cộng thành dấu trừ
                elif editing_state == 'day':
                    # Kiểm tra xem tháng hiện tại có bao nhiêu ngày
                    days_in_month = 31  # Gán mặc định là 31 ngày
                    if month in [4, 6, 9, 11]:
                        days_in_month = 30
                    elif month == 2:
                        days_in_month = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
                    day = (day - 1) % (days_in_month + 1)  # Sửa dấu cộng thành dấu trừ
                    if day == 0:  # Nếu vượt qua ngày cuối cùng của tháng, quay lại tháng 1
                        month = (month - 1) % 12  # Sửa dấu cộng thành dấu trừ
                        if month == 0:  # Nếu quay lại tháng 1, giảm năm đi 1
                            year -= 1  # Sửa dấu cộng thành dấu trừ
                elif editing_state == 'month':
                    month = (month - 1) % 12  # Sửa dấu cộng thành dấu trừ
                elif editing_state == 'year':
                    year -= 1  # Sửa dấu cộng thành dấu trừ


        button_lock.release()
        utime.sleep_ms(100)  # Debouncing delay

# Bắt đầu các luồng xử lý nút bấm
_thread.start_new_thread(button1_press_handler, ())
_thread.start_new_thread(button2_press_handler, ())
_thread.start_new_thread(button3_press_handler, ())


connect_wifi(wifi_ssid, wifi_password)

while True:
    check_time()
    if alert:
        if menu < 3:
            menu += 3
        check_medication_time()
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
