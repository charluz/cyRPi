# Worklog of Cross Compiling OpenCV 4 for Raspberry Pi #

## Reference ##
* [Cross compiling OpenCV 4 for Raspberry Pi and BeagleBone Black](https://solarianprogrammer.com/2018/12/18/cross-compile-opencv-raspberry-pi-raspbian/) 2019/Aug

## My Workshop ##
* Start up a Debian Buster docker container as the build machine.
* Docker containner running on VM (Ubuntu 18.04 64bit)
> docker run -ti --name pi-cross-compile -v /home/charles/workbench:/home/charles/workbench debian:latest /bin/bash
> The whole stuff is in the folder ~/opencv-all of the container.

### The Scripts ###

```bash
sudo apt update
sudo apt upgrade
```

* Eable the armhf architecture on x86-64
```bash
sudo dpkg --add-architecture armhf
sudo apt update -y
sudo apt install -y qemu-user-static
```

* Install Python & GTK3
```
sudo apt-get install -y python3-dev python3-numpy python-dev python-numpy
sudo apt-get install -y libpython2-dev:armhf libpython3-dev:armhf
sudo apt-get install -y libgtk-3-dev:armhf libcanberra-gtk3-dev:armhf
```

* Install other libraries required by CV
```
sudo apt install -y libtiff-dev:armhf zlib1g-dev:armhf libjpeg-dev:armhf libpng-dev:armhf
sudo apt install -y libavcodec-dev:armhf libavformat-dev:armhf libswscale-dev:armhf libv4l-dev:armhf
sudo apt install -y libxvidcore-dev:armhf libx264-dev:armhf
```

* Install the default cross compilers (To create armhf binaries for RPi)
```
sudo apt install -y crossbuild-essential-armhf
sudo apt install -y gfortran-arm-linux-gnueabihf
```

* Install utilities needed while building opencv binaries
```
udo apt install -y cmake git pkg-config wget
```

* Download OpenCV (both default and contrib libraries)
```
cd ~
mkdir opencv_all && cd opencv_all
wget -O opencv.tar.gz https://github.com/opencv/opencv/archive/4.1.0.tar.gz
tar xf opencv.tar.gz
wget -O opencv_contrib.tar.gz https://github.com/opencv/opencv_contrib/archive/4.1.0.tar.gz
tar xf opencv_contrib.tar.gz
rm *.tar.gz
```

* Tw system variables required to buitl GTK+ support
```
export PKG_CONFIG_PATH=/usr/lib/arm-linux-gnueabihf/pkgconfig:/usr/share/pkgconfig
export PKG_CONFIG_LIBDIR=/usr/lib/arm-linux-gnueabihf/pkgconfig:/usr/share/pkgconfig
```

* Go and build OpenCV
1. Cmake configuration
```
cd opencv-4.1.0
mkdir -p build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
     -D CMAKE_INSTALL_PREFIX=/opt/opencv-4.1.0 \
     -D CMAKE_TOOLCHAIN_FILE=../platforms/linux/arm-gnueabi.toolchain.cmake \
     -D OPENCV_EXTRA_MODULES_PATH=~/opencv_all/opencv_contrib-4.1.0/modules \
     -D OPENCV_ENABLE_NONFREE=ON \
     -D ENABLE_NEON=ON \
     -D ENABLE_VFPV3=ON \
     -D BUILD_TESTS=OFF \
     -D BUILD_DOCS=OFF \
     -D PYTHON2_INCLUDE_PATH=/usr/include/python2.7 \
     -D PYTHON2_LIBRARIES=/usr/lib/arm-linux-gnueabihf/libpython2.7.so \
     -D PYTHON2_NUMPY_INCLUDE_DIRS=/usr/lib/python2/dist-packages/numpy/core/include \
     -D PYTHON3_INCLUDE_PATH=/usr/include/python3.7m \
     -D PYTHON3_LIBRARIES=/usr/lib/arm-linux-gnueabihf/libpython3.7m.so \
     -D PYTHON3_NUMPY_INCLUDE_DIRS=/usr/lib/python3/dist-packages/numpy/core/include \
     -D BUILD_OPENCV_PYTHON2=ON \
     -D BUILD_OPENCV_PYTHON3=ON \
     -D BUILD_EXAMPLES=OFF ..
```

2. Build and Install
```
make -j4
sudo make install/strip
```

3. <span style="color: red;">Change the name of a library that the installer mistakenly labeled as a x86_64 library when in fact it is an armhf one</span>
```
cd /opt/opencv-4.1.0/lib/python3.7/dist-packages/cv2/python-3.7/
sudo cp cv2.cpython-37m-x86_64-linux-gnu.so cv2.so
```

4. Compress the generated opencv package

[註] 
> * Build 在 /opt 的實際上 Pi (armhf) 的 binary。
> * 原始的 script 是把檔案打包到 Home(~) 目錄下，我改成存到 ~/opencv_all/Pi-INSTALLATION 裡面。

```
cd /opt
mkdir -p ~/opencv_all/Pi-INSTALLATION
tar -cjvf ~/opencv_all/Pi-INSTALLATION/opencv-4.1.0-armhf.tar.bz2 opencv-4.1.0
cd ~
```

5. Prepare pkg-config settings file
```
cd ~/opencv_all
git clone https://gist.github.com/sol-prog/ed383474872958081985de733eaf352d opencv_cpp_compile_settings
cd opencv_cpp_compile_settings
cp opencv.pc ~/opencv_all/Pi-INSTALLATION/
cd ~
```

最後，打包
~/opencv_all/Pi-INSTALLATION/ 到 RPi 上
