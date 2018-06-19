/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLGEMM.h>
#include <arm_compute/core/Types.h>

#include "ck_nntest_armcl.h"
#include <memory>

static const int DEFAULT_M = 1024;
static const int DEFAULT_N = 1024;
static const int DEFAULT_K = 1024;

static const float DEFAULT_ALPHA = 1.f;
static const float DEFAULT_BETA = 0.f;

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

enum TENSOR {
  INPUT_A, INPUT_B, INPUT_C, OUTPUT,

  TENSOR_COUNT
};

static const char *TENSOR_NAMES[TENSOR_COUNT] = {
  [INPUT_A] = "A",
  [INPUT_B] = "B",
  [INPUT_C] = "C",
  [OUTPUT]  = "OUTPUT"
};

void init_tensor_data(CLTensor *tensor, const CK::Shape &shape, const char *env_var, const char *title) {
  float *in_data = get_random_raw_data<float>(shape);
  log_raw_data(in_data, shape, env_var, title);
  copy_raw_data_to_tensor(tensor, in_data, shape);
  delete[] in_data;
}

int main() {
  init_test();
  init_armcl();

  const unsigned int m = getenv_i("CK_GEMM_M", DEFAULT_M);
  const unsigned int n = getenv_i("CK_GEMM_N", DEFAULT_N);
  const unsigned int k = getenv_i("CK_GEMM_K", DEFAULT_K);
  const float alpha = getenv_f("CK_GEMM_ALPHA", DEFAULT_ALPHA);
  const float beta = getenv_f("CK_GEMM_BETA", DEFAULT_BETA);

  printf("M = %d, K = %d, N = %d, alpha = %f, beta = %f\n", m, k, n, alpha, beta);

  CK::Shape shapes[TENSOR_COUNT] = {
    [INPUT_A] = CK::Shape::make_chw(1, m, k),
    [INPUT_B] = CK::Shape::make_chw(1, k, n),
    [INPUT_C] = CK::Shape::make_chw(1, n, m),
    [OUTPUT]  = CK::Shape::make_chw(1, n, m)
  };

  CLTensor tensors[TENSOR_COUNT];
  CLGEMM gemm;

  measure_setup([&]() {
    for (int i = 0; i < TENSOR_COUNT; ++i) {
      auto a = tensors[i].allocator();
      a->init(TensorInfo(to_tensor_shape_whcn(shapes[i]), Format::F32));
    }

    // Exceptionally, the CLGEMM configure must be called before allocating any tensors
    // (otherwise CLGEMM does not work).
    gemm.configure(tensors + INPUT_A, tensors + INPUT_B, tensors + INPUT_C, tensors + OUTPUT, alpha, beta);

    // Allocate and initialize tensors after the CLGEMM configure.
    for (int i = 0; i < TENSOR_COUNT; ++i) {
      tensors[i].allocator()->allocate();
      if (i != OUTPUT) {
        init_tensor_data(tensors + i, shapes[i], "CK_PRINT_IN_TENSOR", TENSOR_NAMES[i]);
      }
    }
  });

  measure_test([&]() {
    gemm.run();

    // Make sure all the OpenCL jobs are done executing
    CLScheduler::get().sync();
  });

  const CK::Shape &output_shape = shapes[OUTPUT];
  float *out_data = new float[output_shape.data_count()];
  copy_raw_data_from_tensor(tensors + OUTPUT, out_data, output_shape);
  print_output_raw_data(out_data, output_shape);
  dump_output_raw_data(out_data, output_shape);
  delete[] out_data;

  for (int i = 0; i < TENSOR_COUNT; ++i) {
    tensors[i].allocator()->free();
  }

  finish_test();
  return 0;
}
