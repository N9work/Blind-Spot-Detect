import sensor
import time
import ml
from ml.utils import NMS
import math
import image
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
min_confidence = 0.4
threshold_list = [(math.ceil(min_confidence * 255), 255)]
model = ml.Model("model.lite")
print(model)
colors = [
	(255, 0, 0),
	(0, 255, 0),
	(255, 255, 0),
	(0, 0, 255),
	(255, 0, 255),
	(0, 255, 255),
	(255, 255, 255),
]
def fomo_post_process(model, inputs, outputs):
	n, oh, ow, oc = model.output_shape[0]
	nms = NMS(ow, oh, inputs[0].roi)
	for i in range(oc):
		img = image.Image(outputs[0][0, :, :, i] * 255)
		blobs = img.find_blobs(
			threshold_list, x_stride=1, area_threshold=1, pixels_threshold=1
		)
		for b in blobs:
			rect = b.rect()
			x, y, w, h = rect
			score = (
				img.get_statistics(thresholds=threshold_list, roi=rect).l_mean() / 255.0
			)
			nms.add_bounding_box(x, y, x + w, y + h, score, i)
	return nms.get_bounding_boxes()
clock = time.clock()
while True:
	clock.tick()
	img = sensor.snapshot()
	for i, detection_list in enumerate(model.predict([img], callback=fomo_post_process)):
		if i == 0:
			continue
		if len(detection_list) == 0:
			continue
		#print("********** %s **********" % model.labels[i])
		for (x, y, w, h), score in detection_list:
			center_x = math.floor(x + (w / 2))
			center_y = math.floor(y + (h / 2))
			print(f"x {center_x}\ty {center_y}\tscore {score}")
			img.draw_circle((center_x, center_y, 12), color=colors[i])
	print(clock.fps(), "fps", end="\n")
