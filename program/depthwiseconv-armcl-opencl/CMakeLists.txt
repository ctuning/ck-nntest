cmake_minimum_required(VERSION 3.8)
project(depthwiseconv_armcl_opencl)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        autotune/tuner_depthwise_convolution.cpp
        autotune/tuner_depthwise_convolution.h
        depthwiseconv.cpp)

add_executable(depthwiseconv_armcl_opencl ${SOURCE_FILES})

#set(USE_18_05_PLUS True)

if (USE_18_05_PLUS)
    add_definitions(-DARMCL_18_05_PLUS)
    include_directories(/home/nikolay/CK-TOOLS/lib-armcl-opencl-private-dividiti-master-gcc-6.4.0-linux-64/src)
    include_directories(/home/nikolay/CK-TOOLS/lib-armcl-opencl-private-dividiti-master-gcc-6.4.0-linux-64/src/utils)
    include_directories(/home/nikolay/CK-TOOLS/lib-armcl-opencl-private-dividiti-master-gcc-6.4.0-linux-64/src/include)
else (USE_18_05_PLUS)
    include_directories(/home/nikolay/CK-TOOLS/lib-armcl-opencl-private-master-gcc-6.3.0-linux-64/src)
    include_directories(/home/nikolay/CK-TOOLS/lib-armcl-opencl-private-master-gcc-6.3.0-linux-64/src/utils)
    include_directories(/home/nikolay/CK-TOOLS/lib-armcl-opencl-private-master-gcc-6.3.0-linux-64/src/include)
endif (USE_18_05_PLUS)

include_directories(/home/nikolay/CK-TOOLS/lib-nntest-0.1-gcc-6.4.0-linux-64/install/include)