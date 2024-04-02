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

def display_date(x, y):
    current_time = rtc.datetime()
    date_str = "{:02d}-{:02d}-{:04d}".format(current_time[2], current_time[1], current_time[0])
    time_str = "{:02d}:{:02d}:{:02d}".format(current_time[4], current_time[5], current_time[6])
    oled.text(date_str, x, y)
    oled.text(time_str, x, y+10)

def display_battery(x, y):
    # Draw outer border of the battery icon (17x10)
    for i in range(x, x + 18):
        oled.pixel(i, y, 1)
        oled.pixel(i, y + 9, 1)
    for j in range(y + 1, y + 9):
        oled.pixel(x, j, 1)
        oled.pixel(x + 17, j, 1)

    # Draw three solid battery cells (4x8) inside the border
    for i in range(3):
        x_offset = x + 2 + i * 5
        for j in range(y + 2, y + 8):
            for k in range(x_offset, x_offset + 4):
                oled.pixel(k, j, 1)

def display_signal_strength(x, y, bars, bar_width, max_bar_height, gap):
    # Draw signal strength bars
    for i in range(bars):
        bar_x = x + i * (bar_width + gap)
        bar_height = (i + 1) * max_bar_height // bars  # Tăng chiều cao dần
        for j in range(bar_height):
            for k in range(bar_width):
                oled.pixel(bar_x + k, y + j, 1)

# Main loop
while True:
    oled.fill(0)
    display_date(10,10)
    display_battery(110,0)
    display_signal_strength(5, 3, 3, 1, 3, 1)
    # Show the display
    oled.show()
    utime.sleep(1)
