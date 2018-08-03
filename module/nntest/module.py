#
# Copyright (c) 2017 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

#
# Developer(s):
#   - Anton Lokhmotov, dividiti, 2017
#   - Grigori Fursin, cTuning foundation, 2017
#

import json
import copy
import os
from time import strftime, gmtime

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

sep='==========================================================================='

form_name='nntest_web_form'
onchange='document.'+form_name+'.submit();'
hextra=''

selector=[
          {'name':'Species', 'key':'species'},
          {'name':'Type', 'key':'prog_type'},
          {'name':'Test', 'key':'prog_uoa'},
          {'name':'Dataset', 'key':'dataset_uoa'},
          {'name':'Platform', 'key':'plat_name', 'new_line':'yes'},
          {'name':'Time stamp', 'key':'timestamp'}
         ]

selector2=[
           {'name':'OpenCL driver', 'key':'##features#gpgpu@0#gpgpu_misc#opencl c version#min', 'skip_empty':'yes', 
                              'extra_key':'##features#gpgpu@0#gpgpu_misc#opencl_c_version#min'},
           {'name':'Dataset file', 'key':'##choices#env#CK_DATASET_FILENAME#min', 'new_line':'yes'},
           {'name':'Batch size', 'key':"##choices#env#CK_IN_SHAPE_N#min", 'type':'int'},
          ]

selector3=[
           {'name':'Plot time in', 'key':'plot_time_in'}
          ]

wchoices3={
            'plot_time_in':[
              {'name':'sec', 'value':'sec'},
              {'name':'ms', 'value':'ms'}
            ]}

k_hi_uid='highlight_behavior_uid'
k_hi_user='highlight_by_user'
k_view_all='all'

hidden_keys=[k_hi_uid, k_hi_user, k_view_all]

view_cache=[
  "##choices#env#CK_ABS_DIFF_THRESHOLD#min",
  "##choices#env#CK_DATASET_FILENAME#min",
  "##choices#env#CK_IN_SHAPE_C#min",
  "##choices#env#CK_IN_SHAPE_H#min",
  "##choices#env#CK_IN_SHAPE_N#min",
  "##choices#env#CK_IN_SHAPE_W#min",
  "##choices#env#CK_POOL_KERNEL#min",
  "##choices#env#CK_POOL_PAD_SCHEME#min",
  "##choices#env#CK_POOL_STRIDE#min",
  "##choices#env#CK_SEED#min",
  "##pipeline_state#fail_bool#min",
  "##pipeline_state#fail_reason#min",
  "##characteristics#compile#compilation_success_bool#min",
  "##characteristics#run#run_success_bool#min",
  "##characteristics#run#output_check_failed_bool#min",
  "##characteristics#run#execution_time#min",
  "##characteristics#run#execution_time#max",
  "##characteristics#run#run_time_state#time_test#min",
  "##characteristics#run#run_time_state#time_test#max",
  "##characteristics#run#run_time_state#time_setup#min",
  "##characteristics#run#run_time_state#time_setup#max",
  "##features#gpgpu@0#gpgpu_misc#opencl c version#min"
]

table_view=[
  {"key":"##meta#prog_uoa", "name":"Test", "skip_if_key_in_input":"prog_uoa"},
  {"key":"##meta#dataset_uoa", "name":"Dataset", "skip_if_key_in_input":"dataset_uoa"},
  {"key":"##meta#plat_name", "name":"Platform", "skip_if_key_in_input":"plat_name"},
  {"key":"##meta#timestamp", "name":"Time stamp", "skip_if_key_in_input":"timestamp"},
  {"key":"##meta#versions", "name":"Versions", "json_and_pre":"yes", "align":"left"},
  {"key":"##choices#env#", "name":"Environment", "starts_with":"yes", "align":"left"},
  {"key":"##characteristics#run#execution_time#min", "name":"Total time (sec. min/max)", "check_extra_key":"max", "format":"%.2e"},
  {"key":"##characteristics#run#run_time_state#time_setup#min", "name":"Setup time (sec. min/max)", "check_extra_key":"max", "format":"%.2e"},
  {"key":"##characteristics#run#run_time_state#time_test#min", "name":"Test time (sec. min/max)", "check_extra_key":"max", "format":"%.2e"},
  {"key":"##meta#user", "name":"User"},
  {"key":"##extra#html_replay_button", "name":"Replay"}
]

pass_vars_to_autotune=[
 'skip_output_validation',
 'output_validation_repo',
 'overwrite_reference_output'
]

prune_first_level=20
prune_second_level=200

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# show stats

