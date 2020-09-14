# -*- encoding: utf-8 -*-

import os, sys
import numpy as np
import cv2, time
import tkinter as TK
import threading
from threading import Lock
from queue import Queue

from pygame import mixer

DEBUG = False
MAIN_WN_WIDTH = 640
MAIN_WN_HEIGHT = 480

USE_THREADING_CAMERA = True


if USE_THREADING_CAMERA == True:
	from web_camera import threading_WebCamera as VideoStream


if True:
	#---- For cy_ViPanel.py development
	from cy_ViPanel import tkViPanel
	#from cy_ViPanel import tkMessagePanel
	from cy_ViPanel import tkH2Frame, tkV2Frame, tkV3Frame
	#import cy_ViPanel as ViDISP
else:
	#---- Use site-packages modules
	from cyTkGUI.cy_ViPanel import tkViPanel
	from cyTkGUI.cy_ViPanel import tkMessagePanel
	from cyTkGUI.cy_ViPanel import tkH2Frame, tkV2Frame #, tkRadioButton
	import cyTkGUI.cy_ViPanel as ViDISP



#----------------------------------------------------------------------
# Main GUI
#----------------------------------------------------------------------
class MainGUI:
	"""
	"""
	def __init__(self):
		self.thread = threading.Thread(target=self.Tk_mainloop, daemon=True, args=())
		self.liveview = False

	def Tk_mainloop(self):
		self.root = TK.Tk()

		#-- Create Top-Bottom frames
		self.TB = tkV2Frame(self.root).Frames

		#---------------------------------
		# Decoded result frames
		#---------------------------------
		#-- Use Upper frame for decoded QR code, and rectified image display
		self.resultFrames = tkH2Frame(self.TB[0]).Frames
		self.boxQRView = tkViPanel(self.resultFrames[0], osdEn=False, size=(160, 160))
		
		self.textFrames = tkV2Frame(self.resultFrames[1]).Frames
		
		self.labelTime = TK.Label(self.textFrames[0], width=12, text="Time Used: ")
		self.labelTime.pack(side=TK.LEFT, fill=TK.Y)
		self.textTime = TK.StringVar()
		TK.Entry(self.textFrames[0], width=42, textvariable=self.textTime).pack(expand=TK.YES)
		"""
		self.labelSize = TK.Label(self.textFrames[1], width=12, text="QR Size: ")
		self.labelSize.pack(side=TK.LEFT, fill=TK.Y)
		self.textSize = TK.StringVar()
		TK.Entry(self.textFrames[1], width=42, textvariable=self.textSize).pack(expand=TK.YES)
		"""
		
		self.labelCode = TK.Label(self.textFrames[1], width=12, text="QR Code: ")
		self.labelCode.pack(side=TK.LEFT, fill=TK.Y)
		self.textCode = TK.StringVar()
		TK.Entry(self.textFrames[1], width=42, textvariable=self.textCode).pack(expand=TK.YES)

		#---------------------------------
		# Video Panel
		#---------------------------------
		self.View = tkViPanel(self.TB[1], osdEn=False, size=(MAIN_WN_WIDTH, MAIN_WN_HEIGHT))	# (720, 540), (960, 720)

		self.root.mainloop()



#---------------------------------------------------------
# Main Entry
#---------------------------------------------------------

def onClose():
	global evAckClose, evStopQR
	evAckClose.set()
	evStopQR.set()



def setup_capture(width=640, height=480):
	"""Sets up the video capture device.

	Returns the video capture instance on success and None on failure.

	Arguments:
		width: Width of frames to capture.
		height: Height of frames to capture.
	"""
	
	if USE_THREADING_CAMERA:
		capture = VideoStream().start()
	else:
		capture = cv2.VideoCapture(0)
		
		
	if not capture.isOpened():
		#print("Could not open video device!")
		return None

	if USE_THREADING_CAMERA == False:
		capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
		capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
		capture.set(cv2.CAP_PROP_EXPOSURE, -10)
		capture.set(cv2.CAP_PROP_GAIN, 4.0)

	return capture


# Display barcode and QR code location
def draw_bbox(im, bbox):
	n = len(bbox)
	for j in range(n):
		cv2.line(im, tuple(bbox[j][0]), tuple(bbox[ (j+1) % n][0]), (255,0,0), 3)
	return im

"""----- Create Camera vStream --------------------------
"""
"""
if True:
	vStream = VideoStream(camera="wbCam", camid=0, debug=False).start()
	time.sleep(1)
else:
	imfiles = ["charles_001.jpg"]
	images = [cv2.imread(imfile) for imfile in imfiles]
	vStream = VideoStream(camera="photo", images=images).start()
"""


