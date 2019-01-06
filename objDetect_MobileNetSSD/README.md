# README: Object Detection with RPi3 Camera #
Reference: [pyimagesearch tutorial](https://www.pyimagesearch.com/2018/09/19/pip-install-opencv/)

## The Content of the Folder ##
1. MobileNetSSD_deploy.caffemodel, MobileNet.prototxt.txt
2. read_time_object_detection.py:
	* Program to be run on PC
	```
	python real_time_object_detection.py \
		--prototxt MobileNetSSD_deploy.prototxt.txt \
		--model MobileNetSSD_deploy.caffemodel
	```
3. pi_object_detection.py:
	* Program to be run on PPi
	```
	python pi_object_detection.py \
		--prototxt MobileNetSSD_deploy.prototxt.txt \
		--model MobileNetSSD_deploy.caffemodel
	```

## The Performance ##

According to author's post, his Mac delivers 6.54 FPS while his Pi3 has 27.83 FPS (??). 
