# -*- encoding: utf-8 -*-
"""
Theia camera GUI to demonstrate Dewarp and Pan/Tilt.
"""
import sys
import numpy as np
import cv2, time
import tkinter as TK
import threading
import socket
import argparse

import utils

#---- Use site-packages modules
from cy_ViPanel import tkViPanel, tkV2Frame, tkH2Frame, tkV3Frame
import cy_ViPanel as ViDISP


###########################################################
# Argument Parser
###########################################################
parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, help='The host machine: localhost or IP of remote machine', default='localhost')
parser.add_argument('--port', type=int, help='The port on which to connect the host', default=3000)
# parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=70)
args = parser.parse_args()


#----------------------------------------------------------------------
# Main GUI
#----------------------------------------------------------------------
class MainGUI:
	"""
	"""
	def __init__(self, host, port):
		self.thread = threading.Thread(target=self.Tk_mainloop, daemon=True, args=())
		self.host = host
		self.port = port

		self.connected = False
		self.disconnect_req = False


		self.pt_button_hold = False
		self.pt_button = "btnNONE"

		# A temporary buffer in which the received data will be copied
		# this prevents creating a new buffer all the time
		self.tmp_buf = bytearray(7)
		self.tmp_view = memoryview(self.tmp_buf) # this allows to get a reference to a slice of tmp_buf

		# Creates a temporary buffer which can hold the largest image we can transmit
		self.img_max_size = 2000000
		self.img_buf_0 = bytearray(self.img_max_size)
		self.img_view_0 = memoryview(self.img_buf_0)

		self.img_buf_1 = bytearray(self.img_max_size)
		self.img_view_1 = memoryview(self.img_buf_1)

		self.shutdown_req = False

	def Tk_mainloop(self):

		self.root = TK.Tk()

		#-- Create Top-Bottom frames
		self.mainFrames = tkV2Frame(self.root).Frames

		#-- Use frame#0 to display image
		self.feView = tkViPanel(self.mainFrames[0], size=(640, 480))

		#-- Use frame#1 for configuration (host, port, quality) and (connect)
		self.ctrlFrames = tkH2Frame(self.mainFrames[1]).Frames

		self.confFrames = tkV3Frame(self.ctrlFrames[0]).Frames
		#-- HOST
		TK.Label(self.confFrames[0], text="HOST: ").pack(side=TK.LEFT, fill=TK.Y)
		self.txtHost = TK.StringVar()
		self.confHost = TK.Entry(self.confFrames[0], width=20, bd=2, textvariable=self.txtHost)
		self.confHost.pack(side=TK.LEFT, expand=TK.YES)
		# self.txtHost.set("192.168.1.19")
		self.txtHost.set(self.host)

		#-- PORT
		TK.Label(self.confFrames[1], text="PORT: ").pack(side=TK.LEFT, fill=TK.BOTH)
		self.txtPort = TK.StringVar()
		self.confPort = TK.Entry(self.confFrames[1], width=20, bd=2, textvariable=self.txtPort)
		self.confPort.pack(side=TK.LEFT, expand=TK.YES)
		self.txtPort.set(self.port)

		#-- Quality
		TK.Label(self.confFrames[2], text="Quality: ").pack(side=TK.LEFT, fill=TK.Y)
		self.txtQuality = TK.StringVar()
		self.confQuality = TK.Entry(self.confFrames[2], width=20, bd=2, textvariable=self.txtQuality)
		self.confQuality.pack(side=TK.LEFT, expand=TK.YES)
		self.txtQuality.set(70)

		#-- Connect
		self.btnConnect = TK.Button(self.ctrlFrames[1], width=15, text="CONNECT", command=self.connect)
		self.btnConnect.pack(side=TK.TOP, fill=TK.BOTH)

		#-- Server Shutdown
		self.btnShutdown = TK.Button(self.ctrlFrames[1], width=15, text="SHUTDOWN", command=self.shutdown)
		self.btnShutdown.pack(expand=TK.YES)

		self.root.mainloop()


	def socket_connect(self):
		print("Connecting camera ...")
		host = self.txtHost.get()
		port = int(self.txtPort.get())
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except:
			raise RuntimeError("ERROR creating socket !!")
			return -1

		try:
			self.sock.settimeout(20)
			self.sock.connect((host, port))
			self.sock.settimeout(None)
		except:
			self.sock.settimeout(None)
			print("Failed to connect remote Host !!")
			return -1

		return 0


	def shutdown(self):
		if self.connected:
			#-- Post a flag to main thread to process shutdown and end application loop !!
			self.shutdown_req = True
		else:
			#-- connect Host before sending shutdown command !!
			self.socket_connect()
			#-- Now we can send shutdown comman though
			print("Sending shutdown command ...")
			self.sock.sendall('quit!'.encode('ascii'))
			self.sock.close()
			#-- Post a flag to main thread to process shutdown and end application loop !!
			self.shutdown_req = True

	def post_disconnect(self):
		print("Post-disconnection ...")
		#--- Reset UIs
		mainGUI.connected = False
		self.disconnect()
		mainGUI.feView.off()


	def connect(self):
		if self.connected == False:
			if self.socket_connect() < 0:
				return

			# #-- configure jpeg_quality
			jpeg_quality = self.txtQuality.get()
			self.send_int_msg('jpegQ', int(jpeg_quality))
			self.recv_reply_ack('jpegQ', int(jpeg_quality))
			self.confQuality.configure(state=TK.DISABLED)

			#-- wait a moment for server to start up camera
			time.sleep(0.001)

			#--- Initialize UIs
			self.connected = True
		else:
			print("Disconnecting camera ...")
			self.disconnect_req = True

			#--- Reset UIs
			self.btnConnect.configure(text = "CONNECT")
			self.confQuality.configure(state=TK.NORMAL)


	def send_int_msg(self, cmdstr, intdata):
		self.msg = bytes("{}{:07}".format(cmdstr, intdata), "ascii")
		try:
			utils.send_data(self.sock, self.msg)
		except:
			#print("-- shit! --")
			return -1

		return len(self.msg)

	def disconnect(self):
		try:
			self.sock.sendall('dscx!'.encode('ascii'))
			self.sock.close()
		except:
			return -1
		return 0

	def recv_reply_ack(self, cmdstr, intdata):
		try:
			utils.recv_data_into(self.sock, self.tmp_view[:5], 5)
		except:
			return -1

		cmd = self.tmp_buf[:5].decode('ascii')
		if cmd != cmdstr:
			raise RuntimeError("Inconsistent server reply {} != {}".format(cmd, cmdstr))
			return -1

		try:
			utils.recv_data_into(self.sock, self.tmp_view, 7)
		except:
			return -1

		ack_data = int(self.tmp_buf.decode('ascii'))
		if ack_data != intdata:
			raise RuntimeError("Inconsistent server reply {} != {}".format(ack_data, intdata))
			return -1

		return ack_data


	def recv_int_data(self, cmdstr):
		ack_data = 0
		try:
			utils.recv_data_into(self.sock, self.tmp_view[:5], 5)
		except:
			return -1, ack_data

		cmd = self.tmp_buf[:5].decode('ascii')
		if cmd != cmdstr:
			raise RuntimeError("Inconsistent server reply {} != {}".format(cmd, cmdstr))
			return -1, ack_data

		try:
			utils.recv_data_into(self.sock, self.tmp_view, 7)
		except:
			return -1, ack_data

		ack_data = int(self.tmp_buf.decode('ascii'))
		return 0, ack_data


	def recv_image_data(self, img_size, img_sel):
		imgView = (self.img_view_1 if img_sel else self.img_view_0)
		if img_size > self.img_max_size:
			raise RuntimeError("Expected size {} exceeds buffer size {}".format(img_size, self.img_max_size))
			return -1, imgView

		try:
			utils.recv_data_into(self.sock, imgView[:img_size], img_size)
		except:
			return -1, imgView

		# Read the final handshake
		try:
			cmd = utils.recv_data(self.sock, 5).decode('ascii')
		except:
			return -1, imgView

		if cmd != 'enod!':
			raise RuntimeError("Unexpected server reply. Expected 'enod!', got '{}'".format(cmd))
			return -1, imgView

		# # Transaction is done, we now process/display the received image
		# img = jpeg_decode_func(img_view[:img_size])

		return 0, imgView