""" ----- Initiate Main GUI ------------------------------
"""
evAckClose = threading.Event()
evAckClose.clear()
mainGUI = MainGUI()
mainGUI.thread.start()
time.sleep(0.5)
mainGUI.root.geometry("+640+200")

mainGUI.root.wm_protocol("WM_DELETE_WINDOW", onClose)


# Open Camera 
capture = setup_capture(MAIN_WN_WIDTH, MAIN_WN_HEIGHT)
if capture is None:
	print("ERROR: Could not open video device!")
	sys.exit()

# Create a qrCodeDetector Object
qrDecoder = cv2.QRCodeDetector()


scanState = "HUNTING"	#-- "LOCKED", "ESCAPING"
ESCAPE_THRESOLD = 20
escape_count = 0
lastCodeSZ=""
lockedCodeSZ=""
timeSZ=""

mp3Beep = "./beep.mp3"
mp3Beep2 = "./beep-beep.mp3"

lockedTime = time.time()

"""----- Beep-Beep -------------------------------
"""
mixer.init()
mixer.music.load("./beep-beep.mp3")

"""----- QR Decode thread ------------------------
https://www.pythonforthelab.com/blog/handling-and-sharing-data-between-threads/
https://blog.gtwang.org/programming/python-threading-multithreaded-programming-tutorial/
"""
evStopQR = threading.Event()
evStopQR.clear()

qr_lock = Lock()
queue_in = Queue()
while not queue_in.empty():
	tt = queue_in.get()
	
queue_out = Queue()
while not queue_out.empty():
	tt = queue_out.get()

qrSrcImg = None
qrData = ""
qrBbox = None
qrRectifiedImage = None
qrBusy = False
def QR_Decoder_Thread(queue_in, queue_out):
	busy = False
		
	while True:
		if evStopQR.isSet():
			break
			
		with qr_lock:
			if not queue_in.empty():
				srcImg = queue_in.get()
				busy = True
		
		#--- do QR detect and decode
		if busy:
			if DEBUG: 
				print("QR: Busy ---".format(busy))
				
			t = time.time()
			data,bbox,rectifiedImage = qrDecoder.detectAndDecode(srcImg)
			timeSZ = "{:.3f} sec".format(time.time() - t)
			if DEBUG:
				print("QR: timeSZ={}".format(timeSZ))

			with qr_lock:
				busy = False
				queue_out.put(data)
				queue_out.put(bbox)
				queue_out.put(rectifiedImage)
				queue_out.put(timeSZ)
				
				if DEBUG:
					print("QR: Done --- data={}".format(data))
					
		#time.sleep(0.010)

qrDecodeX = threading.Thread(target=QR_Decoder_Thread, daemon=True, args=(queue_in, queue_out))
qrDecodeX.start()


""" ----- Main Loop ------------------------------
"""
grabbed, frame = capture.read()
with qr_lock:
	qrSrcImg = frame.copy()
	queue_in.put(qrSrcImg)
	qrBusy = True
	if DEBUG:
		print("init -- qrTrig ---")

time.sleep(0.05)

while True and not evAckClose.isSet():

	grabbed, frame = capture.read()

	with qr_lock:
		if not queue_out.empty():
			if DEBUG:
				print("Main: queue_out not empty!!")
			
			qrData = queue_out.get()
			qrBbox = queue_out.get()
			qrRectifiedImage = queue_out.get()
			timeSZ = queue_out.get()
			qrBusy = False

			
	if DEBUG:
		print("Main: qrBusy={}".format(qrBusy))
		
	if (not qrBusy):
		if (len(qrData)>0):
			mixer.music.play()
			#-- QR detected and decoded	
			codeSZ = "{}".format(qrData)
			frame = draw_bbox(qrSrcImg, qrBbox)
			#lockedFrame = frame.copy()
			rectifiedImage = np.uint8(qrRectifiedImage)
			#lockedRectifiedImage = rectifiedImage.copy()

			mainGUI.textCode.set(codeSZ)
			mainGUI.textTime.set(timeSZ)
			mainGUI.boxQRView.show(rectifiedImage)
			mainGUI.View.show(frame)
			
			time.sleep(2)
			
			mainGUI.boxQRView.off()

		#grabbed, frame = capture.read()
		with qr_lock:
			qrSrcImg = frame.copy()
			queue_in.put(qrSrcImg)
			qrBusy = True
			if DEBUG:
				print("Main: Trig >>>>")
		#time.sleep(0.001)
		
	mainGUI.View.show(frame)
	time.sleep(0.05)

qrDecodeX.join()
cv2.destroyAllWindows()
