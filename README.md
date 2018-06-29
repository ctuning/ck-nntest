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

### CK-NNTest

```
$ ck install package:lib-nntest
```

### Compute Library (OpenCL)

To use Compute Library (OpenCL) tests with the master branch of the public [repository](https://github.com/Arm-software/ComputeLibrary.git), install:
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

CK-NNTest supports the following operators:
* average pool ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#average-pool-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#average-pool-uint8))
* convolution ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#convolution-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#convolution-uint8))
* depthwise convolution ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#depthwise-convolution-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#depthwise-convolution-uint8))
* direct convolution ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#direct-convolution-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#direct-convolution-uint8))
* fully connected ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#fully-connected-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#fully-connected-uint8))
* gemm ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#gemm-to-fix))
* reshape ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#reshape-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#reshape-uint8))
* resize bilinear ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#resize-bilinear-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#resize-bilinear-uint8))
* softmax ([fp32](https://github.com/dividiti/ck-nntest/blob/master/README.md#softmax-fp32), [uint8](https://github.com/dividiti/ck-nntest/blob/master/README.md#softmax-uint8))

#### average pool fp32
* Kernel profiling:
```
$ ck run nntest:avgpool-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:avgpool-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### average pool uint8
* Kernel profiling:
```
$ ck run nntest:avgpool-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:avgpool-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```

#### convolution fp32
* Kernel profiling:
```
$ ck run nntest:conv-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:conv-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### convolution uint8
* Kernel profiling:
```
$ ck run nntest:conv-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:conv-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```


#### depthwise convolution fp32
* Kernel profiling:
```
$ ck run nntest:depthwiseconv-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:depthwiseconv-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### depthwise convolution uint8
* Kernel profiling:
```
$ ck run nntest:depthwiseconv-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:depthwiseconv-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```

#### direct convolution fp32
* Kernel profiling:
```
$ ck run nntest:directconv-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:directconv-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### direct convolution uint8
* Kernel profiling:
```
$ ck run nntest:directconv-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:directconv-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```


#### fully connected fp32
* Kernel profiling:
```
$ ck run nntest:fullyconnected-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:fullyconnected-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### fully connected uint8
* Kernel profiling:
```
$ ck run nntest:fullyconnected-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:fullyconnected-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```


#### gemm [TO FIX]
* Kernel profiling:
```
$ ck run nntest:gemm-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:gemm-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```




#### reshape fp32
* Kernel profiling:
```
$ ck run nntest:reshape-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:reshape-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### reshape uint8
* Kernel profiling:
```
$ ck run nntest:reshape-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:reshape-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```

#### resize bilinear fp32
* Kernel profiling:
```
$ ck run nntest:resizebilinear-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:resizebilinear-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### resize bilinear uint8
* Kernel profiling:
```
$ ck run nntest:resizebilinear-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:resizebilinear-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```

#### softmax fp32
* Kernel profiling:
```
$ ck run nntest:softmax-armcl-opencl --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:softmax-armcl-opencl --repetitions=10 --record --timestamp=<platform>-validation
```

#### softmax uint8
* Kernel profiling:
```
$ ck run nntest:softmax-armcl-opencl-uint8 --dvdt_prof --record --timestamp=<platform>-profiling
```
* Validation:
```
$ ck run nntest:softmax-armcl-opencl-uint8 --repetitions=10 --record --timestamp=<platform>-validation
```


### Choose a dataset

If more than one dataset suitable for the operator under test (`softmax`
above) is found, make the choice.

To test with a particular dataset, use e.g.:
```
$ ck run program:softmax-armcl-opencl --dataset_file=shape-1024-1-1
```

To test with all suitable datasets, use e.g.:
```
$ ck run nntest:softmax-armcl-opencl --iterations=1
```

**NB:** By default, `ck run nntest:*` iterates over the batch sizes ranging from 1 to 16;
`--iterations=1` stops the test after the first iteration (for the batch size of 1).

### Override dataset values

To override one or more keys in a dataset, use e.g.:
```
$ ck run program:softmax-armcl-opencl --env.CK_IN_SHAPE_C=256
```


### Record test results locally

By default, test results are printed to the standard output. To save test
results in a local repository, use e.g.:

```
$ ck run nntest:softmax-armcl-opencl --iterations=1 --record
```

To list the results saved locally, use e.g.:
```
$ ck list local:experiment:nntest-softmax-armcl-opencl-*
```

### Output validation

When a test is invoked with a particular dataset for the first time, CK saves
its output as reference (e.g. a vector of floating-point values).  In
subsequent invocations of this test with the same dataset, CK validates its output
against the reference.

To replace the reference output, use e.g.:
```
$ ck run program:softmax-armcl-opencl --overwrite_reference_output
```

Output validation is performed within a certain threshold specified via the
`CK_ABS_DIFF_THRESHOLD` key in the `runs_vars` dictionary in the program
metadata. That is, any differences smaller than the threshold are ignored.

To override the threshold value at run-time, use e.g.:
```
$ ck run program:softmax-armcl-opencl --env.CK_ABS_DIFF_THRESHOLD=0.01
```

#### Output naming convention

Each reference output gets a unique name e.g. `default-3cda82464112173d-1000-1-1-2-42`. Here:
- `default` is the command key of the given test program;
- `3cda82464112173d` is the unique id of the dataset (`ck-nntest:dataset:tensor-0001`);
- `1000-1-1` are the dash-separated values of the keys in the dataset file (`shape-1000-1-1.json`) listed in the alphabetical order (i.e. `CK_IN_SHAPE_C`, `CK_IN_SHAPE_H`, `CK_IN_SHAPE_W`);
- `2-42` are the dash-separated values of selected keys in the `run_vars` dictionary in the program metadata file listed in the alphabetical order (i.e. `CK_IN_SHAPE_N`, `CK_SEED`).


### Visualise test results

To visualize test results in a web browser, run:
```
$ ck dashboard nntest
```
and select "Raw results".

It is possible to run this dashboard on a different host and port:
```
$ ck dashboard nntest --host=192.168.99.1 --port=3355
```

It is also possible to specify external host and port useful for Docker instances:
```
$ ck dashboard nntest --wfe_host=192.168.99.1 --wfe_port=3355
```

### Replay test results

You will be able to replay individual tests (to validate performance or fix bugs).

The simplest way is to select a given experiment from the above nntest dashboard,
and then click on a button "Copy to clipboard" in the `Reproduce` field.

You can then paste and run a command in your shell. It will look similar to
```
$ ck replay experiment:186380dfcd98cd7a --point=4e9e9476bab09b2c
```

Alternatively, you can see all available raw nntest experiments on your machine as follows:
```
$ ck search experiment --tags=nntest
```

### Test outputs of all tensor shapes and batch sizes:

```
$ ck run nntest:*softmax* --iterations=4 --repetitions=1 --pause_if_fail
```

### Run on other platforms

You can run some of the test directly on Android devices connected to your host machine via ADB
as follows (you need to have Android NDK and SDK installed):

```
$ ck compile program:softmax-armcl-opencl --speed --target_os=android23-arm64
$ ck run program:asoftmax-armcl-opencl --speed --target_os=android23-arm64
```

We plan to add support to compile and run ArmCL-based clients on Android too
(there are some minor issues at this stage):

```
$ ck install package --tags=armcl,vopencl,vavgpool --env.USE_EMBEDDED_KERNELS=ON --target_os=android23-arm64
$ ck compile program:avgpool-armcl-opencl --speed --target_os=android23-arm64
$ ck run program:avgpool-armcl-opencl --speed --target_os=android23-arm64
```

### Notes

Extra environment variables for development/debugging:

* `--env.CK_ADD_RAW_NNTEST_OUTPUT=yes` - add vector output to the CK pipeline
* `--env.CK_ADD_RAW_DVDT_PROF=yes` - add raw `dvdt_prof` profile to the CK pipeline
* `--env.CK_ADD_RAW_MALI_HWC=yes` - add Mali hardware performance counters to the CK pipeline

To record the hostname to the meta of all experimental entries:

```
$ ck set kernel var.record_nntest_hostname=yes
```

To turn off recording the hostname:
```
$ ck set kernel var.record_nntest_hostname=no
```
or
```
$ ck set kernel var.record_nntest_hostname=
```

# Native validation of Arm OpenCL kernels

The Arm Compute Library includes validation suite which tests all internal Arm routines. 
It can be compiled for any ArmCL package as follows:

```
$ ck compile compile program:validation-armcl-opencl
```

It is possible to customize this build via `--env.KEY=val`.
For example, you can add CXX flags as follows:

```
$ ck compile program:validation-armcl-opencl --env.EXTRA_CXX_FLAGS="-DDVDT_DEBUG"
```

You can now run validation as follows (select the `run` command):
```
$ ck run program:validation-armcl-opencl
```

You can also filter tests such as for `softmax` as follows:
```
$ ck run program:validation-armcl-opencl --env.FILTER=CL/.*Softmax
```
