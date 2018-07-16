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

              (no_record)           - if "yes", do not record experiments, "no" by default, experiments will be recorded using UIDs
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

def crowdsource(i):
    """
    Input:  {
              See ck run nntest --help

              (local)               - if 'yes', local crowd-benchmarking, instead of public
              (no_record)           - if "yes", do not record experiments, "no" by default, experiments will be recorded using UIDs
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    def yes_no(bool_flag): return 'yes' if bool_flag else 'no'

    # Initializing various workflow parameters
    import copy
    import os
    from time import strftime, gmtime

    # Get current timestamp
    r=ck.get_current_date_time({})
    if r['return']>0: return r
    timestamp=r['iso_datetime']

    #striped timestamp
    j=timestamp.find('.')
    if j>0: timestamp=timestamp[:j]

    stimestamp=timestamp.replace('-','').replace(':','').replace('T','')

    # Setting output and checking misc vars
    o=i.get('out','')
    oo=''
    if o=='con': oo='con'

    quiet=i.get('quiet','')

    xautotune_id=i.get('autotune_id','')

    target=i.get('target','')

     # Check working repository (possibly remote)
    OPTIONS_record = True
    if i.get('no_record') == 'yes':
        OPTIONS_record = False

    local=i.get('local','')
    if local=='yes': 
       er='local'
       esr=''
    else:
       er=i.get('exchange_repo','')
       if er=='': er=cfg.get('default_exchange_repo_uoa','')
       if er=='': er=ck.cfg.get('default_exchange_repo_uoa','')

       esr=i.get('exchange_subrepo','')
       if esr=='': esr=cfg.get('default_exchange_subrepo_uoa','')
       if esr=='': esr=ck.cfg.get('default_exchange_subrepo_uoa','')

    if i.get('record_repo','')!='': er=i['record_repo']
    xrecord_uoa=i.get('record_uoa','')

    # Misc params
    num_repetitions=i.get('repetitions','')
    if num_repetitions=='': num_repetitions=3
    num_repetitions=int(num_repetitions)

    iterations=i.get('iterations','')
    if iterations=='': iterations=-1
    iterations=int(iterations)

    if i.get('overwrite_reference_output','')=='yes':
       iterations=1

    pause=i.get('pause','')
    pause_if_fail=i.get('pause_if_fail','')

    lib_uoa=i.get('library_uoa','')

    see_tests=i.get('see_tests','')
    dry_run=i.get('dry_run','')

    xmali_hwc=i.get('mali_hwc','')

    xdvdt_prof=i.get('dvdt_prof','')
    flags=i.get('flags','')
    if flags=='': flags='-O3'

    if xmali_hwc=='yes' and xdvdt_prof=='yes':
       ck.out('[WARNING] Shouldn\'t use --mali_hwc and --dvdt_prof at the same time ...')

    ikcmd=i.get('cmd_key','')
    idduoa=i.get('dataset_uoa','')
    idfile=i.get('dataset_file','')

    ldfile=[]
    if idfile.find(',')>0:
       ldfile=idfile.split(',')

    custom_autotuning=i.get('custom_autotuning',{})

    # Check deps caching
    deps_cache=[]

    cd=i.get('cache_deps','')
    if cd=='': cd='default'
    deps_cache_uoa='deps-cache-'+work['self_module_uoa']+'-'+cd

    reuse_deps=''
    skip_deps_cache=i.get('skip_deps_cache','')
    if skip_deps_cache!='yes':
       reuse_deps='yes'

    refresh_deps_cache=i.get('refresh_deps_cache','')

    if refresh_deps_cache=='yes':
       r=ck.access({'action':'update',
                    'module_uoa':cfg['module_deps']['tmp'],
                    'data_uoa':deps_cache_uoa,
                    'dict':{'cache':[]}, 'substitute':'yes', 'ignore_update':'yes'})
       if r['return']>0: return r
    elif reuse_deps=='yes':
       r=ck.access({'action':'load',
                    'module_uoa':cfg['module_deps']['tmp'],
                    'data_uoa':deps_cache_uoa})
       if r['return']==0:
          deps_cache=r['dict'].get('cache',[])

    # Check if any key in input dictionary has . and convert to dict (for example deps.xyz or env.xyz) 
    for k in list(i.keys()):
        if k.find('.')>0:
            v=i[k]

            kk='##'+k.replace('.','#')

            del(i[k])

            r=ck.set_by_flat_key({'dict':i, 'key':kk, 'value':v})
            if r['return']>0: return r

    env=i.get('env',{})

    # Check user
    user=''

    mcfg={}
    ii={'action':'load',
        'module_uoa':'module',
        'data_uoa':cfg['module_deps']['program.optimization']}
    r=ck.access(ii)
    if r['return']==0:
       mcfg=r['dict']

       dcfg={}
       ii={'action':'load',
           'module_uoa':mcfg['module_deps']['cfg'],
           'data_uoa':mcfg['cfg_uoa']}
       r=ck.access(ii)
       if r['return']>0 and r['return']!=16: return r
       if r['return']!=16:
          dcfg=r['dict']

       user=dcfg.get('user_email','')

    # Initialize local environment for program optimization ***********************************************************
    pi=i.get('platform_info',{})
    if len(pi)==0:
       ii=copy.deepcopy(i)
       ii['action']='initialize'
       ii['module_uoa']=cfg['module_deps']['program.optimization']
       ii['data_uoa']='caffe'
       ii['exchange_repo']=er
       ii['exchange_subrepo']=esr
       ii['skip_welcome']='yes'
       ii['skip_log_wait']='yes'
       ii['crowdtuning_type']='nntest'
       ii['update_platform_init']=i.get('update_platform_init','')
       if local=='yes': ii['local_autotuning']='yes'
       r=ck.access(ii)
       if r['return']>0: return r

       pi=r['platform_info']
       user=r.get('user','')

    hos=pi['host_os_uoa']
    hos_uid=pi['host_os_uid']
    hosd=pi['host_os_dict']

    tos=pi['os_uoa']
    tos_uid=pi['os_uid']
    tosd=pi['os_dict']
    tbits=tosd.get('bits','')

    remote=tosd.get('remote','')

    tdid=pi['device_id']

    features=pi.get('features',{})

    fplat=features.get('platform',{})
    fos=features.get('os',{})
    fcpu=features.get('cpu',{})

    plat_name=fplat.get('name','')
    plat_uid=features.get('platform_uid','')
    os_name=fos.get('name','')
    os_uid=features.get('os_uid','')
    cpu_name=fcpu.get('name','')
    cpu_abi=fcpu.get('cpu_abi','')
    if cpu_name=='': cpu_name='unknown-'+cpu_abi
    cpu_uid=features.get('cpu_uid','')
    sn=fos.get('serial_number','')

    # Now checking which tests to run
    if o=='con':
       ck.out(sep)
       ck.out('Preparing a list of tests ...')

    tags=['nntest']

    if i.get('tags','')!='':
       tags+=i['tags'].split(',')

    # Check species
    species_uid=[]
    species=i.get('species','').split(',')
    for q in species:
        q=q.strip()
        if q!='':
           r=ck.access({'action':'load',
                        'module_uoa':cfg['module_deps']['program.species'],
                        'data_uoa':q})
           if r['return']>0: return r
           species_uid.append(r['data_uid'])

    # Check opencl, cuda and cpu keywoards and add v
    stags=''
    for q in range(0, len(tags)):
        x=tags[q].strip()

        if x=='opencl': 
           x='vopencl'
        elif x=='cpu': 
           x='vcpu'
        elif x=='cuda':
           x='vcuda'

        if stags!='': stags+=','
        stags+=x

    duoa=i.get('data_uoa','')

    ii={'action':'search',
        'module_uoa':cfg['module_deps']['program'],
        'data_uoa':duoa,
        'tags':stags,
        'add_meta':'yes'}
    r=ck.access(ii)
    if r['return']>0: return r

    lst=r['lst']

    if len(species_uid)>0:
       xlst=[]
       for q in lst:
           if q['meta'].get('skip_from_tests','')!='yes': # it's possible to skip some tests
              for s in species_uid:
                  if s in q['meta'].get('species',[]):
                     xlst.append(q)
                     break
       lst=xlst

    nlst=len(lst)

    if nlst==0:
       return {'return':1, 'error':'no programs selected'}

    # Start iterating over programs
    ip=-1
    for p in sorted(lst, key=lambda x: x.get('data_uoa','')):
        ip+=1

        test_uoa=p['data_uoa']
        test_uid=p['data_uid']
        mm=copy.deepcopy(p['meta']) # program meta

        # Get and save dependencies
        saved_cdeps=copy.deepcopy(mm.get('compile_deps',{}))

        path=p['path']

        prog_tags=mm.get('tags',[])
        prog_type=''
        if 'vopencl' in prog_tags: prog_type='opencl'
        elif 'vcuda' in prog_tags: prog_type='cuda'
        else: prog_type='cpu'

        if o=='con':
           ck.out(sep)
           ck.out('Analyzing program '+str(ip+1)+' of '+str(nlst)+': '+test_uoa+' ('+test_uid+')')

        # Check and iterate over all or pruned command lines
        run_cmds=mm.get('run_cmds',{})
        if len(run_cmds)==0:
           return {'return':1, 'error':'no CMD for run'}

        krun_cmds=sorted(list(run_cmds.keys()))

        if ikcmd!='':
           if ikcmd in krun_cmds:
              krun_cmds=[ikcmd]
           else:
              krun_cmds=[]

        for kcmd in sorted(krun_cmds):
            # Explicitly ignore development command lines
            if kcmd.startswith('dev'): 
               continue

            if o=='con':
               ck.out('  '+sep)
               ck.out('  Analyzing command line: '+kcmd)

            # Meta related to the selected command line
            vcmd=run_cmds[kcmd]

            # Check MALI HWC
            mali_hwc=''
            if xmali_hwc=='yes' and vcmd.get('run_time',{}).get('need_compute_device','')=='opencl':
               mali_hwc='yes'
               env['CK_ADD_RAW_MALI_HWC']='yes'

            # Check dvdt prof
            dvdt_prof=''
            if xdvdt_prof=='yes' and vcmd.get('run_time',{}).get('need_compute_device','')=='opencl':
               dvdt_prof='yes'

            # Check if takes datasets from CK and prepare selection
            dtags=vcmd.get('dataset_tags',[])
            if len(dtags)>0:
               dmuoa=cfg['module_deps']['dataset']

               ii={'action':'search',
                   'module_uoa':dmuoa,
                   'add_meta':'yes'}

               if idduoa=='':
                  tags=''
                  for q in dtags:
                      if tags!='': tags+=','
                      tags+=q

                  ii['tags']=tags
               else:
                  ii['data_uoa']=idduoa

               rx=ck.access(ii)
               if rx['return']>0: return rx

               dlst=rx['lst']

               # Iterate over datasets and check data files
               for dataset in sorted(dlst, key=lambda x: x.get('data_uoa','')):
                   dduoa=dataset['data_uoa']
                   dduid=dataset['data_uid']

                   if o=='con':
                      ck.out('    '+sep)
                      ck.out('    Analyzing dataset: '+dduoa)

                   dd=dataset['meta']

                   dfiles=dd.get('dataset_files',[])
                   if len(ldfile)>0:
                      dfiles=ldfile
                   elif idfile!='':
                      if idfile in dfiles:
                         dfiles=[idfile]
                      else:
                         dfiles=[]
                   elif len(dfiles)==0:
                      dfiles=[''] # add empty for 1 iteration without a file

                   # Iterate over data files
                   for dfile in dfiles:
                      if dfile!='' and o=='con':
                         ck.out('      '+sep)
                         ck.out('      Analyzing dataset file: '+dfile)
                         ck.out('')

                      if pause=='yes':
                         ck.inp({'text':'Press Enter to continue ...'})

                      # Check which species program belongs to (to prepare experiment tags)
                      species=''
                      for q in mm.get('species',[]):
                          r=ck.access({'action':'load',
                                       'module_uoa':cfg['module_deps']['program.species'],
                                       'data_uoa':q})
                          if r['return']>0: return r

                          if species!='': species+=','
                          species+=r['data_uoa']

                      # Resolve library environment UOA(s) (don't use cache to get all choices)
                      cdeps=copy.deepcopy(saved_cdeps) # here unresolved cdeps 
                      if cdeps.get('library', None):
                          if lib_uoa!='':
                              library_env_uoas=[lib_uoa]
                          else:
                             ii={'action':'resolve',
                                 'module_uoa':cfg['module_deps']['env'],
                                 'host_os':hos,
                                 'target_os':tos,
                                 'device_id':tdid,
                                 'deps':{'library':copy.deepcopy(cdeps['library'])}
                             }
                             r=ck.access(ii)
                             if r['return']>0: return r

                             library_env_uoas=r['deps']['library'].get('choices',[])
                             if len(library_env_uoas)==0:
                                 # Check that maybe 1 env was installed during resolving
                                 x=r.get('deps',{}).get('library',{}).get('uoa','')
                                 if x!='':
                                    library_env_uoas.append(x)

                             if len(library_env_uoas)==0:
                                 return {'return':1, 'error':'expected at least one library environment'}

                      else:
                          library_env_uoas=[''] # Empty for at least one iteration even if library is not used

                      # Need to sort by lib_id (if exist to put reference first)
                      libs=[]
                      for library_env_uoa in library_env_uoas:
                          if library_env_uoa=='':
                             libs.append({})
                          else:
                              ii={'action':'load',
                                  'module_uoa':'env',
                                  'data_uoa':library_env_uoa}
                              r=ck.access(ii)
                              if r['return']>0: return r
                              libs.append(r)

                      library_env_uoas2=sorted(libs, key=lambda x: x.get('dict',{}).get('customize',{}).get('lib_id',99999))

                      for library_env in library_env_uoas2:
                          library_env_uoa=library_env.get('data_uoa','')

                          autotune_id=xautotune_id

                          if len(library_env)==0:
                             library_env=None
                             library_id='no-library'
                          else:
                             if o=='con':
                                ck.out('        '+sep)
                                ck.out('        Analyzing library: '+library_env_uoa)
                                ck.out('')

                             cdeps['library']['uoa']=library_env_uoa # here still clean deps
                             cdeps['library']['skip_cache']='yes' # do not cache since we will iterate over it

                             library_tags=library_env['data_name'].lower().replace(', ','-').replace(' ','-').replace(',','-').replace('(','').replace(')','')

                             x1=library_tags
                             x2=library_env['dict']['customize']['version']

                             # Anton asked to remove duplicates at the end of x1 and beginning of x2 (e.g. avgpool-avgpool)
                             j1=x1.rfind('-')
                             if j1>0:
                                xx=x1[j1+1:]

                                yy=x2
                                j2=x2.find('-')
                                if j2>0:
                                   yy=x2[:j2]

                                if xx==yy:
                                   x1=x1[:j1]

                             library_id=x1+'-'+x2

                             # Get specific autotuner
                             lib_id=str(library_env.get('dict',{}).get('customize',{}).get('lib_id',0))

                             if autotune_id=='':
                                autotune_id=str(lib_id)

                          if autotune_id=='':
                             autotune_id='0'

                          if o=='con':
                             ck.out('        Autotune ID: '+autotune_id)
                             ck.out('')

                          if see_tests=='yes':
                             continue

                          # Prepare pipeline.
                          ii={'action':'pipeline',

                              'prepare':'yes',

                              'dependencies':cdeps,
                              'deps_cache':deps_cache,
                              'reuse_deps':reuse_deps,

                              'host_os':hos,
                              'target':target,
                              'target_os':tos,
                              'device_id':tdid,

                              'module_uoa':cfg['module_deps']['program'],
                              'data_uoa':test_uoa,

                              'cmd_key':kcmd,
                              'dataset_uoa':dduoa,
                              'dataset_file':dfile,

                              'dvdt_prof':dvdt_prof,
                              'mali_hwc':mali_hwc,

                              'env':env,

                              'no_state_check':'yes',
                              'no_compiler_description':'yes',
                              'skip_calibration':'yes',

                              'cpu_freq':'max',
                              'gpu_freq':'max',

                              'flags':flags,
                              'speed':'no',
                              'energy':'no',

                              'skip_print_timers':'yes',
                              'out':'con'
                          }

                          # Pass vars from input to pipeline
                          for x in pass_vars_to_autotune:
                              if x in i:
                                 ii[x]=i[x]

                          r=ck.access(ii)
                          if r['return']>0: return r

                          fail=r.get('fail','')
                          if fail=='yes':
                              return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}

                          ready=r.get('ready','')
                          if ready!='yes':
                              return {'return':11, 'error':'pipeline not ready'}

                          # Remember resolved deps for this benchmarking session.
                          xcdeps=r.get('dependencies',{})

                          # Get extra features (resolved GPGPU if needed)
                          pfeatures=pi.get('features',{})

                          fgpu=pfeatures.get('gpu',{})
                          gpu_name=fgpu.get('name','')

                          fgpgpu=pfeatures.get('gpgpu',{})
                          gpgpu_name=fgpgpu.get('name','')
                          gpgpu_vendor=fgpgpu.get('vendor','')
                          gpgpu_type=fgpgpu.get('type','')

                          gpgpu_name2=gpgpu_name
                          if gpgpu_vendor!='': gpgpu_name2=gpgpu_vendor+' '+gpgpu_name

                          fgpgpu_misc=pfeatures.get('gpgpu_misc',{})
                          opencl=fgpgpu_misc.get('opencl c version','')

                          # Clean pipeline.
                          if 'ready' in r: del(r['ready'])
                          if 'fail' in r: del(r['fail'])
                          if 'return' in r: del(r['return'])

                          pipeline=copy.deepcopy(r)
                          jj={'action':'resolve',
                              'module_uoa':'env',
                              'host_os':hos,
                              'target_os':tos,
                              'device_id':tdid,
                              'deps':xcdeps}
                          r=ck.access(jj)
                          if r['return']>0: return r

                          # Get versions of all deps
                          r=ck.access({'action':'get_all_versions_in_deps',
                                       'module_uoa':cfg['module_deps']['env'],
#                                       'only_root':'yes',
                                       'deps':xcdeps})
                          if r['return']>0: return r
                          versions=r['versions']

                          tags=[ 'nntest', test_uoa, library_id ]

                          record_uoa=''
                          if OPTIONS_record:
                             if xrecord_uoa!='':
                                record_uoa=xrecord_uoa
                             else:
                                x=stimestamp
                                if i.get('timestamp','')!='': x=i['timestamp']
                                record_uoa='-'.join(tags)+'-'+x

                          tags.append(timestamp)
                          tags.append(stimestamp)
                          tags.append(species)

                          ck.out('---------------------------------------------------------------------------------------')
                          ck.out('- Program: %s (%s)' % (test_uoa, test_uid))

                          if library_env:
                              ck.out('- Library: %s (%s)'  % (library_env['data_name'], library_env['data_uoa']))

                          ck.out('- Compiler: %s v%s (%s)' % (cdeps['compiler']['dict']['data_name'],
                                                              cdeps['compiler']['ver'], 
                                                              cdeps['compiler']['uoa']))
                          if OPTIONS_record:
                             ck.out('- Experiment: %s:%s' % (er, record_uoa))
                          ck.out('- Tags: %s' % tags)
                          ck.out('---------------------------------------------------------------------------------------')

                          # Prepare experiment entry meta
                          meta={'timestamp':timestamp,
                                'stimestamp':stimestamp,
                                'user':user,
                                'nntest_ver':cfg['version'],

                                'scenario_module_uoa':work['self_module_uid'],

                                'host_os_uid':hos_uid,
                                'target_os_uid':tos_uid,
                                'target_device_id':tdid,

                                'cpu_name':cpu_name,
                                'cpu_abi':cpu_abi,
                                'cpu_uid':cpu_uid,

                                'os_name':os_name,
                                'os_uid':os_uid,

                                'plat_name':plat_name,
                                'plat_uid':plat_uid,

                                'gpu_name':gpu_name,

                                'gpgpu_name':gpgpu_name2,
                                'gpgpu_vendor':gpgpu_vendor,
                                'opencl':opencl,

                                'prog_uoa':test_uoa,
                                'prog_uid':test_uid,

                                'prog_type':prog_type,

                                'species':species,

                                'cmd_key':kcmd,

                                'versions':versions,

                                'dataset_uoa':dduoa,
                                'dataset_uid':dduid,

                                'dataset_file':dfile
                          }

                          # Add hostname
                          if ck.cfg.get('record_nntest_hostname','')=='yes':
                             import platform
                             meta['platform_hostname']=platform.node() 

                          # Start benchmarking or autotuning
                          ii={'action':'autotune',

                              'module_uoa':'pipeline',
                              'data_uoa':'program',

                              'features_keys_to_process':['##choices#*'],

                              'record_params':{
                                  'search_point_by_features':'yes'
                              },

                              'meta':meta,
                              'tags':tags,

                              'iterations':iterations,
                              'repetitions':num_repetitions,

                              'record': yes_no(OPTIONS_record),
                              'record_repo':er,
                              'record_experiment_repo':esr,
                              'record_uoa':record_uoa,

                              'record_failed':'yes',

                              "record_dict":{"subview_uoa":cfg['data_deps']['experiment.view.nntest']},

                              'pause':pause,
                              'pause_if_fail':pause_if_fail,

                              'pipeline':pipeline,
                              'out':'con'}

                          if dvdt_prof=='yes': ii['skip_stat_analysis']='yes' # too much raw statistics

                          if dry_run=='yes': continue

                          # Check if program meta has global autotuning
                          autotuning=mm.get('autotuning',{})
                          if len(autotuning)>0:
                             ii.update(copy.deepcopy(autotuning))

                          # Check if program meta has autotuning for a given command line
                          autotuning2=vcmd.get('autotuning',{})
                          if len(autotuning2)>0:
                             ii.update(copy.deepcopy(autotuning2))

                          # Check if autotune_id
                          if autotune_id!='':
                             px=os.path.join(path,'autotune',autotune_id+'.json')
                             if os.path.isfile(px):
                                r=ck.load_json_file({'json_file':px})
                                if r['return']>0: return r
                                ii.update(copy.deepcopy(r['dict']))

                          # Check if external autotuning is defined
                          if len(custom_autotuning)>0:
                             ii.update(copy.deepcopy(custom_autotuning))
 
                          r=ck.access(ii)
                          if r['return']>0: return r

                          fail=r.get('fail','')
                          if fail=='yes':
                              return {'return':10, 'error':'autotuning failed ('+r.get('fail_reason','')+')'}
                          # end of for each library

                      ck.out('=======================================================================================')
                      ck.out('')
                      # end of for each program

    return {'return':0}

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
