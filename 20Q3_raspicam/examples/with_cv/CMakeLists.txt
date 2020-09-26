cmake_minimum_required (VERSION 2.8)
project (raspicam_test)
# Enable C++11
#set(CMAKE_CXX_STANDARD 11)
#set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

find_package(raspicam REQUIRED)
find_package(OpenCV REQUIRED)
IF  ( OpenCV_FOUND AND raspicam_CV_FOUND)
MESSAGE(STATUS "COMPILING OPENCV TESTS")
add_executable (simpletest_raspicam_cv simpletest_raspicam_cv.cpp)

#-- For openCV 4.1: add ${openCV_LIBS} to target_link_libraries !!
target_link_libraries (simpletest_raspicam_cv ${OpenCV_LIBS} ${raspicam_CV_LIBS})
ELSE()
MESSAGE(FATAL_ERROR "OPENCV NOT FOUND IN YOUR SYSTEM")
ENDIF()
