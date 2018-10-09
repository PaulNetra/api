#!/usr/bin/env python3
# -*- coding: utf-8 -*-n
"""
Created on Tue Jul 31 2018

BSD LICENSE for sci-kit learn

PROPERTY OF NETRAMARK CORP.

@author: jalal
"""

import flask as flsk
import requests
import json
#import DpcController as dpcon # Importing controller module for DeepCrush.
import varselect as vs
#from apilog import API_log, API_terminate, API_logfname, API_Response, API_process
import apilog
import os
import time

app = flsk.Flask(__name__)

data_ = {}
map_data = {}
#@app.route('/api/deep') # App route declaration for DeepCrush-API.
@app.route('/api/varsig') # App route declaration for DeepCrush-API.
def run_dpc_process():
    sig= 0#limit = accuracy = 0
    try:
        fin = flsk.request.args.get('i')
        fout = flsk.request.args.get('o')
        method = flsk.request.args.get('m') # method
        sig = int(flsk.request.args.get('s')) # signif features
#        appkey = flsk.request.args.get('appkey')
#        key    = flsk.request.args.get('key')

#        limit = int(flsk.request.args.get('l')) #limit
#        accuracy = int(flsk.request.args.get('a')) # accuracy
    except Exception as e:
        print("Exception", e)
#        return apilog.API_Response(appkey="",key="",status="error", error="wrong url", result=str(e)) # Flask returns json of map_data; either through curl or web browser.
#        return apilog.API_Response(appkey="",key="", status="EG100") # Flask returns json of map_data; either through curl or web browser.
        return apilog.API_Response(appkey="",key="", status=apilog.URL_ERROR) # Flask returns json of map_data; either through curl or web browser.


#    threshold = int(flsk.request.args.get('threshold')) # Grabbing value from 'threshold' key in Query String.
#    scoop_size = int(flsk.request.args.get('scoop_size')) # Grabbing value from 'scoop_size' key in Query String.
#    file_name = flsk.request.args.get('file_name') # Grabbing value from 'file_name' key in Query String.
    print(fin,fout,method,sig)
    
    # check valid arguments
    errurl = vs.API_commandline(fin, fout, method, sig)
    if errurl != '':
        print('Invalid args given in uri.') # Error message for if values for threshold and scoop_size are invalid.
#        return apilog.API_Response(appkey="",key="",status="error", error="wrong url", result=errurl) # Flask returns json of map_data; either through curl or web browser.
        return apilog.API_Response(appkey="",key="",flog="",status= errurl) # Flask returns json of map_data; either through curl or web browser.
    else:    
#        global data_
#        data_ = dpcon.main_process(file_name, threshold, scoop_size) # Calls main_process in DpcController.py (DeepCrush's controller module).
        print('Main process initiated via API')

#        global map_data
#        map_data = dpcon.maps_to_dict(data_) # Creates the dictionary structure to be stored in Apptudio.
#        print('map_data:\n{}'.format(map_data)) # Printing structure; debugging.

        appkey, key = login_apptudio() # Perform login to Apptudio; should return appkey and key. 
        print('appkey: {}, key: {}'.format(appkey, key)) 

        data_id = post_api(appkey, key, 0, map_data) # POST dictionary structure to Apptudio, using appkey and key as authentication. 0 is process_id for now. Should return data_id if successful.
        print('data_id: {}'.format(data_id)) 

        r_json = get_api(appkey, key, data_id) # GET from Apptudio end; using appkey, key, and data_id to confirm map_data has been stored. Should return json response including map_data (map_count, map_0, map_1, ..., map_M).
        print('r_json:\n{}'.format(r_json))

        flog = apilog.API_logfname()
        try:
            varsigparam= vs.API_convertmethod(fin, fout, method, sig, appkey, key, flog)
#            varsigparam= "-i LungFull15.csv -o lung -m s+f -l 20000 -a 99 -s 4 --log --appkey %s --apikey %s" % (appkey, key)
#            varsigparam= "-i AcceraPlacebo.csv -o accout -m s+f -l 20000 -a 99 -s 4 --log --appkey %s --apikey %s" % (appkey, key)
            pid= vs.VarsigScriptProcess(varsigparam) # MAIN PROCESS
#            pid= vs.VarsigScriptProcess(vs.VarsigScript, varsigparam) # MAIN PROCESS
#            pid= vs.VarsigScriptProcessTest(vs.VarsigTest, "A", "DD" ) # MAIN PROCESS
            print("PID",pid)
