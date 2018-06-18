/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLReshapeLayer.h>

#include "arm_compute/core/PixelValue.h"
#include "autotune/tuner_reshape.h"
#include "ck_nntest_armcl.h"

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

int main() {
  init_test();
  arm_compute::ICLTuner *tuner = nullptr;
  const bool find_optimal_lws = static_cast<bool>(getenv("CK_FIND_OPTIMAL_LWS"));
  if(find_optimal_lws) tuner = new arm_compute::CLTuner_Reshape();
  init_armcl(tuner);

  Shape in_shape = get_input_shape_from_env();

  Shape out_shape;
  out_shape.num =  in_shape.num;
  out_shape.height = getenv_i("CK_OUT_SHAPE_H", 1);
  out_shape.height = getenv_i("CK_OUT_SHAPE_H", 1);
  out_shape.width =  getenv_i("CK_OUT_SHAPE_W", 1);
  out_shape.channels = getenv_i("CK_OUT_SHAPE_C", 1);

  CLTensor input, output;
  CLReshapeLayer layer;

  measure_setup([&]() {
    TensorShape tensor_shape(static_cast<unsigned int>(in_shape.width),
                             static_cast<unsigned int>(in_shape.height),
                             static_cast<unsigned int>(in_shape.channels),
                             static_cast<unsigned int>(in_shape.num));
    TensorShape shape_reshaped(static_cast<unsigned int>(out_shape.width),
                               static_cast<unsigned int>(out_shape.height),
                               static_cast<unsigned int>(out_shape.channels),
                               static_cast<unsigned int>(in_shape.num));

    input.allocator()->init(TensorInfo(tensor_shape, Format::F32));
    output.allocator()->init(TensorInfo(shape_reshaped, Format::F32));

    layer.configure(&input, &output);

    input.allocator()->allocate();
    output.allocator()->allocate();

    float *in_data =  get_random_raw_data<float>(in_shape);
    print_input_raw_data(in_data, in_shape);
    copy_raw_data_to_tensor(&input, in_data, in_shape);
    delete[] in_data;
  });

  measure_test([&]() {
    layer.run();
    // Ensure that all OpenCL jobs have completed.
    CLScheduler::get().sync();
  });

  float *out_data = new float[out_shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, out_shape);
  print_output_raw_data(out_data, out_shape);

  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  input.allocator()->free();
  output.allocator()->free();
  if(find_optimal_lws) delete tuner;
  finish_test();
  return 0;
}
