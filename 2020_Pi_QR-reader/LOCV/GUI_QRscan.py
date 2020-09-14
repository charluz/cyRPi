# -*- encoding: utf-8 -*-

import os, sys
import numpy as np
import cv2, time
import tkinter as TK
import threading

DEBUG = False
MAIN_WN_WIDTH = 640
MAIN_WN_HEIGHT = 480

USE_THREADING_CAMERA = True
USE_THREADING_DECODE = False


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
	global evAckClose
	evAckClose.set()



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

mp3Beep = "./beep.mp3"
mp3Beep2 = "./beep-beep.mp3"

lockedTime = time.time()


"""----- QR Decode thread ------------------------
"""
def QR_Decoder_Thread():
	pass
	
qrDecodeX = threading.Thread(target=QR_Decoder_Thread, daemon=True, args=()).start()



""" ----- Main Loop ------------------------------
"""
while True and not evAckClose.isSet():

	grabbed, frame = capture.read()

	"""
	if not grabbed:
		time.sleep(0.05)
		continue
	"""
	if True:
		# Detect and decode the qrcode
		t = time.time()
		
		if USE_THREADING_DECODE:
			ret, bbox = qrDecoder.detectMulti(frame)
			print("type ret={}, type bbox={}".format(type(ret), type(bbox)))
			if ret:
				data, rectifiedImage = qrDecoder.decode(frame, bbox)
			else:
				data = ""
		else:
			data,bbox,rectifiedImage = qrDecoder.detectAndDecode(frame)
				
		timeSZ = "{:.3f} sec".format(time.time() - t)
		if DEBUG:
			print("Time Taken for Detect and Decode : {:.3f} seconds".format(time.time() - t))

		if len(data)>0:
			if scanState == "HUNTING":
				if DEBUG:
					print("--- XX ---")
					
				scanState = "LOCKED"

				lockedCodeSZ = codeSZ = "{}".format(data)
				frame = draw_bbox(frame, bbox)
				lockedFrame = frame.copy()
				rectifiedImage = np.uint8(rectifiedImage)
				lockedRectifiedImage = rectifiedImage.copy()

				os.system("mplayer "+mp3Beep2)
				lockedTime = time.time()
			else:
				if DEBUG:
					print("--- YY ---")
				frame = lockedFrame
				rectifiedImage = None	#lockedRectifiedImage

		else:
			if DEBUG:
				print("--- 1 ---")
				
			if scanState == "LOCKED" and (time.time() - lockedTime < 3):
				if DEBUG:
					print("--- 2 ---")
				frame = lockedFrame
			else:
				if DEBUG:
					print("--- 3 ---")
				scanState = "HUNTING"
				mainGUI.boxQRView.off()
				rectifiedImage = None
				lockedCodeSZ = ""
				codeSZ=""

		
		if DEBUG:
			print("scanState={} ".format(scanState))

		mainGUI.textCode.set(codeSZ)
		mainGUI.textTime.set(timeSZ)
		if rectifiedImage is None:
			if DEBUG:
				print("--- A ---")
			pass #mainGUI.boxQRView.off()
		else:
			if DEBUG:
				print("--- B ---")
			mainGUI.boxQRView.show(rectifiedImage)
	
	mainGUI.View.show(frame)

		
cv2.destroyAllWindows()
