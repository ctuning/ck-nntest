/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include "ck_nntest_caffe_softmax.h"

using namespace caffe;

int main() {
  Caffe::set_mode(Caffe::GPU);
  Caffe::SetDevice(0);

  CK::Caffe::test_softmax();

  return 0;
}