#---------------------------------------------------------
# Main thread functions
#---------------------------------------------------------

def onClose():
	global evAckClose
	evAckClose.set()
	# print("---- Set ----")

jpeg_decode_func = lambda buf: utils.cv2_decode_image_buffer(buf)


def get_remote_feye_view(index):
	global mainGUI

	# Prepare the request
	if mainGUI.send_int_msg('image', index) < 0:
		raise RuntimeError('ERROR requesting feye view images !!')
		return -1, -1, None


	#------------------------------------------------------
	# Read the reply command ("feye!1234567")
	#------------------------------------------------------
	_, index = mainGUI.recv_int_data('image')
	#print("index= ", index)

	#-------------------------------------------------------
	# Read the feye view image buffer size ("fsize1234567")
	#-------------------------------------------------------
	succ, feImg_size = mainGUI.recv_int_data('size!')
	if succ < 0:
		return -1, -1, None
	#print("feImg_size ", feImg_size)

	#-------------------------------------------------------
	# Read the image buffer
	#-------------------------------------------------------
	succ, recv_feImg = mainGUI.recv_image_data(feImg_size, 0)
	if succ < 0:
		return -1, -1, None

	#------------------------------------------------------
	# Read the end of image command ("enod!1234567")
	#------------------------------------------------------
	mainGUI.recv_int_data('enod!')

	#print("Frame index {}, feSize {}".format(index, feImg_size))
	return index, feImg_size, recv_feImg


