from machine import Pin, I2C
import ssd1306

# ESP32 Pin assignment 
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Mảng bitmap của Pokemon2
pokemon1_bitmap = [
0x00, 0x00, 0x00, 0xfe, 0x00, 0x7e, 0x18, 0xfe, 0x18, 0x9c, 0x10, 0x0c, 0x00, 0x0e, 0x00, 0xc0, 
0x02, 0xc0, 0x00, 0xc8, 0x07, 0xc0, 0x47, 0xc0, 0x06, 0x20, 0x04, 0x40, 0x0c, 0x30, 0x08, 0x00, 
0x00, 0x00
]
# Hàm chuyển đổi màu trong mảng bitmap
def convert_color(bitmap):
    converted_bitmap = bytearray(len(bitmap))
    for i in range(len(bitmap)):
        # Chuyển màu trắng thành màu đen và ngược lại
        converted_bitmap[i] = ~bitmap[i] & 0xFF
    return converted_bitmap

# Mảng bitmap mới sau khi chuyển đổi màu
pokemon2_bitmap = convert_color(pokemon1_bitmap)

# Hàm vẽ bitmap lên màn hình OLED
def draw_bitmap(bitmap, x, y, width, height):
    for yi in range(height):
        for xi in range(width):
            # Lấy giá trị pixel tương ứng từ mảng bitmap
            pixel_index = (yi * (width // 8)) + (xi // 8)
            pixel_shift = 7 - (xi % 8)
            pixel_value = (bitmap[pixel_index] >> pixel_shift) & 0x01
            
            # Vẽ pixel
            if pixel_value:
                oled.pixel(x + xi, y + yi, 1) # 1: White
            else:
                oled.pixel(x + xi, y + yi, 0) # 0: Black

# Xóa màn hình
oled.fill(0)
oled.show()

# Hiển thị bitmap của Pokemon2 từ vị trí (0, 0) trên màn hình
draw_bitmap(pokemon2_bitmap, 0, 0, 16, 17)

# Cập nhật màn hình OLED để hiển thị bitmap
oled.show()
