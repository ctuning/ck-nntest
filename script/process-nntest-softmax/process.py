#
# Copyright (c) 2017 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#
# Convert raw output of a softmax test program to the CK format.
#
# Developer(s):
#   - Anton Lokhmotov, dividiti, 2017
#

import json
import os
import re
import struct
import time

# ******************************************************************************
def ck_preprocess(i):
    ck=i['ck_kernel']
    rt=i['run_time']

    meta=i['meta']
    env=i['env']

    return {'return':0}

# ******************************************************************************
def _flat_index(n, c, h, w, channels, height, width):
    return ((n * channels + c) * height + h) * width + w

# ******************************************************************************
def check_softmax_results(i):

    ck=i['ck_kernel']
    env=i['env']
    result=i['unpacked_output']

    dim_n = int(env['CK_IN_SHAPE_N'])
    dim_c = int(env['CK_IN_SHAPE_C'])
    dim_w = int(env['CK_IN_SHAPE_W'])
    dim_h = int(env['CK_IN_SHAPE_H'])
    threshold = float(env.get('CK_ABS_DIFF_THRESHOLD', 0.0))
    expected_sum = float(env.get('CK_SOFTMAX_BATCH_SUM', 1.0))

    ck.out('  (checking softmax values sanity, sum for each N should be ' + str(expected_sum) + ' with ' + str(threshold) + ' precision ...)')
    for n in range(dim_n):
        total = 0.0

        for c in range(dim_c):
            for w in range(dim_w):
                for h in range(dim_h):
                    v = result[_flat_index(n, c, h, w, dim_c, dim_h, dim_w)]
                    if 0 > v or v > expected_sum:
                        return {'return': 1, 'error': 'All values must be between 0 and ' + str(expected_sum)}
                    total += v
        ck.out('     * sum for N=' + str(n) + ' is ' + str(total))

        if abs(total - expected_sum) > threshold:
            return {'return': 2, 
                'error': 'Sum of all values for each N must be equal to 1, but for N=' + str(n) + ' it\'s ' + str(total)}

    return {'return': 0}

# ******************************************************************************
def ck_postprocess(i):
    ck=i['ck_kernel']
    rt=i['run_time']
    env=i['env']
    deps=i['deps']

    # Dictionary to return.
    d={}

    # Load xOpenME output.
    r=ck.load_json_file({'json_file':rt['fine_grain_timer_file']})
    if r['return']>0: return r
    d=r['dict']

    drts=d.get('run_time_state',{})

    # Save final environment variables (can be changed in the pipeline)
    d['env']={}
    for k in env:
        d['env'][k]=env[k]

#    d['env']['CK_IN_SHAPE_N']=env.get('CK_IN_SHAPE_N','')
#    d['env']['CK_IN_SHAPE_C']=env.get('CK_IN_SHAPE_C','')
#    d['env']['CK_IN_SHAPE_H']=env.get('CK_IN_SHAPE_H','')
#    d['env']['CK_IN_SHAPE_W']=env.get('CK_IN_SHAPE_W','')
#    d['env']['CK_DATASET_FILENAME']=env.get('CK_DATASET_FILENAME','')
#    d['env']['CK_ABS_DIFF_THRESHOLD']=env.get('CK_ABS_DIFF_THRESHOLD','')
#    d['env']['CK_OUT_RAW_DATA']=env.get('CK_OUT_RAW_DATA','')
#    d['env']['CK_SEED']=env.get('CK_SEED','')

#    # Load and concatenate stdout and stderr.
#    lst=[]
#    stdout=rt['run_cmd_out1']
#    stderr=rt['run_cmd_out2']
#    if os.path.isfile(stdout):
#       r=ck.load_text_file({'text_file':stdout,'split_to_list':'yes'})
#       if r['return']>0: return r
#       lst+=r['lst']
#    if os.path.isfile(stderr):
#       r=ck.load_text_file({'text_file':stderr,'split_to_list':'yes'})
#       if r['return']>0: return r
#       lst+=r['lst']
#    for line in lst:
#        # TODO: match something someday.

    rr={}
    rr['return']=0

    json_out_file = 'tmp-ck-output.json'
    # Call process output vector
    r=ck.access({'action':'run', 'module_uoa':'script', 'data_uoa':'process-nntest', 
                 'code':'output', 'func':'process', 
                 'dict':{'file_out': json_out_file, 
                         'data':d, 'env':env, 'deps':deps}})
    if r['return']>0: return r

    # Sanity check on non-fingerprinted data !
    unpacked_output=r['unpacked_output']

    # Check sum only if CK_DIFF_MIN==0
    x=env.get('CK_DIFF_MIN','')
    if x=='': x='0'
    if int(x)==0:
       dt=time.time()

       r=check_softmax_results({'env': env, 'unpacked_output': unpacked_output, 'ck_kernel': ck})
       if r['return']>0: return r

       ck.out('Debug time (sanity check): '+str(time.time()-dt)+' sec.')

    # Call dvdt prof script
    r=ck.access({'action':'run', 'module_uoa':'script', 'data_uoa':'ctuning.process.dvdt-prof', 
                 'code':'dvdt_prof', 'func':'process', 
                 'dict':{'file_in':rt['run_cmd_out1'], 'file_out':'tmp-dvdt-prof.json', 
                         'data':d, 'env':env, 'deps':deps}})
    if r['return']>0: return r

    # Call MALI HWC collector
    r=ck.access({'action':'run', 'module_uoa':'script', 'data_uoa': 'mali-hwc',
                 'code':'process', 'func':'read',
                 'dict':{'data':d, 'env':env, 'deps':deps, 'continue_if_no_file':'yes'}})
    if r['return']==0:
       if env.get('CK_ADD_RAW_MALI_HWC','').lower()=='yes':
          d['mali_hwc']=r['hwc']

    # Process total time
    total_time=0.0
    if drts.get('time_setup',0.0)!=0.0: total_time+=drts['time_setup']
    if drts.get('time_test',0.0)!=0.0: total_time+=drts['time_test']

    d['execution_time']=total_time
    d['execution_time_kernel_0']=total_time

    if d.get('post_processed','')=='yes':
        r=ck.save_json_to_file({'json_file':rt['fine_grain_timer_file'], 'dict':d, 'sort_keys':'yes'})
        if r['return']>0: return r
    else:
        rr['return']=1
        rr['error']='failed to find required info in test output!'

    return rr

def ck_check_output(i):
    ck=i['ck_kernel']

    env=i.get('env',{})

    r=ck.access({'action':'check_numerical',
                 'module_uoa':'program.output',
                 'file1':i['file1'],
                 'file2':i['file2'],
                 'abs_threshold':env.get('CK_ABS_DIFF_THRESHOLD','')})

    return r