#---------------------------------------------------------
# Main thread Entry
#---------------------------------------------------------
""" ----- Initiate Main GUI ------------------------------
"""
evAckClose = threading.Event()
evAckClose.clear()
mainGUI = MainGUI(args.host, args.port)
mainGUI.thread.start()
time.sleep(0.01)

mainGUI.root.wm_protocol("WM_DELETE_WINDOW", onClose)
last_frame_index = 0
frame_index = 0
while True:
	if mainGUI.connected:
		#----------------------------------------------
		# Disconnect Handling
		#----------------------------------------------
		if mainGUI.disconnect_req:
			mainGUI.disconnect_req = False
			mainGUI.post_disconnect()
			continue

		#----------------------------------------------
		# 向 server 提取影像
		#----------------------------------------------
		#--- Request feye image from server.
		frame_index, feImg_size, recv_feImg, = get_remote_feye_view(0)
			# get_remote_feye_view(frame_index)
		# print("Frame index {}, feSize {}".format(frame_index, feImg_size))
		# print("check: {} {}", len(recv_feImg), len(recv_dwpImg))

		if last_frame_index == frame_index:
			if feImg_size < 0 :
				raise RuntimeError("Failed to get feye image!!")

			# Transaction is done, we now process/display the received image
			img = jpeg_decode_func(recv_feImg[:feImg_size])
			mainGUI.feView.show(img)

			last_frame_index = frame_index

		# if frame_index == 9999999:
		# 	frame_index = 0
		# else:
		# 	frame_index += 1

		#-----------------------------------------------
		# stop pulling image from remote side
		#-----------------------------------------------
		if mainGUI.shutdown_req:
			#-- send 'quit!' command to shutdown remote service
			mainGUI.sock.sendall('quit!'.encode('ascii'))
			#-- close local socket
			mainGUI.sock.close()
			#-- clear connected flag
			mainGUI.connected = False
		pass #-- end of if mainGUI.connected == True

	if mainGUI.shutdown_req:
		#-- close Application
		onClose()

	if evAckClose.isSet():
		break

cv2.destroyAllWindows()
