#
# Copyright (c) 2017 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#
# Convert raw output of a fc test program to the CK format.
#
# Developer(s):
#   - Anton Lokhmotov, dividiti, 2017
#

import json
import os
import re
import struct

def ck_preprocess(i):
    ck=i['ck_kernel']
    rt=i['run_time']

    meta=i['meta']
    env=i['env']

    return {'return':0}

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

    rr={}
    rr['return']=0

    # Call process output vector
    r=ck.access({'action':'run', 'module_uoa':'script', 'data_uoa':'process-nntest',
                 'code':'output', 'func':'process',
                 'dict':{'file_in':d['env']['CK_OUT_RAW_DATA'],
                         'file_out':'tmp-ck-output.json',
                         'data':d, 'env':env, 'deps':deps}})
    if r['return']>0: return r

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

# Do not add anything here!
