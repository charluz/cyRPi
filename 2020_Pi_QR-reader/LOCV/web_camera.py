# -*- coding: utf-8 -*-

import cv2
import threading
import time


# #--------------------------------------------------
# # 以下為 main() 使用
# #--------------------------------------------------
# '''
# if __name__ == "__main__":
# 	import sys, os
# 	sys.path.append(os.path.join("..", "face_recognition"))
# 	from face_utils import draw_box
# '''
# #--------------------------------------------------
# from cyFaceRecognition.face_utils import draw_box


#------------------------------------------------------------------------------
#-- Class: threading_VideoStream
#------------------------------------------------------------------------------
class threading_WebCamera:
	""" 用 python multi-threading 實現 Video Stream

	@param	src			設定使用的 Camera ID (0=/dev/video0, 1=/dev/video1, ...)
	@param	resolution	設定影像 size (Width, Height)
	@param	fps			Frame Rate
	"""
	def __init__(self, src=0, resolution=(640, 480), fps=30, name="mtWebCam", debug=False):
		# Initiate stream
		self.debug = debug

		self.stream = cv2.VideoCapture(src)
		self.Frame = []
		self.ready = False	#-- Camera Ready
		self.grabbed = False		# flag to tell is frame captured
		self.isstop = False  # flag to stop stream

		self.fps = fps
		self.frame_time = 1.0 / self.fps
		self.resolution = resolution

		# 設定擷取影像的尺寸大小
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

		if self.debug:
			self.camName = "{}{}".format(name, src)
			print("[{}] initiated.".format(self.camName))


	def start(self, waitReady=True):
		""" 啟動 threading web Camera
		"""
		# 把程式放進子執行緒，daemon=True 表示該執行緒會隨著主執行緒關閉而關閉。
		if self.debug:
			print("[{}] starting ...".format(self.camName))

		self.frame_lock = threading.Lock()
		self.last_time = time.time()
		threading.Thread(target=self.update, daemon=True, args=()).start()

		if waitReady:
			ready = False
			while not ready:
				ready, _ = self.read(blocking=False)
				# time.sleep(1)

		self.ready = True
		if self.debug:
			print("[{}] ready ...".format(self.camName))

		return self


	def stop(self):
		""" 結束 threading web camera
		"""
		# 記得要設計停止無限迴圈的開關。
		if self.debug:
			print("[{}] stopping...".format(self.camName))

		self.isstop = True

		if self.debug:
			print("[{}] stopped ...".format(self.camName))


	def read(self, blocking=True):
		""" 取回及時畫面
		"""
		if blocking:
			now = time.time()
			sleep_time = self.frame_time - (now - self.last_time)
			if sleep_time > 0.0:
				time.sleep(sleep_time)

		self.frame_lock.acquire()
		ret = self.grabbed, self.Frame
		self.frame_lock.release()

		self.last_timer = time.time()
		return ret



	def update(self):
		""" threading stream 主體，背景讀取當前影像到 buffer
		"""
		while (not self.isstop):
			self.grabbed, _frame = self.stream.read()
			if self.grabbed:
				self.frame_lock.acquire()
				self.Frame = _frame
				self.frame_lock.release()
				time.sleep(0.001)

		self.stream.release()





# #-------------------------------------------------
# # Main()
# #-------------------------------------------------
# def main():
# 	photoCam = threading_WebCamera(debug=True)

# 	photoCam.start()
# 	time.sleep(2)

# 	for i in range(10):
# 		_, frame = photoCam.read()
# 		rects = [ [(174+i*10, 134), (353, 313)], [(452+i*10, 272), (577, 397)] ]
# 		draw_box(frame, rects)
# 		cv2.imshow("frame", frame)
# 		cv2.waitKey(100)


# if __name__ == "__main__":
# 	main()
