#! /bin/bash


export PATH=/home/nikolay/CK/ck-env/platform.init/generic-linux:$PATH


. /home/nikolay/CK/local/env/42af974480b989d7/env.sh
. /home/nikolay/CK/local/env/1a4f96b3790174ff/env.sh
. /home/nikolay/CK/local/env/4c19a8e4f5093d05/env.sh
. /home/nikolay/CK/local/env/799de4c0e89eb088/env.sh

. /home/nikolay/CK/local/env/1a4f96b3790174ff/env.sh 1

export CK_DATASET_PATH=/home/nikolay/CK/ck-acl-private/dataset/tensor-depthwiseconv-mobilenets/

export CK_ABS_DIFF_THRESHOLD=0.001
export CK_DATASET_FILENAME=shape-512-12-12-1-1
export CK_DEPTHWISE_PAD=1
export CK_DEPTHWISE_STRIDE=1
export CK_IN_SHAPE_C=512
export CK_IN_SHAPE_H=12
export CK_IN_SHAPE_N=1
export CK_IN_SHAPE_W=12
export CK_OUT_RAW_DATA=tmp-ck-output.bin
export CK_SEED=42


echo    executing code ...
 ./depthwiseconv > tmp-stdout.tmp 2> tmp-stderr.tmp
