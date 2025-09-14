import sensor
import time
import ml
import math
import image
import network
import usocket
from ml.utils import NMS

# ===== CONFIG =====
SSID = "ESP32_AP"
KEY = "12345678"
ESP_IP = "192.168.4.1"  # IP ของ ESP32 AP
PORT = 5005

MIN_CONFIDENCE = 0.5
threshold_list = [(math.ceil(MIN_CONFIDENCE*255), 255)]
COLOR = 255
SEND_INTERVAL = 200  # ms, ส่งซ้ำขณะ detect

# ===== WiFi Connect ก่อนโหลดโมเดล =====
print("Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    time.sleep_ms(500)
print("WiFi connected:", wlan.ifconfig())

# UDP Socket
sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)

# แจ้ง ESP32 ว่ามี client เชื่อมต่อแล้ว
sock.sendto(b"HELLO", (ESP_IP, PORT))

# ===== Camera Init =====
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# ===== Load Model =====
model = ml.Model("model.lite")
print("Model Loaded:", model)

# ===== Post Process FOMO =====
def fomo_post_process(model, inputs, outputs):
    n, oh, ow, oc = model.output_shape[0]
    nms = NMS(ow, oh, inputs[0].roi)
    for i in range(oc):
        if i == 0:  # skip background
            continue
        img_mask = image.Image(outputs[0][0, :, :, i] * 255)
        blobs = img_mask.find_blobs(
            threshold_list, x_stride=1, area_threshold=1, pixels_threshold=1
        )
        for b in blobs:
            x, y, w, h = b.rect()
            score = img_mask.get_statistics(thresholds=threshold_list, roi=b.rect()).l_mean() / 255.0
            if score >= MIN_CONFIDENCE:
                nms.add_bounding_box(x, y, x + w, y + h, score, i)
    return nms.get_bounding_boxes()

# ===== Main Loop =====
clock = time.clock()
last_send_time = time.ticks_ms()

while True:
    clock.tick()
    img = sensor.snapshot()

    detected = False

    for i, detection_list in enumerate(model.predict([img], callback=fomo_post_process)):
        if i == 0:
            continue
        for (x, y, w, h), score in detection_list:
            center = (x + w//2, y + h//2)
            img.draw_circle((center[0], center[1], 12), color=COLOR)
            print(f"x {center[0]} y {center[1]} score {score:.2f} vehicle detected")
            detected = True

    # ส่ง UDP เฉพาะตอน detect
    now = time.ticks_ms()
    if detected and time.ticks_diff(now, last_send_time) > SEND_INTERVAL:
        sock.sendto(b"CAR_DETECTED", (ESP_IP, PORT))
        last_send_time = now

    print(clock.fps(), "fps")
