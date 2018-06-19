# ck-nntest
AI/SW/HW co-design repository
# CK-NNTest - testing and benchmarking common Neural Network operations via Collective Knowledge

[![logo](https://github.com/ctuning/ck-guide-images/blob/master/logo-powered-by-ck.png)](http://cKnowledge.org)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

## Installation

```
$ sudo pip install ck
$ ck pull repo --url=https://github.com/dividiti/ck-nntest
```

Note that you can install CK locally as described [here](https://github.com/ctuning/ck#minimal-installation).

### Compute Library (OpenCL)

To use Compute Library (OpenCL) tests with the master branch of the public [repository](https://github.com/ARM-software/ComputeLibrary.git), install:
```
$ ck install package:lib-armcl-opencl-master
```

To install a specific version of the library (e.g., 18.05), use:
```
$ ck install package:lib-armcl-opencl-18.05 
```
To check out other versions available, use:
```
$ ck list package:lib-armcl-opencl-*
```

### TensorFlow

To use TensorFlow CPU tests, install a third-party [TensorFlow_CC](https://github.com/FloopCZ/tensorflow_cc) package:
```
$ ck pull repo --url=git@github.com:dividiti/ck-tensorflow
$ ck install package:lib-tensorflow_cc-shared-1.7.0 [--env.CK_HOST_CPU_NUMBER_OF_PROCESSORS=2]
```
To install, follow the instructions in the [Readme](https://github.com/ctuning/ck-tensorflow/blob/master/package/lib-tensorflow_cc-shared-1.7.0/README.md)
**NB:** You may want to limit the number of build threads on a memory-constrained platform (e.g. to 2 as above).

### Caffe

To use Caffe tests, get the public [CK-Caffe](https://github.com/dividiti/ck-caffe) repository:
```
$ ck pull repo --url=https://github.com/dividiti/ck-caffe
```

To use Caffe CPU tests, install:
```
$ ck install package:lib-caffe-bvlc-master-cpu-universal
```

To use Caffe OpenCL tests, install one or more of the packages listed by:
```
$ ck list package:lib-caffe-bvlc-opencl-*-universal
```

For example, install Caffe with [CLBlast](https://github.com/cnugteren/CLBlast):
```
$ ck install package:lib-caffe-bvlc-opencl-clblast-universal
```

## Usage

### View all operator tests

To view all available NNTest test programs and data sets:

```
$ ck search program --tags=nntest | sort
$ ck search dataset --tags=nntest | sort
```

### Test a single operator

To compile and run a single test listed above, use e.g.:
```
$ ck run nntest:softmax-armcl-opencl
```

### Run Experiments on Compute Libray (OpenCL)

CK-NNTEST supports the following operators:
* avgpool (fp32, uint8)
* convolution (fp32, uint8)
* depthwise convolution (fp32, uint8)
* direct convolution (fp32, uint8)
* fully connected (fp32, uint8)
* gemm (fp32)
* reshape (fp32, uint8)
* resize bilinear (fp32, uint8)
* softmax (fp32, uint8)
