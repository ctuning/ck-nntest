cmake_minimum_required(VERSION 3.8)
project(conv_armcl_opencl)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        autotune/tuner_convolution.cpp
        autotune/tuner_convolution.h
        conv.cpp)

add_executable(conv_armcl_opencl ${SOURCE_FILES})