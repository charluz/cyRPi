import cv2
import numpy as np
from threading import Thread, Lock
import time
import sys, os
import gc
import picamera
import utils

CAMERA_CV2 = 0
CAMERA_PICAMERA = 1

class piGrabber(Thread):
	"""A threaded video grabber.
	Attributes:
	encode_params ():
	cap (str):
	attr2 (:obj:`int`, optional): Description of `attr2`.
	"""
	global CAMERA_CV2, CAMERA_PICAMERA
	def __init__(self, width=640, height=480, frame_rate=30, jpeg_quality=70, jpeg_lib='cv2'):
		"""Constructor.
		Args:
		jpeg_quality (:obj:`int`): Quality of JPEG encoding, in 0, 100.
		"""
		# global CAMERA_CV2, CAMERA_PICAMERA
		Thread.__init__(self)
		self.width	= width
		self.height	= height
		self.fps = frame_rate

		self.camera = picamera.PiCamera(framerate=self.fps, sensor_mode=4)
		self.camera.resolution = (self.width, self.height)
		self.camera.framerate = self.fps
		time.sleep(2)
		#self.camera.start_preview()
		self.numpy_array = np.empty((self.width * self.height * 3,), dtype=np.uint8)

		self.frame_index = 0
		self.running = True
		self.jpeg_image = None
		self.lock = Lock()

		self.jpeg_quality = jpeg_quality
		self.jpeg_encode_func = lambda img, jpeg_quality=self.jpeg_quality: utils.cv2_encode_image(img, jpeg_quality)


	def capture_cv2(self):
		self.camera.capture(self.numpy_array, 'bgr', use_video_port=True)
		self.image = self.numpy_array.reshape((self.height, self.width, 3))
		return self.image


	def set_quality(self, quality):
		self.jpeg_quality = quality


	def set_manual_ae(self, iso, shutter):
		# Set ISO to the desired value
		self.camera.iso = iso
		self.camera.shutter_speed = shutter
		self.camera.exposure_mode = 'off'
		# g = camera.awb_gains
		# camera.awb_mode = 'off'
		# camera.awb_gains = g

	def set_auto_ae(self):
		self.camera.exposure_mode = 'auto'

	def stop(self):
		self.running = False


	def get_jpeg_image(self):
		"""Method to access the encoded buffer.
			Returns:
			np.ndarray: the compressed image if one has been acquired. None otherwise.
		"""
		if self.jpeg_image is None:
			return None

		self.lock.acquire()
		_img = self.jpeg_image	#-- 原始大小 image
		self.lock.release()
		return _img


	def run(self):
		while True:
			# print("++x++")
			img = self.capture_cv2() #--

			#--- Force Garbage collection
			#gc.collect()

			# JPEG compression
			# Protected by a lock
			# As the main thread may asks to access the buffer
			self.lock.acquire()
			self.jpeg_image = self.jpeg_encode_func(img, self.jpeg_quality)
			self.frame_index += 1
			self.lock.release()

		print("exiting grabber thread ...")