#            vs.VarsigScript(varsigparam)
#            vs.VarsigScript("-i LungFull15.csv -o lung.out -s 4")
        except Exception as e:
            print("Exception", e)
#            return apilog.API_Response(appkey, key, status="error",error="cannot start varsig",result=str(e))
#            return apilog.API_Response(appkey, key, flog, status="EG400")
            return apilog.API_Response(appkey, key, flog, status=apilog.PROCESS_ERR)

    data={}
    data['appkey']= appkey
    data['key']= key
    data['status']= "ok"
    
    log={}
    log['time']= "00:11:45"
    log['process']= "mixt method"
#    return json.dump(("appkey", appkey),("key",key))
#    return varsig_response(appkey, key, 'log') # Flask returns json of map_data; either through curl or web browser.
#    return flsk.jsonify(("appkey",appkey), ("key",key), ("status","ok"), ("result","start process")) # Flask returns json of map_data; either through curl or web browser.
#    return flsk.jsonify( data)#("appkey",appkey), ("key",key), ("status","ok"), ("result","start process")) # Flask returns json of map_data; either through curl or web browser.
#    return apilog.API_Response(appkey, key, flog, "EG000","","varsig started", {})
    return apilog.API_Response(appkey, key, flog, apilog.STATUS_OK,"","varsig started", {})



@app.route('/api/varsig-process') # App route declaration for DeepCrush-API.
def varsig_process():
    log={}
    appkey=None
    key=None
    flog=None
    try:
        appkey = flsk.request.args.get('appkey')
        key    = flsk.request.args.get('key')
        flog   = flsk.request.args.get('log')
        task   = flsk.request.args.get('task')
        print(" varsig_process " , appkey, key)
    except Exception as e:
        print("Exception", e)
#        log['status'] = apilog.URL_ERROR #'error'
#        log['error']  = 'wrong url'
#        log['exception'] = str(e)
#        return apilog.API_Response(appkey, key, flog, apilog.URL_ERROR, log=log) # Flask returns json of map_data; either through curl or web browser.
        return apilog.API_Response(appkey, key, flog, apilog.URL_ERROR) # Flask returns json of map_data; either through curl or web browser.
    
    return apilog.API_process(appkey, key, flog, task)

#########################################
def varsig_response(appkey, key, task):
    url= "http://127.0.0.1:5000/api/varsig-process?appkey=%s&key=%s&task=%s"%(appkey, key,task)
    r = requests.get(url)
    return flsk.Response(
        r.text,
        status=r.status_code,
        content_type=r.headers['content-type'],
    )

#########################################################################
def login_apptudio(): # Function definition for login_apptudio(); api_endpoint and username/password predefined.
    api_endpoint = 'http://52.90.21.58/api/Login?cashTime=&isCashEnable=false'
    data = {'UserName': 'netra', 'Password': 'Ad5AGy2dz3a!'}
    r = requests.post(url=api_endpoint, data=data) # POST api call to Apptudio.
    data_r = r.json()['Data'] # Grab 'Data' by key, holds our appkey and key values.

    response_data = json.loads(data_r)[0] #[0] cause its wrapped in a list.
    appkey = response_data['AppKey'] # Grab appkey value.
    key = response_data['Key'] # Grab key value.
    return appkey, key


def post_api(appkey, key, process_id, map_data): # Function definition for post_api(). api_endpoint merged with appkey and key values. 
    api_endpoint = 'http://52.90.21.58/api/'+appkey+'/ModuleData/deepProcess?key='+key # Include appkey and key values in the api_endpoint for authentication. 
    data = {'process_id': process_id, 'map_data': map_data} # Process_id and map_data to used in api call.
    r = requests.post(url=api_endpoint, data=data)
    data_id = r.json()['Data'] # Grab data_id value.
    return data_id

def get_api(appkey, key, data_id): # Function definition for get_api(). api_endpoint merged with appkey, key, and data_id values.
    api_endpoint = 'http://52.90.21.58/api/'+appkey+'/ModuleData/deepProcess/'+data_id+'?key='+key # Include appkey, key, and data_id in api_endpoint for authentication/grabbing the correct stored map_data.
    r = requests.get(url=api_endpoint) # Grab Response.
    return r.json() # Returning Response as json.

if __name__ == '__main__':
    with app.test_request_context(): # For debugging; used to see correct api_endpoint for DeepCrush.
        print(flsk.url_for('run_dpc_process', threshold=40, scoop_size=16, file_name='1077_lung_set.csv'))
    
    app.run()
    
