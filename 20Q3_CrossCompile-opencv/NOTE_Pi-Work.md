# Enabling OpenCV on RPi with Cross-Compiled binaries #
## Reference ##
* [Cross compiling OpenCV 4 for Raspberry Pi and BeagleBone Black](https://solarianprogrammer.com/2018/12/18/cross-compile-opencv-raspberry-pi-raspbian/) 2019/Aug


## Prepare dependent libraries ##
```
sudo apt install -y libgtk-3-dev libcanberra-gtk3-dev
sudo apt install -y libtiff-dev zlib1g-dev
sudo apt install -y libjpeg-dev libpng-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev
```

## Install Binaries ##
* Uncompress and move pre-build binaries to /opt
> tar xvf opencv-4.1.0-armhf.tar.bz2
> sudo mv opencv-4.1.0 /opt
> sudo mv opencv.pc /usr/lib/arm-linux-gnueabihf/pkgconfig
>
> echo 'export LD_LIBRARY_PATH=/opt/opencv-4.1.0/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
> source ~/.bashrc

## Create some symbolic links that will allow Python to load the newly created libraries ##
```
sudo ln -s /opt/opencv-4.1.0/lib/python2.7/dist-packages/cv2 /usr/lib/python2.7/dist-packages/cv2
sudo ln -s /opt/opencv-4.1.0/lib/python3.7/dist-packages/cv2 /usr/lib/python3/dist-packages/cv2
```
Log out and log in or restart the Terminal.

