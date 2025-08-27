import sensor, time, os, pyb, gc

# ตั้งค่ากล้อง
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# เปิดใช้งาน SD การ์ด
os.mount(pyb.SDCard(), "/sd")

# สร้างโฟลเดอร์ใน SD ถ้ายังไม่มี
folder = "/sd/images"
try:
    os.mkdir(folder)
except OSError:
    pass

img_counter = 0
for fname in os.listdir(folder):
    if fname.startswith("image_") and fname.endswith(".jpg"):
        try:
            num = int(fname[6:-4])
            if num >= img_counter:
                img_counter = num + 1
        except OSError:
            pass

print(img_counter)

# ตั้งค่า LED
led = pyb.LED(2)

while True:
    led.on()
    img = sensor.snapshot()

    filename = "%s/image_%03d.jpg" % (folder, img_counter)
    gc.collect()
    img.save(filename)
    print("Saved:", filename)

    img_counter += 1
    # led.off()
    time.sleep_ms(2000)
