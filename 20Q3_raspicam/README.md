# 實作 RaspiCam: C++ API for using Raspberry camera with/without OpenCv #

## 參考資料 ##
* [RaspiCam: C++ API for using Raspberry camera with/without OpenCv](http://www.uco.es/investiga/grupos/ava/node/40)
* The raspicam I use is v0.1.9 @ [SOURCEFORGE](https://sourceforge.net/projects/raspicam/files/?)
* Installation of OpenCV v4.1.0 on Raspberry Pi: [my Workshop: Cross Compiling OpencCV 4.0 for Raspberry Pi](https://github.com/charluz/cyRPi/tree/master/20Q3_CrossCompile-opencv)

## Raspicam with OpenCV ##
使用參考網站上的sample project 的原始 CMakeLists.txt 時，發現 build code 會出現以下 error:
```
[ 50%] Building CXX object CMakeFiles/simpletest_raspicam_cv.dir/simpletest_raspicam_cv.cpp.o
[100%] Linking CXX executable simpletest_raspicam_cv
/usr/bin/ld: CMakeFiles/simpletest_raspicam_cv.dir/simpletest_raspicam_cv.cpp.o: in function `main':
simpletest_raspicam_cv.cpp:(.text+0x2c8): undefined reference to `cv::imwrite(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, cv::_InputArray const&, std::vector<int, std::allocator<int> > const&)'
collect2: error: ld returned 1 exit status
make[2]: *** [CMakeFiles/simpletest_raspicam_cv.dir/build.make:85: simpletest_raspicam_cv] Error 1
make[1]: *** [CMakeFiles/Makefile2:73: CMakeFiles/simpletest_raspicam_cv.dir/all] Error 2
make: *** [Makefile:84: all] Error 2
```
修正方式是在 CMakeLists.txt 的 target_link_libraries 加入 ${OpenCV_LIBS}:
```
target_link_libraries(simpletest_raspicam_cv ${OpenCV_LIBS} ${raspicam_CV_LIBS})
```
