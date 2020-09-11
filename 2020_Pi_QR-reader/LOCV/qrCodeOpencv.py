import cv2
import numpy as np
import sys
import time

DEBUG = False

WN_GAP = 20
MAIN_WN_WIDTH = 720
MAIN_WN_HEIGHT = 540
MAIN_WN_X, MAIN_WN_Y = 100, 100

QRCODE_WN_X, QRCODE_WN_Y = MAIN_WN_X+MAIN_WN_WIDTH+WN_GAP, MAIN_WN_Y


if False:
	if len(sys.argv)>1:
		inputImage = cv2.imread(sys.argv[1])
	else:
		inputImage = cv2.imread("qrcode-learnopencv.jpg")


def setup_capture(width=640, height=480):
	"""Sets up the video capture device.

	Returns the video capture instance on success and None on failure.

	Arguments:
		width: Width of frames to capture.
		height: Height of frames to capture.
	"""
	capture = cv2.VideoCapture(0)
	if not capture.isOpened():
		#print("Could not open video device!")
		return None
	capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	return capture


# Display barcode and QR code location
def display(im, bbox):
	n = len(bbox)
	for j in range(n):
		cv2.line(im, tuple(bbox[j][0]), tuple(bbox[ (j+1) % n][0]), (255,0,0), 3)

	# Display results
	cv2.imshow("QR Scanner", im)
	cv2.moveWindow("QR Scanner", MAIN_WN_X, MAIN_WN_Y)


def display_decode_QR(qr_image, bbox, code, timeused):
	if DEBUG:
		print("Num of bbox={}, num of qr_image={} ...".format(len(bbox), len(qr_image))
	
	osdCode = "%s".format(code)
	osdTime = "Time Used: %s".format(timeused)
	
	#print("Decoded Data : {}".format(data))
	#display(inputImage, bbox)
	rectifiedImage = np.uint8(qr_image);
	cv2.imshow("Rectified QRCode", rectifiedImage);


# Open Camera 
capture = setup_capture(MAIN_WN_WIDTH, MAIN_WN_HEIGHT)
if capture is None:
	print("ERROR: Could not open video device!")
	sys.exit()

# Create a qrCodeDetector Object
qrDecoder = cv2.QRCodeDetector()

while True:
	# Capture frame
	_, inputImage = capture.read()

	# Detect and decode the qrcode
	t = time.time()
	data,bbox,rectifiedImage = qrDecoder.detectAndDecode(inputImage)
	print("Time Taken for Detect and Decode : {:.3f} seconds".format(time.time() - t))
	if len(data)>0:
		print("Decoded Data : {}".format(data))
		display(inputImage, bbox)
		rectifiedImage = np.uint8(rectifiedImage);
		cv2.imshow("Rectified QRCode", rectifiedImage);
	else:
		print("QR Code not detected")
		cv2.imshow("Results", inputImage)
		
		
	# cv2.imwrite("output.jpg",inputImage)
	key = cv2.waitKey(1)
	if key == ord('q'):
		break

cv2.destroyAllWindows()
sys.exit()

