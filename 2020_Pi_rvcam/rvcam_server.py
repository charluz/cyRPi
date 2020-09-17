import sys
import argparse
import socket
import picamera

import cv2
import numpy as np

import utils
from pi_grabber import piGrabber
import time


###########################################################
# Argument Parser
###########################################################
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, required=True, default=3390,
	help='The port on which to listen for incoming connections')
parser.add_argument('--jpeg_quality', type=int, default=70,
	help='The JPEG quality for compressing the reply')
args = parser.parse_args()

###########################################################
# System Initial configurations
###########################################################
host		 = '' # any interface
port		 = args.port
jpeg_quality = args.jpeg_quality


jpeg_encode_func = lambda img, jpeg_quality=jpeg_quality: utils.cv2_encode_image(img, jpeg_quality)
jpeg_decode_func = lambda buf: utils.cv2_decode_image_buffer(buf)

#---------------------------------------------------------
# Start a thread to grab theia images
#---------------------------------------------------------
grabber = piGrabber(jpeg_quality=jpeg_quality)
grabber.set_manual_ae(100, 8333)
grabber.start()


# A lambda function to get a cv2 image
# get_buffer = lambda: grabber.get_buffer()
get_jpeg_image = lambda: grabber.get_jpeg_image()
drop_cmd_data = lambda: parse_cmddata()

#----------------------------------------------------------
# Define 'pointer' to directly access network msg and images
# in memory.
#----------------------------------------------------------
# A temporary buffer in which the received data will be copied
# this prevents creating a new buffer all the time
tmp_buf = bytearray(7)
tmp_view = memoryview(tmp_buf) # this allows to get a reference to a slice of tmp_buf

# Creates a temporary buffer which can hold the largest image we can transmit
img_buffer = bytearray(1000000)
img_view = memoryview(img_buffer)


def parse_cmdcode():
	global tmp_view, conn, tmp_buf
	try:
		utils.recv_data_into(conn, tmp_view[:5], 5)
	except:
		return '12345'
	cmdcode = tmp_buf[:5].decode('ascii')
	return cmdcode


def parse_cmddata():
	global tmp_view, conn, tmp_buf
	try:
		utils.recv_data_into(conn, tmp_view, 7)
	except:
		return -1
	cmddata = tmp_buf.decode('ascii')
	return cmddata


def send_msg(cmdstr, intdata):
	global conn
	msg = bytes("{}{:07}".format(cmdstr, intdata), "ascii")
	try:
		utils.send_data(conn, msg)
	except:
		raise RuntimeError("ERROR sending msg to client!!")


def send_image(img_buf):
	global conn
	try:
		utils.send_data(conn, img_buf)
		utils.send_data(conn, bytes('enod!', 'ascii'))
	except:
		raise RuntimeError("ERROR sending image buffer")

is_shutdown = False

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
	raise RuntimeError("Failed to create socket !!")
	sys.exit()

s.bind((host, port))
s.listen(1)

print("Listening at port {} ...".format(port))

while True:
	conn, addr = s.accept()

	with conn:
		print('Connected by', addr)
		while True:
			#-------------------------------------
			#  接收命令訊息
			#-------------------------------------
			try:
				utils.recv_data_into(conn, tmp_view[:5], 5)
			except:
				continue
			# print("&")
			cmd = tmp_buf[:5].decode('ascii')
			#-----------------------------------------------
			# Client sends "imageXXXXXXX" to request new image
			# where XXXXXXX is image index
			#-----------------------------------------------
			if (cmd == 'image'):
				# Read the image index
				image_index = int(parse_cmddata())
				# Grab and encode the image
				#print("Received: {}-{}".format(cmd, image_index))
				n_NG = 5
				img_buffer= None
				while True:
					img_buffer = get_jpeg_image()
					if img_buffer is None:
						if (n_NG==0):
							print("ERROR, Can't grab image!!")
							break
						else:
							print("WARNING, No image, === retry!!")
						n_NG -= 1
						print("==\\", end="")
						time.sleep(0.2)
						print("/==")
					else:
						# print("Sending image{} ...".format(image_index))
						break
					
				# print("Replying msg: image ", image_index)
				# Reply the image index
				#send_msg('image', grabber.frame_index)
				send_msg('image', image_index)

				# Prepare the message with the number of bytes going to be sent
				send_msg('size!', len(img_buffer))
				# print(">> img_buffer: {}".format(len(img_buffer)))
				#-- Send image and 'enod!'
				send_image(img_buffer)

				send_msg('enod!', image_index)

			elif (cmd == 'jpegQ'):
				#-- Setting jpeg quality
				#--- 目前 jpegQ 當做 Camera start capture 的信號，
				jpeg_quality = int(parse_cmddata())
				print("Setting quality: ", jpeg_quality)
				grabber.set_quality(jpeg_quality)
				#-- ack command
				send_msg('jpegQ', jpeg_quality)

			#-----------------------------------------------
			# Client sends "dscx!" to disconnect streaming
			#-----------------------------------------------
			elif cmd == 'dscx!':
				print("Processing disconnect command ...")
				break

			#-----------------------------------------------
			# Client sends "quit!" to shutdown Host
			#-----------------------------------------------
			elif cmd == 'quit!':
				is_shutdown = True
				print("Stopping Host service ...")
				break
			else:
				print("Got something else -- {}", cmd)

		print("Disconnecting ...", end="")
		conn.close()
		print(" Done")

		if is_shutdown:
			print("Shutting down video grabber ...", flush=True)
			grabber.stop()
			time.sleep(1)
			grabber.join()
			print(" Done")
			break

print("Bye bye !!")
