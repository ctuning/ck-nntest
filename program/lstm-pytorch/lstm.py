import os
import torch
import torch.nn as nn
import struct
import numpy as np
import json
from time import perf_counter
from pprint import pprint

start_setup_time = perf_counter()

# Setup.
output_bin = os.environ.get('CK_OUT_RAW_DATA', 'tmp-ck-output.bin')
output_json = output_bin.replace('bin', 'json')

dataset_path = os.environ.get('CK_DATASET_PATH', '')

weights_prefix = os.environ.get('CK_LSTM_WEIGHTS_PREFIX', '')
dataset_prefix = os.environ.get('CK_LSTM_DATASET_PREFIX', '')

op_id = os.environ.get('CK_LSTM_OP_ID', '')
sample_id = os.environ.get('CK_LSTM_SAMPLE_ID', '0').zfill(6)

layers = int(os.environ.get('CK_LSTM_LAYERS', '1'))
hidden_width = int(os.environ.get('CK_LSTM_HIDDEN_WIDTH', ''))
input_width = int(os.environ.get('CK_LSTM_INPUT_WIDTH', ''))

print_in_tensor = os.environ.get('CK_PRINT_IN_TENSOR', 'no') in [ 'yes', 'YES', 'ON', 'on', '1' ]
print_out_tensor = os.environ.get('CK_PRINT_OUT_TENSOR', 'no') in [ 'yes', 'YES', 'ON', 'on', '1' ]

weights_file = os.path.join(dataset_path, '{}{}-{}.W'.format(dataset_path, weights_prefix, op_id))
sample_file  = os.path.join(dataset_path, '{}{}-{}-{}.x'.format(dataset_path, dataset_prefix, op_id, sample_id))

sizeof_float32 = 4

# LOAD LSTM
lstm = torch.load(weights_file)

# LOAD DATA
input_data = torch.load(sample_file)

if print_in_tensor:
    print("Input:")
    pprint(input_data)
    print("")

logit_count, _, _ = input_data.size()

finish_setup_time = perf_counter()

# RUN THE TEST
output, _ = lstm(input_data, None)

finish_lstm_time = perf_counter()

# Print output as tensor.
if print_out_tensor:
    print("LSTM Output:")
    pprint(output)

# Convert output to flat list.
output_list = output.flatten().tolist()

# Dump output as binary.
with open(output_bin, 'wb') as output_file:
    output_file.write( struct.pack('f'*len(output_list), *output_list) )

# Dump output as JSON.
with open(output_json, 'w') as output_file:
    output_file.write( json.dumps(output_list, indent=2) )

# Dump timing and misc info.
height, batch, width = output.size()

timer_json = 'tmp-ck-timer.json'
with open(timer_json, 'w') as output_file:
    timer = {
        "execution_time": (finish_lstm_time - start_setup_time),
        "run_time_state": {
            "input_width": input_width,
            "hidden_width": hidden_width,
            "num_layers": layers,
            "logit_count": logit_count,
            "out_shape_N": batch,
            "out_shape_C": 1,
            "out_shape_H": height,
            "out_shape_W": width,
            "data_bits": sizeof_float32*8,
            "time_setup": (finish_setup_time - start_setup_time),
            "time_test": (finish_lstm_time - finish_setup_time)
        }
    }
    output_file.write( json.dumps(timer, indent=2) )