def show(i):
    """
    Input:  {
               (crowd_module_uoa)       - if rendered from experiment crowdsourcing
               (crowd_key)              - add extra name to Web keys to avoid overlapping with original crowdsourcing HTML
               (crowd_on_change)        - reuse onchange doc from original crowdsourcing HTML

               (highlight_behavior_uid) - highlight specific result (behavior)!
               (highlight_by_user)      - highlight all results from a given user

               (refresh_cache)          - if 'yes', refresh view cache
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy
    import time

    # Preparing various parameters to render HTML dashboard
    st=''

    view_all=i.get(k_view_all,'')

    cmuoa=i.get('crowd_module_uoa','')
    ckey=i.get('crowd_key','')

    if 'reset_'+form_name in i: reset=True
    else: reset=False

    if 'all_choices_'+form_name in i: all_choices=True
    else: all_choices=False

    debug=(i.get('debug','')=='yes')
#    debug=True

    conc=i.get('crowd_on_change','')
    if conc=='':
        conc=onchange

    hi_uid=i.get(k_hi_uid,'')
    hi_user=i.get(k_hi_user,'')

    refresh_cache=i.get('refresh_cache','')

    bd='<div style="background-color:#bfffbf;margin:5px;">'

#    h='<hr>\n'
    h='<center>\n'
    h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

    h+=hextra

#    h+='<hr>\n'
#    h+='<br>\n'

    # Check host URL prefix and default module/action *********************************************
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':i.get('template','')})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    url+='action=index&module_uoa=wfe&native_action='+action+'&'+'native_module_uoa='+muoa
    url1=url

    # Check and add hidden keys ***************************************************
    h+='\n\n'

    for k in hidden_keys:
        if i.get(k,'')!='':
           h+='<input type="hidden" name="'+k+'" value="'+i[k]+'">\n'

    h+='\n\n'

    # Prepare first level of selection with pruning ***********************************************
    r=ck.access({'action':'prepare_selector',
                 'module_uoa':cfg['module_deps']['experiment'],
                 'original_input':i,
                 'tags':'nntest',
                 'debug': debug,
                 'selector':selector,
                 'crowd_key':ckey,
                 'crowd_on_change':conc,
                 'url1':url1,
                 'form_name':form_name,
                 'background_div':bd,
                 'skip_html_selector':'yes'})
    if r['return']>0: return r

    olst=r['lst'] # original list (if all_choices)
    plst=r['pruned_lst']

    # Sort list ***********************************************************************************
    dt=time.time()
    splst=sorted(plst, key=lambda x: (
        x.get('meta',{}).get('meta',{}).get('prog_uoa',''), 
        x.get('meta',{}).get('meta',{}).get('dataset_uoa',''), 
        x.get('meta',{}).get('meta',{}).get('plat_name',''), 
        x.get('meta',{}).get('meta',{}).get('timestamp','')
        ))

    if debug: h+='\n<p>Debug time (sorting table): '+str(time.time()-dt)+' sec.<p>\n'

    # Prune list **********************************************************************************
    len_plst=len(plst)
    if len_plst>prune_first_level:
       plst=plst[:prune_first_level]

       h+='\n<i>Showing '+str(prune_first_level)+' of '+str(len_plst)+' entries ...</i><br>\n'

    # Prepare and cache results for the table
    r=ck.access({'action':'get_and_cache_results',
                 'module_uoa':cfg['module_deps']['experiment'],
                 'lst':splst,
                 'cache_uid':work['self_module_uid'],
                 'refresh_cache':refresh_cache,
                 'view_cache':view_cache,
                 'table_view':table_view})
    if r['return']>0: return 
    table=r['table']

    # Prepare second level of selection with pruning ***********************************************
    r=ck.access({'action':'prepare_selector',
                 'module_uoa':cfg['module_deps']['experiment'],
                 'original_input':i,
                 'lst':table,
                 'skip_meta_key':'yes',
                 'debug': debug,
                 'selector':selector2,
                 'crowd_key':ckey,
                 'crowd_on_change':conc,
                 'url1':url1,
                 'form_name':form_name,
                 'skip_form_init':'yes',
                 'background_div':bd})
    if r['return']>0: return r

    h2=r['html']
    table=r['pruned_lst']

    choices2=r['choices']
    wchoices2=r['wchoices']

    # Extra fields (customized for this module) *****************************************************************************
    for row in table:
        duoa=row.get('##data_uid','')
        dpoint=row.get('##point_uid','')

        x=''
        if duoa!='' and dpoint!='':
           x='ck replay experiment:'+duoa+' --point='+str(dpoint)
           y=ck.cfg.get('add_extra_to_replay','')
           if y!='':x+=' '+y

        row['##extra#html_replay_button']='<input type="button" class="ck_small_button" onClick="copyToClipboard(\''+x+'\');" value="Copy to clipboard">\n'

    # Prune first list based on second selection*****************************************************************************
    if all_choices:
       nsplst=olst
    elif reset:
       nsplst=splst
    else:
       all_uid=[]
       for row in table:
           duid=row['##data_uid']
           if duid!='' and duid not in all_uid:
              all_uid.append(duid)

       nsplst=[]
       for q in splst:
           if q['data_uid'] in all_uid:
              nsplst.append(q)

    # Check if too many *****************************************************************************************************
    ltable=len(table)
    min_view=False

    hx=''
    if ltable==0:
        h+='<b>No results found!</b>'
        return {'return':0, 'html':h, 'style':st}

    elif ltable>prune_second_level and view_all!='yes':
       table=table[:prune_second_level]

       hx='\n<i>Showing '+str(prune_second_level)+' of '+str(ltable)+' entries ...</i><br>\n'

    # Get unique values and create html selector 1 (after selector 2)
    r=ck.access({'action':'get_unique_keys_from_list',
                 'module_uoa':cfg['module_deps']['experiment'],
                 'lst':nsplst,
                 'selector':selector,
                 'crowd_key':ckey,
                 'original_input':i})
    if r['return']>0: return 

    choices1=r['choices']
    wchoices1=r['wchoices']

    # Prepare selector 1  (based on choices from selector 2)
    r=ck.access({'action':'prepare_html_selector',
                 'module_uoa':cfg['module_deps']['experiment'],
                 'start_form':'yes',
                 'url1':url1,
                 'form_name':form_name,
                 'background_div':bd,
                 'selector':selector,
                 'crowd_key':ckey,
                 'crowd_on_change':conc,
                 'wchoices':wchoices1,
                 'original_input':i})
    if r['return']>0: return r
    h1=r['html']

    h+=h1+'\n'+h2

    ltable=len(table)
    min_view=False

    if ltable==0:
        h+='<b>No results found!</b>'
        return {'return':0, 'html':h, 'style':st}

    elif ltable>prune_second_level and view_all!='yes':
       table=table[:prune_second_level]

       h+='\n<i>Showing '+str(prune_second_level)+' of '+str(ltable)+' entries ...</i><br>\n'

    # Prepare selector 3 (without pruning - about tables and graphs)
    if len(selector3)>0:
       r=ck.access({'action':'prepare_html_selector',
                    'module_uoa':cfg['module_deps']['experiment'],
                    'start_form':'no',
                    'url1':url1,
                    'form_name':form_name,
                    'background_div':bd,
                    'selector':selector3,
                    'crowd_key':ckey,
                    'crowd_on_change':conc,
                    'wchoices':wchoices3,
                    'original_input':i,
                    'add_reset':'yes'})
       if r['return']>0: return r
       h+='\n'+r['html']+'\n'

    h+='\n'+hx+'\n'

    # Prepare graph *********************************************************************************************************
    bgraph={'0':[]}
    igraph={'0':[]}

    stable=sorted(table, key=lambda row: (
        ck.safe_float(row.get('##characteristics#run#execution_time#min',None),0.0)
        ))

    xtscale=i.get('plot_time_in','')
    tscale=1.0
    if xtscale=='ms':
       tscale=1000.0

    ix=0
    for row in stable:
        ix+=1
        six=str(ix)

        x=row.get('##characteristics#run#execution_time#min',None)
        if type(x)!=float: 
           tmin=0.0
        else:
           tmin=x*tscale

        x=row.get('##characteristics#run#execution_time#max',None)
        if type(x)!=float: 
           tmax=tmin
        else:
           tmax=x*tscale

        tdelta=0.0
        if tmin!=0.0 and tmax!=0.0:
           tdelta=tmax-tmin

        bgraph['0'].append([ix,tmin, tmin+tdelta])

        raw_data_url=url0#+'wcid='+x+':'+duid

#        igraph['0'].append({'size':sizem, 'color':xcol, 'features':row, 'url':'', 'url_ext':raw_data_url})
        igraph['0'].append({'size':4, 'features':row, 'anchor':'id'+six}) #, 'url':'', 'url_ext':''})


    if len(bgraph['0'])>0:
       dt=time.time()
       ii={'action':'plot',
           'module_uoa':cfg['module_deps']['graph'],

           "table":bgraph,
           "table_info":igraph,

           "xmin":0,
           "ymin":0,

           "ignore_point_if_none":"yes",

           "plot_type":"d3_2d_scatter",

           "display_y_error_bar2":"yes",

           "title":"Powered by Collective Knowledge",

           "x_ticks_period":10,

           "axis_x_desc":"Experiment",
           "axis_y_desc":"Total kernel execution time ("+xtscale+")",

           "plot_grid":"yes",

           "d3_div":"ck_interactive",

           "image_width":"900",
           "image_height":"400",

           "wfe_url":url0}

       r=ck.access(ii)
       if r['return']==0:
          x=r.get('html','')
          if x!='':
             st+=r.get('style','')

             h+='<center>\n'
             h+='<div id="ck_box_with_shadow" style="width:940px;">\n'
             h+=' <div id="ck_interactive" style="text-align:center;font-size:11px;">\n'
             h+=x+'\n'
             h+=' </div>\n'
             h+='</div>\n'
             h+='</center>\n'
             h+='<br>\n'

    # In the future, we may want to use Django + numpy here
    # Prepare table header ******************************************************************
    bgc='dfffdf'
    bg=' style="background-color:#'+bgc+';"'
    bg1=' style="background-color:#bfffbf;"'
    bg2=' style="background-color:#afffaf;"'

    h+='<small><table border="1" cellpadding="7" cellspacing="0">\n'

    ha='align="$#align#$" valign="top"'

    # Prepare table header *****************************************************************
    h+='  <tr style="background-color:#dddddd">\n'

    h+='   <td '+ha.replace('$#align#$','center')+'><b>#</b></td>\n'

    for tv in table_view:
        k=tv['key']

        align=tv.get('align','')
        if align=='': align='center'

        skip=False

        kk=tv.get('skip_if_key_in_input','')
        if kk!='' and i.get(kk,'')!='':
           skip=True

        if not skip:
           n=tv.get('name','')
           if n=='': n=k

           h+='   <td '+ha.replace('$#align#$',align)+'><b>'+n+'</b></td>\n'

    h+='  </tr>\n'

    # Draw table ***************************************************************************
    dt=time.time()
    ix=0
    for q in table:
        ix+=1
        six=str(ix)

        # Check colors
        bgx=bg
        bgx1=bg1
        bgx2=bg2
        if (hi_uid!='' and duid==hi_uid) or (hi_user!='' and hi_user==user):
           bgx=' style="background-color:#ffcf7f"'
           bgx1=' style="background-color:#ffbf5f"'
           bgx2=' style="background-color:#ffaf2f"'

        # Starting raw ***************************************
        h+='  <tr'+bgx+'>\n'

        h+='   <td '+ha.replace('$#align#$','center')+'><a name="id'+six+'" id="id'+six+'">'+six+'</a></td>\n'

        for tv in table_view:
            k=tv['key']

            align=tv.get('align','')
            if align=='': align='center'

            skip=False

            kk=tv.get('skip_if_key_in_input','')
            if kk!='' and i.get(kk,'')!='':
               skip=True

            if not skip:
               v=q.get(k,'')

               format=tv.get('format','')
               if format!='' and v!='' and v!=None:
                  v=format % float(v)

               if tv.get('json_and_pre','')=='yes' and v!='' and type(v)==dict:
                  v1=''
                  for kx in v:
                      v1+=kx+'='+str(v[kx])+'<br>'
                  v=v1

#                  import json
#                  v='<pre>'+json.dumps(v, indent=2, sort_keys=True)+'</pre>'

               if tv.get('starts_with','')=='yes':
                  v=''
                  for kx in sorted(q):
                      if kx!=k and kx.startswith(k):
                         v+=kx[len(k):-4]+'='+str(q.get(kx,''))+'<br>'

               v=str(v)

               cek=tv.get('check_extra_key','')
               if cek!='':
                  j=k.rfind('#')
                  if j>0:
                     k1=k[:j+1]+cek

                     v1=q.get(k1,'')

                     if format!='' and v1!='' and v1!=None:
                        v1=format % float(v1)

                     v1=str(v1)

                     if v1!='':
                        v+=' .. '+v1

               h+='   <td '+ha.replace('$#align#$',align)+'>'+v+'</td>\n'

        h+='  <tr>\n'

    h+='</table></small>\n'
    h+='</center>\n'

    if debug: h+='\n<p>Debug time (preparing html of a table): '+str(time.time()-dt)+' sec.<p>\n'

    if cmuoa=='':
        h+='</form>\n'

    # Add <br> to be able to select anchor on top
    for j in range(0,30):
        h+='<br>\n'

    return {'return':0, 'html':h, 'style':st}

##############################################################################
# run tests

def run(i):
    """
    Input:  {
              (user)                - force different user ID/email for demos

              (data_uoa)            - program UOA to benchmark it
              (tags)                - prune programs by tags (opencl, cpu, armcl, caffe, tensorflow ...)
              (species)             - list of species

              (cmd_key)             - prune by CMD key, otherwise trying all
              (dataset_uoa)         - prune by dataset UOA, otherwise trying all
              (dataset_file)        - prune by dataset filename, otherwise trying all
              (library_uoa)         - if !=', specify lib UOA to use

              (pause_if_fail)       - if pipeline fails, ask to press Enter
                                      (useful to analyze which flags fail during compiler flag autotuning)

              (pause)               - if 'yes', pause before compiling and running test

              (see_tests)           - show all tests to be performed, but do not run them 
              (dry_run)             - if 'yes', prepare pipeline and resolve dependencies, but do not run it (testing)

              (skip_deps_cache)     - if 'yes', do not cache deps
              (deps_cache)          - name of cache for deps (in local:tmp:cache-deps-nntest-{cache_deps}) and reuse them for all tests
                                      (by tags) (NOT COMPLETELY FINISHED - not recorded at the end - TBD)
              (refresh_deps_cache)  - if 'yes', clean entry with deps cache and start again

              (repetitions)         - statistical repetitions (default=1), for now statistical analysis is not used (TBD)

              (mali_hwc)            - if 'yes', dump MALI hardware counters

              (dvdt_prof)           - if 'yes', use dvdt_prof to collect opencl stats (only for opencl programs)
              (flags)               - pass flags for compiler compilation of tests (-O3 by default)

              (iterations)          - autotuning iterations (-1 by default, i.e. all possible such as batch size)

              (custom_autotuning)   - dict to customize autotuning (can be added via external file in cmd @some-name.json)
              (autotune_id)         - get autotune/{autotune_id}.json from program entry to start autotuning

              (no_record)           - if "yes", do not record experiments ("no" by default, i.e. experiments will be recorded)
              (record_uoa)          - use this experiment UOA to record all data to 
              (timestamp)           - use this instead of timestamp
              (record_repo)         - if !='', record to this repo (local by default)

              (skip_output_validation)        - skip validation of output (dangerous during auto-tuning -
                                                  some optimizations may break semantics or change accuracy)
              (output_validation_repo)        - output validation repo UOA (when recording new output)
              (overwrite_reference_output)    - if 'yes', overwrite reference output (useful if broken)

              (update_platform_init)          - update platform.init scripts (ask user)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    i['local']='yes'

    return crowdsource(i)

##############################################################################
# crowdsource nntest

NOT_FOUND_ERROR = 16

class CKException(Exception):
    def __init__(self, ck_result):
        self.ck_result = ck_result

    @staticmethod
    def throw(message, code=1):
        raise CKException({'return': code, 'error': message})


def yes_no(bool_flag):
    return 'yes' if bool_flag else 'no'


def ck_access(params_json, skip_error_codes = []):
    '''
    Performs call to ck-kernel and raises an exception when an error.
    Returns the result of ck-operation.
    '''
    r = ck.access(params_json)
    error_code = r['return']
    if error_code > 0 and not (error_code in skip_error_codes):
        ck.out('CK error details:')
        ck.out('    action: ' + params_json.get('action'))
        ck.out('    param: module_uoa=' + params_json.get('module_uoa'))
        ck.out('    param: data_uoa=' + params_json.get('data_uoa'))
        import traceback
        stack_lines = traceback.format_stack()
        if len(stack_lines) >= 2:
            # The last line of the stack is the current line (`traceback.format_stack`),
            # so we need a line before the last - location of call of `ck_access` function.
            location_and_code = stack_lines[-2].strip().split('\n')
            ck.out('    location: ' + location_and_code[0].strip())
            if len(location_and_code) > 1:
                ck.out('    code: ' + location_and_code[1].strip())
        raise CKException(r)
    return r


def convert_to_flat_dict(i):
    '''
    Check if any key in input dictionary has . and convert to dict (for example deps.xyz or env.xyz) 
    '''
    for key in i:
        if '.' in key:
            value = i[key]
            del(i[key])
            new_key = '##' + key.replace('.', '#')
            r = ck.set_by_flat_key({'dict': i, 'key': new_key, 'value': value})
            if r['return'] > 0:
                raise CKException(r)


def get_user_from_module_config():
    r = ck_access({'action': 'load',
                   'module_uoa': 'module',
                   'data_uoa': cfg['module_deps']['program.optimization']})
    mcfg = r['dict']

    r = ck_access({'action': 'load',
                    'module_uoa': mcfg['module_deps']['cfg'],
                    'data_uoa': mcfg['cfg_uoa']
                }, skip_error_codes = [NOT_FOUND_ERROR])

    if r['return'] != NOT_FOUND_ERROR:
        return r['dict'].get('user_email','')

    return ''


def get_programs(data_uoa, tags_list, species_uids):
    r = ck_access({'action':'search',
                   'module_uoa': cfg['module_deps']['program'],
                   'data_uoa': data_uoa,
                   'tags': ','.join(tags_list),
                   'add_meta': 'yes'})
    programs = r['lst']

    # it's possible to skip some tests
    programs = [p for p in programs if p['meta'].get('skip_from_tests') != 'yes']

    if species_uids:
        filtered = []
        for p in programs:
            program_species = p['meta'].get('species',[])
            for s in species_uids:
                if s in program_species:
                    filtered.append(p)
                    break
        programs = filtered
    if not programs:
        CKException.throw('no programs selected')
    return sorted(programs, key = lambda p: p.get('data_uoa',''))


def load_lib_envs_sorted_by_id(library_env_uoas):
    '''
    Loads all library envs and returns them as a list sorted by `lib_id`
    '''
    lib_envs = []
    for uoa in library_env_uoas:
        if not uoa:
            lib_envs.append({})
        else:
            lib_envs.append(ck_access({'action': 'load',
                                       'module_uoa': 'env',
                                       'data_uoa': uoa}))

    return sorted(lib_envs, key = lambda x: x.get('dict',{})
                                             .get('customize',{})
                                             .get('lib_id',99999))


def get_versions_of_all_deps(deps):
    r = ck_access({'action': 'get_all_versions_in_deps',
                   'module_uoa': cfg['module_deps']['env'],
                   'deps': deps})
    return r['versions']


def resolve_all_deps(deps, platform):
    r = ck_access({'action': 'resolve',
                   'module_uoa': 'env',
                   'host_os': platform.host_os,
                   'target_os': platform.target_os,
                   'device_id': platform.device_id,
                   'deps': deps})
    return r


class ActionOptions:
    def __init__(self, i):
        self.data_uoa = i.get('data_uoa','')
        self.lib_uoa = i.get('library_uoa','')
        self.species = i.get('species','')
        self.cmd_key = i.get('cmd_key','')
        self.target = i.get('target','')
        self.user = i.get('user','')

        files = i.get('dataset_file','')
        self.dataset_files = files.split(',') if (',' in files) else []
        self.dataset_uoa = i.get('dataset_uoa','')

        self.tags = self.__get_input_tags(i)
        self.autotune_id = str(i.get('autotune_id',''))
        self.timestamp = i.get('timestamp','')

        self.local = i.get('local') == 'yes'

        self.cache_deps = i.get('cache_deps') or 'default'
        self.reuse_deps = i.get('skip_deps_cache') != 'yes'
        self.refresh_deps_cache = i.get('refresh_deps_cache') == 'yes'

        self.record = i.get('no_record') != 'yes'
        self.record_uoa = i.get('record_uoa','')
        self.record_repo = i.get('record_repo', '')
        self.exchange_repo = i.get('exchange_repo','')
        self.exchange_subrepo = i.get('exchange_subrepo','')

        self.dry_run = i.get('dry_run') == 'yes'
        self.mali_hwc = i.get('mali_hwc') == 'yes'
        self.dvdt_prof = i.get('dvdt_prof') == 'yes'
        self.see_tests = i.get('see_tests') == 'yes'
        self.pause = i.get('pause') == 'yes'
        self.pause_if_fail = i.get('pause_if_fail') == 'yes'
        self.console = i.get('out') == 'con'

        self.flags = i.get('flags') or '-O3'
        self.env = i.get('env',{})

        self.num_repetitions = int(i.get('repetitions') or 3)
        self.iterations = int(i.get('repetitions') or -1)
        if i.get('overwrite_reference_output','') == 'yes':
            self.iterations = 1

        self.custom_autotuning = i.get('custom_autotuning',{})
        
    def __get_input_tags(self, i):
        tags = ['nntest']
        if 'tags' in i:
            for tag in i['tags'].split(','):
                t = tag.strip()
                # Check opencl, cuda and cpu keywoards and add `v`
                if t == 'opencl': t = 'vopencl'
                elif x == 'cuda': t = 'vcuda'
                elif t == 'cpu': t = 'vcpu'
                tags.append(t)
        return tags

    def get_species_uids(self):
        uids = []
        for s in self.species.split(','):
            s = s.strip()
            if s:
                r = ck_access({'action':'load',
                               'module_uoa': cfg['module_deps']['program.species'],
                               'data_uoa': s})
                uids.append(r['data_uid'])
        return uids


class TestConfig:
    def __init__(self, options):
        self.user = None # to be initialized externally
        self.__init_timestamps()
        self.__init_repo_names(options)
        self.__init_deps_cache(options)

    def __init_timestamps(self):
        '''
        Init timestamp and striped timestamp
        '''
        r = ck.get_current_date_time({})
        if r['return'] > 0:
            raise CKException(r)
        t = r['iso_datetime']
        
        j = t.find('.')
        if j > 0: t = t[:j]

        self.timestamp = t
        self.stimestamp = t.replace('-','').replace(':','').replace('T','')

    def __init_repo_names(self, options):
        '''
        Check working repository (possibly remote)
        '''
        if options.local: 
            self.exchange_repo = 'local'
            self.exchange_subrepo = ''
        else:
            self.exchange_repo = \
                options.exchange_repo or \
                cfg.get('default_exchange_repo_uoa','') or \
                ck.cfg.get('default_exchange_repo_uoa','')
            self.exchange_subrepo = \
                options.exchange_subrepo or \
                cfg.get('default_exchange_subrepo_uoa','') or \
                ck.cfg.get('default_exchange_subrepo_uoa','')
        if options.record_repo:
            self.exchange_repo = options.record_repo

    def __init_deps_cache(self, options):
        self.deps_cache = []
        deps_cache_uoa = 'deps-cache-{}-{}'.format(work['self_module_uoa'], options.cache_deps)

        def refresh_deps_cache():
            ck_access({'action':'update',
                       'module_uoa': cfg['module_deps']['tmp'],
                       'data_uoa': deps_cache_uoa,
                       'dict': { 'cache': [] },
                       'substitute': 'yes',
                       'ignore_update': 'yes'})

        if options.refresh_deps_cache:
            refresh_deps_cache()
        elif options.reuse_deps:
            r = ck_access({'action': 'load',
                           'module_uoa': cfg['module_deps']['tmp'],
                           'data_uoa': deps_cache_uoa},
                           skip_error_codes = [NOT_FOUND_ERROR])
            if r['return'] != NOT_FOUND_ERROR:
                self.deps_cache = r['dict'].get('cache',[])
            else:
                refresh_deps_cache()


class PlatformInfo:
    def __init__(self, action_params_json, config):
        self.user = None

        info = action_params_json.get('platform_info',{})
        if not info:
            params_json = copy.deepcopy(action_params_json)
            params_json.update({
                'action': 'initialize',
                'module_uoa': cfg['module_deps']['program.optimization'],
                'data_uoa': 'caffe', # TODO why `caffe` here? comment needed
                'exchange_repo': config.exchange_repo,
                'exchange_subrepo': config.exchange_subrepo,
                'skip_welcome': 'yes',
                'skip_log_wait': 'yes',
                'crowdtuning_type': 'nntest',
                'update_platform_init': action_params_json.get('update_platform_init',''),
                'local_autotuning': action_params_json.get('local','')
            })
            r = ck_access(params_json)
            info = r['platform_info']
            self.user = r.get('user','')

        self.host_os = info['host_os_uoa']
        self.host_os_uid = info['host_os_uid']
        self.target_os = info['os_uoa']
        self.target_os_uid = info['os_uid']
        self.device_id = info['device_id']
        self.features = info.get('features',{})
        self.name = self.features.get('platform', {}).get('name','')
        self.uid = self.features.get('platform_uid')
        self.os_name = self.features.get('os',{}).get('name','')
        self.os_uid = self.features.get('os_uid','')
        self.cpu_abi = self.features.get('cpu',{}).get('cpu_abi','')
        self.cpu_name = self.features.get('cpu',{}).get('name','') or ('unknown-' + self.cpu_abi)
        self.cpu_uid = self.features.get('cpu_uid','')
        self.gpu_name = self.features.get('gpu',{}).get('name','')
        self.gpgpu_name = self.features.get('gpgpu',{}).get('name','')
        self.gpgpu_vendor = self.features.get('gpgpu',{}).get('vendor','')
        self.gpgpu_name2 = (self.gpgpu_vendor + ' ' + self.gpgpu_name) if self.gpgpu_vendor else self.gpgpu_name
        self.opencl_version = self.features.get('gpgpu_misc',{}).get('opencl c version','')


class Program:
    def __init__(self, p):
        self.uoa = p['data_uoa']
        self.uid = p['data_uid']
        self.meta = p['meta']
        self.path = p['path']
        self.compile_deps = self.meta.get('compile_deps',{})
        self.autotuning = self.meta.get('autotuning',{})
        
        self.commands = self.meta.get('run_cmds',{})
        if not self.commands:
            CKException.throw('no CMD for run in program {} ({})'.format(self.uoa, self.uid))

        # Init program type from tags
        tags = self.meta.get('tags',[])
        if 'vopencl' in tags: self.type = 'opencl'
        elif 'vcuda' in tags: self.type = 'cuda'
        else: self.type = 'cpu'

        # Comma separated species string the program belongs to (to prepare experiment tags)
        self.species_uoas_str = self.__make_species_uoas_str()

    def __make_species_uoas_str(self):
        uoas = []
        for s in self.meta.get('species', []):
            r = ck_access({'action': 'load',
                            'module_uoa': cfg['module_deps']['program.species'],
                            'data_uoa': s})
            uoas.append(r['data_uoa'])
        return ','.join(uoas)

    def get_cmd_keys(self, options):
        # Do process only key given in the input
        if options.cmd_key:
            return [k for k in self.commands if k == options.cmd_key]
        # Ignore development keys
        return sorted([k for k in self.commands if not k.startswith('dev')])

    def get_lib_env_uoas(self, platform):
        '''
        Resolve library environment UOA(s) (don't use cache to get all choices)
        '''
        lib = self.compile_deps.get('library')
        # Empty for at least one iteration even if library is not used
        if not lib: return [''] 

        r = ck_access({'action': 'resolve',
                        'module_uoa': cfg['module_deps']['env'],
                        'host_os': platform.host_os,
                        'target_os': platform.target_os,
                        'device_id': platform.device_id,
                        'deps': {'library': copy.deepcopy(lib)}
                    })
        uoas = r['deps']['library'].get('choices',[])
        if not uoas:
            # Check that maybe 1 env was installed during resolving
            x = r.get('deps',{}).get('library',{}).get('uoa','')
            if x:
                uoas.append(x)
        if not uoas:
            raise CKException.throw('expected at least one library environment')
        return uoas

    def get_autotuning_from_file(self, autotune_id):
        '''
        Load autotuning parameters from json file in program's directory
        '''
        if autotune_id:
            filename = os.path.join(self.path, 'autotune', autotune_id+'.json')
            if os.path.isfile(filename):
                r = ck.load_json_file({'json_file': filename})
                if r['return'] > 0:
                    raise CKException(r)
                return r['dict']
        return {}


class ProgramCommand:
    '''
    Meta related to the selected command line
    '''
    def __init__(self, program, cmd_key):
        self.key = cmd_key
        self.cmd = program.commands[cmd_key]
        self.is_opencl = self.cmd.get('run_time',{}).get('need_compute_device','') == 'opencl'
        self.dataset_tags = self.cmd.get('dataset_tags',[])
        self.autotuning = self.cmd.get('autotuning',{})

    def get_datasets(self, dataset_uoa):
        '''
        Find datasets by command's dataset tags or by explicitly specified input uoa
        '''
        if not self.dataset_tags:
            return []
        params = {'action':'search',
                  'module_uoa':cfg['module_deps']['dataset'],
                  'add_meta':'yes'}
        if dataset_uoa:
            params['data_uoa'] = dataset_uoa
        else:
            params['tags'] = ','.join(self.dataset_tags)
        r = ck_access(params)
        return sorted(r['lst'], key = lambda x: x.get('data_uoa',''))


class Dataset:
    def __init__(self, json):
        self.uoa = json['data_uoa']
        self.uid = json['data_uid']
        self.files = json['meta'].get('dataset_files',[])

    def get_files(self, requested_files):
        if requested_files:
            files = [f for f in self.files if f in requested_files]
        else:
            files = self.files
        # add empty for 1 iteration without a file
        return files if files else ['']


class LibraryEnv:
    def __init__(self, library_env):
        self.env = library_env
        self.data_uoa = self.env.get('data_uoa','')
        self.data_name = self.env.get('data_name','')
        self.version = self.env['dict']['customize']['version']
        self.tags = self.env['data_name'].lower().replace(', ','-').replace(' ','-').replace(',','-').replace('(','').replace(')','')
        self.lib_id = str(self.env.get('dict',{}).get('customize',{}).get('lib_id', 0))

    def get_tags_for_test(self):
        if not self.data_uoa:
            return 'no-library'

        # Remove duplicates at the end of `tags` and beginning of `version` (e.g. avgpool-avgpool)
        x1 = self.tags
        x2 = self.version

        j1=x1.rfind('-')
        if j1>0:
            xx=x1[j1+1:]

            yy=x2
            j2 = x2.find('-')
            if j2>0:
                yy=x2[:j2]

            if xx==yy:
                x1=x1[:j1]

        return x1+'-'+x2


class Experiment:
    def __init__(self,
                 options,        # instance of ActionOptions
                 config,         # instance of TestConfig
                 platform,       # instance of PlatformInfo
                 program,        # instance of Program
                 command,        # instance of ProgramCommand 
                 dataset,        # instance of Dataset  
                 dataset_file,   # string
                 library         # instance of LibraryEnv
                ):
        self.options = options             
        self.config = config               
        self.platform = platform           
        self.program = program             
        self.command = command             
        self.dataset = dataset             
        self.dataset_file = dataset_file   
        self.library = library             

        self.dvdt_prof = options.dvdt_prof and command.is_opencl
        self.mali_hwc = options.mali_hwc and command.is_opencl
        if self.mali_hwc:
            self.env = copy.deepcopy(options.env)
            self.env['CK_ADD_RAW_MALI_HWC'] = 'yes'
        else:
            self.env = options.env

        # These are valid only after call of `prepare`
        self.deps = None
        self.compile_deps = None
        self.prepared_pipeline = None
        self.batches_info = None

        # Base tags set
        self.tags = ['nntest', program.uoa, library.get_tags_for_test()]

        # Make record uoa from base tags and timestamps
        self.record_uoa = ''
        if options.record:
            if options.record_uoa:
                self.record_uoa = options.record_uoa
            else:
                ts = options.timestamp or config.stimestamp
                self.record_uoa = '-'.join(self.tags) + '-' + ts

        # Full tags set
        self.tags.extend([config.timestamp, config.stimestamp, program.species_uoas_str])

        # Get specific autotuner
        self.autotune_id = options.autotune_id or library.lib_id

    def prepare(self, action_params_json):
        '''
        Prepare pipeline, resolve all dependencies.
        '''
        # `compile_deps` will be resolved after call of `prepare` 
        # and this object will be updated, so we need the copy
        self.compile_deps = copy.deepcopy(self.program.compile_deps)
        if self.library.data_uoa:
            self.compile_deps['library']['uoa'] = self.library.data_uoa
            self.compile_deps['library']['skip_cache']='yes' # do not cache since we will iterate over it

        params_json = {
            'action': 'pipeline',
            'prepare': 'yes',

            'dependencies': self.compile_deps,
            'deps_cache': self.config.deps_cache,
            'reuse_deps': yes_no(self.options.reuse_deps),

            'host_os': self.platform.host_os,
            'target': self.options.target,
            'target_os': self.platform.target_os,
            'device_id': self.platform.device_id,

            'module_uoa': cfg['module_deps']['program'],
            'data_uoa': self.program.uoa,

            'cmd_key': self.command.key,
            'dataset_uoa': self.dataset.uoa,
            'dataset_file': self.dataset_file,

            'dvdt_prof': yes_no(self.dvdt_prof),
            'mali_hwc': yes_no(self.mali_hwc),

            'env': self.env,

            'no_state_check': 'yes',
            'no_compiler_description': 'yes',
            'skip_calibration': 'yes',

            'cpu_freq':'max',
            'gpu_freq':'max',

            'flags': self.options.flags,
            'speed': 'no',
            'energy': 'no',

            'skip_print_timers': 'yes',
            'out': 'con' # TODO should it be the same as `i.get('out','')` ?
        }

        # Pass vars from input to pipeline
        for var in pass_vars_to_autotune:
            if var in action_params_json:
                params_json[var] = action_params_json[var]

        # Prepare pipeline
        r = ck_access(params_json)
        if r.get('fail') == 'yes':
            reason = r.get('fail_reason') or 'unknown reason'
            CKException.throw('pipeline failed (%s)' % reason, code=10)
        if r.get('ready') != 'yes':
            CKException.throw('pipeline not ready', code=11)

        # Clean and store pipeline.
        if 'ready' in r: del(r['ready'])
        if 'fail' in r: del(r['fail'])
        if 'return' in r: del(r['return'])
        self.prepared_pipeline = r
        self.deps = r.get('dependencies', {})

    def run(self):
        '''
        Run prepared pipeline.
        '''
        assert self.prepared_pipeline

        params_json = {
            'action': 'autotune',

            'module_uoa': 'pipeline',
            'data_uoa': 'program',

            'meta': self.__make_experiment_meta(),
            'tags': self.tags,
            'pipeline': self.prepared_pipeline,
                              
            'features_keys_to_process': ['##choices#*'],

            'iterations': self.options.iterations,
            'repetitions': self.options.num_repetitions,

            'record': yes_no(self.options.record),
            'record_repo': self.config.exchange_repo,
            'record_experiment_repo': self.config.exchange_subrepo,
            'record_failed': 'yes',
            'record_dict': { 'subview_uoa': cfg['data_deps']['experiment.view.nntest'] },
            'record_params': { 'search_point_by_features': 'yes' },
            'record_uoa': self.record_uoa,

            'pause': yes_no(self.options.pause),
            'pause_if_fail': yes_no(self.options.pause_if_fail),
            'skip_stat_analysis': yes_no(self.dvdt_prof), # too much raw statistics
            'out': 'con' # TODO should it be the same as `i.get('out','')` ?
        }

        self.__apply_autotuning_params(params_json)

        # Start benchmarking or autotuning
        r = ck_access(params_json)
        if r.get('fail') == 'yes':
            reason = r.get('fail_reason') or 'unknown reason'
            CKException.throw('autotuning failed (%s)' % reason, code=10)

    def __make_experiment_meta(self):
        '''
        Prepare experiment entry meta
        '''
        meta = {
            'timestamp': self.config.timestamp,
            'stimestamp':  self.config.stimestamp,
            'user': self.config.user,
            'nntest_ver': cfg['version'],

            'scenario_module_uoa': work['self_module_uid'],

            'host_os_uid': self.platform.host_os_uid,
            'target_os_uid': self.platform.target_os_uid,
            'target_device_id': self.platform.device_id,

            'cpu_name': self.platform.cpu_name,
            'cpu_abi': self.platform.cpu_abi,
            'cpu_uid': self.platform.cpu_uid,

            'os_name': self.platform.os_name,
            'os_uid': self.platform.os_uid,

            'plat_name': self.platform.name,
            'plat_uid': self.platform.uid,

            'gpu_name': self.platform.gpu_name,
            'gpgpu_name': self.platform.gpgpu_name2,
            'gpgpu_vendor': self.platform.gpgpu_vendor,
            'opencl': self.platform.opencl_version,

            'prog_uoa': self.program.uoa,
            'prog_uid': self.program.uid,
            'prog_type': self.program.type,

            'species': self.program.species_uoas_str,

            'cmd_key': self.command.key,

            'dataset_uoa': self.dataset.uoa,
            'dataset_uid': self.dataset.uid,
            'dataset_file': self.dataset_file,

            'versions': get_versions_of_all_deps(self.deps)
        }  

        # Add hostname if required
        if ck.cfg.get('record_nntest_hostname','') == 'yes':
            import platform
            meta['platform_hostname'] = platform.node() 

        return meta

    def __apply_autotuning_params(self, target_json):
        # Check if program meta has global autotuning
        if self.program.autotuning:
            target_json.update(self.program.autotuning)

        # Check if program meta has autotuning for a given command line
        if self.command.autotuning:
            target_json.update(self.command.autotuning)

        # Check if autotune_id
        autotuning = self.program.get_autotuning_from_file(self.autotune_id)
        if autotuning:
            target_json.update(autotuning)

        # Check if external autotuning is defined
        if self.options.custom_autotuning:
            target_json.update(self.options.custom_autotuning)

    def __format_batch_sizes(self):
        if self.batches_info:
            return self.batches_info
        autotuning = self.program.get_autotuning_from_file(self.autotune_id)
        batch_size_choise_order = -1
        for order, param in enumerate(autotuning.get('choices_order', [])):
            if param and 'CK_IN_SHAPE_N' in param[0]:
                batch_size_choise_order = order
                break
        if batch_size_choise_order >= 0:
            choices_selection = autotuning.get('choices_selection', [])
            if batch_size_choise_order < len(choices_selection):
                choise = choices_selection[batch_size_choise_order]
                batch_sizes = range(choise['start'], choise['stop']+1, choise['step'])
                self.batches_info = ','.join([str(bs) for bs in batch_sizes])
                return self.batches_info
        return ''

    def print_report(self):
        ck.out('- Program: %s (%s)' % (self.program.uoa, self.program.uid))

        if self.library.data_uoa:
            ck.out('- Library: %s (%s)'  % (self.library.data_name, self.library.data_uoa))

        if self.compile_deps:
            ck.out('- Compiler: %s v%s (%s)' % (self.compile_deps['compiler']['dict']['data_name'],
                                                self.compile_deps['compiler']['ver'],
                                                self.compile_deps['compiler']['uoa']))
        
        if self.dataset_file:
            ck.out('- Shape: dataset:%s:%s' % (self.dataset.uoa, self.dataset_file))

        if self.autotune_id:
            ck.out('- Autotune ID: ' + self.autotune_id)
            ck.out('- Batch sizes: %s' % self.__format_batch_sizes())

        if self.record_uoa:
            ck.out('- Repo: %s:experiment:%s' % (self.config.exchange_repo, self.record_uoa))

        ck.out('- Tags: %s' % self.tags)


def crowdsource(i):
    """
    Input:  {
              See ck run nntest --help

              (local)               - if 'yes', local crowd-benchmarking, instead of public
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }
    """
    try:
        # Initializing various workflow parameters
        convert_to_flat_dict(i)
        OPTIONS = ActionOptions(i)
        CONFIG = TestConfig(OPTIONS)

        def ck_header(msg, level=0):
            if OPTIONS.console:
                indent = '  ' * level
                if level == 0:
                    ck.out('')
                    ck.out(indent + sep)
                ck.out(indent + msg)

        if OPTIONS.mali_hwc and OPTIONS.dvdt_prof:
            ck.out('[WARNING] Shouldn\'t use --mali_hwc and --dvdt_prof at the same time ...')

        # Initialize local environment for program optimization
        PLATFORM = PlatformInfo(i, CONFIG)
        
        # Check user
        CONFIG.user = OPTIONS.user or PLATFORM.user or get_user_from_module_config()
        
        # Now checking which experiments to run
        # Iteration order PROGRAM -> COMMAND -> DATASET -> DATASET_FILE -> LIBRARY
        ck_header('Preparing a list of experiments ...')
        EXPERIMENTS = []

        # Start iterating over programs
        programs = get_programs(OPTIONS.data_uoa, OPTIONS.tags, OPTIONS.get_species_uids())
        for PROGRAM in map(Program, programs):
            ck_header('Analyzing program: {} ({})'.format(PROGRAM.uoa, PROGRAM.uid), level=1)

            # Get libraries from dependencies
            library_envs = load_lib_envs_sorted_by_id(
                [OPTIONS.lib_uoa] if OPTIONS.lib_uoa else PROGRAM.get_lib_env_uoas(PLATFORM)
            )
            
            # Iterate over command lines
            cmd_keys = PROGRAM.get_cmd_keys(OPTIONS)
            for COMMAND in [ProgramCommand(PROGRAM, k) for k in cmd_keys]:
                ck_header('Analyzing command line: ' + COMMAND.key, level=2)

                # Iterate over datasets and check data files
                datasets = COMMAND.get_datasets(OPTIONS.dataset_uoa)
                for DATASET in [Dataset(d) for d in datasets]:
                    ck_header('Analyzing dataset: ' + DATASET.uoa, level=3)

                    # Iterate over data files
                    for DATASET_FILE in DATASET.get_files(OPTIONS.dataset_files):
                        if DATASET_FILE:
                            ck_header('Analyzing dataset file: ' + DATASET_FILE, level=4)

                        # Iterate over libraries
                        for LIBRARY in map(LibraryEnv, library_envs):
                            if LIBRARY.data_uoa:
                                ck_header('Analyzing library: ' + LIBRARY.data_uoa, level=5)

                            EXPERIMENT = Experiment(OPTIONS, CONFIG, PLATFORM, 
                                PROGRAM, COMMAND, DATASET, DATASET_FILE, LIBRARY)

                            EXPERIMENTS.append(EXPERIMENT)
                            # end of for each library
            ck_header('')
            # end of for each program

        if OPTIONS.console:
            ck.out('Experiments prepared: {}'.format(len(EXPERIMENTS)))

        def print_experiment(index, experiment):
            if OPTIONS.console:
                ck.out('')
                ck.out('--------------------------------------------------------')
                ck.out('Experiment {} of {}:'.format(index+1, len(EXPERIMENTS)))
                experiment.print_report()

        # Show all tests to be performed, but do not run them 
        if OPTIONS.see_tests and OPTIONS.console:
            for index, EXPERIMENT in enumerate(EXPERIMENTS):
                print_experiment(index, EXPERIMENT)
            return {'return': 0}

        # Prepare pipelines
        ck_header('Preparing pipelines for all experiments ...')
        for index, EXPERIMENT in enumerate(EXPERIMENTS):
            print_experiment(index, EXPERIMENT)

            EXPERIMENT.prepare(i)

            # TODO: comment needed, what does it need for? 
            # TODO: its result is not used and all seems working without it
            resolve_all_deps(EXPERIMENT.deps, PLATFORM)

        # Prepare pipeline and resolve dependencies, but do not run it
        if OPTIONS.dry_run:
            for index, EXPERIMENT in enumerate(EXPERIMENTS):
                print_experiment(index, EXPERIMENT)
            return {'return': 0}

        # Run all prepared pipelines
        ck_header('Run experiments ...')
        for index, EXPERIMENT in enumerate(EXPERIMENTS):
            print_experiment(index, EXPERIMENT)

            # Pause before compiling and running test
            if OPTIONS.console and OPTIONS.pause:
                ck.inp({'text': 'Press Enter to run experiment ...'})

            EXPERIMENT.run()

    except CKException as e:
        return e.ck_result

    return {'return': 0}

##############################################################################
# start NN/SW/HW co-design dashboard

def dashboard(i):
    """
    Input:  {
              (host)        - Internal web server host
              (port)        - Internal web server port

              (wfe_host)    - External web server host
              (wfe_port)    - External web server port

              (extra_url)   - extra URL
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

#    Old style
#    i['action']='browser'
#    i['cid']=''
#    i['module_uoa']=''
#    i['template']='nntest'


    i['action']='start'
    i['module_uoa']='web'
    i['browser']='yes'
    i['template']='nntest'
    i['cid']=''

    return ck.access(i)
