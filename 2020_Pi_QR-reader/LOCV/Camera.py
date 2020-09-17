# -*- coding: utf-8 -*-

import cv2
import threading
import time

import sys, os

#--------------------------------------------------
# 以下為 main() 使用
#--------------------------------------------------
'''
if __name__ == "__main__":
	sys.path.append(os.path.join("..", "cyVisionToolbox"))
	from cy_imutils import (cv2_resize, cv2_draw_rectangles)
'''
#--------------------------------------------------

from cyCamera.web_camera import threading_WebCamera as WebCamera
from cyCamera.photo_camera	import threading_photoCamera as PhotoCamera



#------------------------------------------------------------------------------
#-- Class: threading_VideoStream
#------------------------------------------------------------------------------
class threading_VideoStream:
	""" 用 python multi-threading 實現 Video Stream

	@param	camera		設定 video stream 來源:
							"webCam"(default), "rpiCam", "url",
							"photo", "video"
	@param	camid		當 camera=="webCam"時，用來設定使用的 Camera ID (0=/dev/video0, 1=/dev/video1, ...)
	@param	images		A LIST，當 camera=="photo"時，設定一組 (LIST) 圖片當做 Video Stream 輸出。
	@param	clip		A video clip file，當 camera=="video"時，指定一個 video clip 檔案當做 Video Stream 輸出。

	@param	size		A tuple (width, height)，設定 Stream 輸出大小。
	@param	fps			設定輸出的 frame rate (integer)
	"""
	def __init__(self, camera="webCam", camid=0, images=None, clip="",
						size=(640, 480), fps=30, name="VS", debug=False):

		self.name = name
		self.debug = debug

		# Initiate stream
		if camera == "photo":
			if images is None:
				print("[{}] Error, images is None !!".format(self.name))
				return
			self.stream = PhotoCamera(images, resolution=size, fps=fps, debug=self.debug)
		else:
			# -- camera == "webCam":
			self.stream = WebCamera(src=camid, debug=self.debug)


	def start(self):
		""" 啟動 threading web Camera
		"""
		# 把程式放進子執行緒，daemon=True 表示該執行緒會隨著主執行緒關閉而關閉。

		self.stream.start()		# return self.stream.start() ???
		return self


	def stop(self):
		""" 結束 threading web camera
		"""
		# 記得要設計停止無限迴圈的開關。
		self.stream.stop()


	def read(self):
		""" 取回及時畫面
		"""
		# 當有需要影像時，再回傳最新的影像。
		status, frame = self.stream.read()
		return status, frame


	def update(self):
		""" 強制重新讀取當前影像到 buffer
		"""
		self.stream.update()



#-------------------------------------------------
# Main()
#-------------------------------------------------
def main():
	#--- photoCamera
	# def __init__(self, camera="webCam", camid=0, images=None, clip="", size=(640, 480), name="VS, debug=False):
	testImagesPath = os.path.join("..", "_TESTSET", "camera")
	imfiles = [os.path.join(testImagesPath, "images-1.jpg")]
	images = []
	for imfile in imfiles:
		image = cv2.imread(imfile)
		# cv2.imshow(imfile, image)
		images.append(image)
		# cv2.waitKey(0)

	# print(images)

	photoCam = threading_VideoStream(camera="photo", images=images, debug=True)

	photoCam.start()

	for i in range(2):
		frame = photoCam.read()
		rects = [[(174+i*10, 134), (353, 313)], [(452+i*10, 272), (577, 397)]]
		cv2_draw_rectangles(frame, rects)
		cv2.imshow("frame-{}".format(i), frame)
		cv2.waitKey(1000)

	photoCam.stop()

	cv2.destroyAllWindows()
	time.sleep(2)

	photoCam.start()
	for i in range(2):
		frame = photoCam.read()
		rects = [[(0, 134), (353, 313)], [(452-i*10, 272), (577, 397)]]
		cv2_draw_rectangles(frame, rects, color=(0, 255, 0))
		cv2.imshow("frame-{}".format(i), frame)
		cv2.waitKey(1000)


if __name__ == "__main__":
	main()
