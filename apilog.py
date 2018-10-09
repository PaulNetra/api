#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 17:07:30 2018

@author: joe-01
"""
import logging
import numpy as np
#import time
import os
import signal
import shutil
import flask as flsk

MAX_COLUMN  = 7         # how many columns in log file
APINAME     = ""        # "varsig"  # put your api name
MES_STATUS  = 1
MES_COLUMN  = 2
MES_VALUE   = 3
#status codes
STATUS_OK       = 'SG000'
URL_ERROR       = 'EG100'

FILE_NOT_EXIST  = 'EG201'
FILE_FORMAT_ERR = 'EG202'
FILE_NAME_ERR   = 'EG203'
FILE_CREATE_ERR = 'EG204'
FILE_ACCESS_ERR = 'EG205'
FILE_DATA_ERR   = 'EG206'
#FILE_CLEAN_IN_ERR   = 'EG207'
#FILE_CLEAN_OUT_ERR  = 'EG208'

LOG_FILE_ERR    = 'EG300'
LOG_TASK_ERR    = 'EG301'
LOG_EMPTY       = 'EG302'
LOG_DELETE_ERR  = 'EG303'

PROCESS_ERR     = 'EG400'

EXIT_OK         = 'SG500'
EXIT_PROCESSING = 'SG501'
EXIT_ERR        = 'EG502'

VARSIG_METHOD_ERR = 'EV101'
VARSIG_SIGNIF_ERR = 'EV102'
VARSIG_2CLASS_ERR = 'EV103'



#####################################################
def Log(cmd,  message="", st=0, fin=0, mode="INFO", status=EXIT_PROCESSING):
    ''' Create log file and save messages
        format: date time=programm=INFO;some messages;N;N
        delimiter = ;
        2018-08-15 17:44:07,027=varsig=INFO;SG501;Forest progress;;48;2000
        
        cmd: dictionary with appkey and key - can be changed
        cmd: fname log file
        message: "mess1;mess2"
        st, fin - values for loop
        mode: INFO, ERROR
        status: default EXIT_PROCESSING
    '''
    global MAX_COLUMN, APINAME
    
    if isinstance(cmd,dict):
#        if cmd['log'] == False:
        if cmd['log'] == '.':
            return
#        flog= API_logfname(cmd['appkey'], cmd['apikey'])
        flog= cmd['log']
        #    flog= cmd['appkey'] + "." + cmd['apikey'] + ".log" # create file name appkey.key.log
    else:
        flog= cmd    
        
#    if flog == "NULL":
#        return
# create logger
    logger = logging.getLogger(APINAME) # put your name
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    logger.handlers.clear()
    ch = logging.FileHandler(flog)
#    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("%(asctime)s=%(name)s=%(levelname)s%(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.handlers.clear()
    logger.addHandler(ch)
    
    message= ';' + status + ';' + message
    mes_split= message.split(';')
    mes='' #alignment for MAX_COLUMN
    for i in range(MAX_COLUMN-2):
        if i < len(mes_split):
            mes = mes + mes_split[i] + ';'
        else:
            mes = mes + ';'
            
    mes = mes + str(st) + ';'
    mes = mes + str(fin)
        
    print(mes)

    if mode == "INFO":
        logger.info(mes)
    if mode == "ERROR":
        logger.error(mes)
    
#    API_log(cmd['appkey'], cmd['apikey'])

###############################################################
def LogStart(flog, nameproc, infile='', outfile='', folder=False, PID=True):
    ''' Start log file with PID process and files name
        
        flog        : log file name
        nameproc    : your process name
        use this function before using Log function
    '''
    
    global APINAME
    
    APINAME= nameproc
#    flog= API_logfname(appkey, key)
    Log(flog,"Start")
    if PID == True:
        Log(flog,"PID;" + str(os.getpid()))
    else:
        Log(flog,"PID;0")
    
    print("FOLDER", folder)
    if infile != '':
        if folder == False:
            Log(flog,"input;" + infile + ";file") #input file
        else:
            Log(flog,"input;" + infile + ";folder") #input file
            
    if outfile != '':
        Log(flog,"output;" + outfile) #output file

################################################################
def API_logfname(appkey='', key=''):
    ''' Name for log file '''
    import uuid
    return str(uuid.uuid4().hex[:8]) + ".log"
    
#    if appkey == "" or key == "":
#        return "NULL"
#    return str(appkey) + "." + str(key) + ".log"
    
################################################################
#def API_log(appkey, apikey):
def API_log(flog):
    ''' Read log file and check last row
    '''
#    flog= "%s.%s.log"%(appkey, apikey)
#    flog= API_logfname(appkey, apikey)
    
    apilog={}
    try:
        log= np.loadtxt(flog,dtype='str',delimiter=';',ndmin=2) # read log
    except Exception as e:
        print(e)
        apilog['status'] = LOG_FILE_ERR #'EG300' #'error'
#        apilog['exception'] = str(e)
        return apilog #log file was not created - can be error command line

    if log == []:
        apilog['status'] = LOG_EMPTY #'EG302' #'empty'
        return apilog
    
    n= len(log)
    lastrow= list(log[n-1])#.split(";")
    mes= lastrow.copy()
    mes.pop(0)
    print("lastrow", n, lastrow)
#    print("lastrow mes:", mes)
    
    info= lastrow[0].split('=')
    print("INFO", info)
#    apilog['status'] = 'ok'
    apilog['time']= info[0]
    apilog['process']= info[1]
#    apilog['message']= ' '.join(mes)
#    if lastrow[1] == "Exit":
#        apilog['exit']= lastrow[2]
#        if lastrow[2] == 'ok':
#            apilog['status']= 'EG500' #Exit ok
#        else:
#            apilog['status']= 'EG502' #Exit error
#    else:
#        apilog['exit']= "processing"
#        apilog['status']= 'EG501' #processing

    apilog['status'] = lastrow[MES_STATUS] # status
    apilog['proc_start']  = lastrow[-2] # 
    apilog['proc_finish'] = lastrow[-1] # 
    
    if apilog['status'] == EXIT_ERR:
        apilog['error'] = API_LogErrors(flog)
        
    return apilog 

################################################################
def API_LogErrors(flog):
    ''' read all status codes with errors in log file
    result: EG101;EG102;EG502
    '''
    log= np.loadtxt(flog,dtype='str',delimiter=';',ndmin=2)
    n= len(log)
    err_stat=''
    for i in range(n):
        row= list(log[i])
        info= row[0].split('=')
        if info[2] == 'ERROR':
            if err_stat == '':
                err_stat = err_stat + row[MES_STATUS]# status
            else:
                err_stat = err_stat + ';' + row[MES_STATUS]# status
    return err_stat

################################################################
def FileDelete(logrow):
    try:
        os.remove(logrow[MES_VALUE])
    except OSError as e:  ## if failed, report it back to the user ##
        print ("Error: %s - %s." % (e.filename, e.strerror))
#                apilog['exception'] = str(e)
#                return apilog
                
################################################################
#def API_terminate(appkey, apikey):
def API_terminate(flog, task):
    ''' Read log file, delete files and terminate process  
    '''
#    flog= "%s.%s.log"%(appkey, apikey)
#    flog= API_logfname(appkey, apikey)
    apilog={}
#    apilog['status'] = 'error'
    try:
        log= np.loadtxt(flog,dtype='str',delimiter=';',ndmin=2)
    except Exception as e:
        print(e)
#        apilog['exception'] = str(e)
#        apilog['error'] = 'log file error'
        apilog['status'] = LOG_FILE_ERR #'EG300' #'error'
        return apilog #log file was not created - can be error command line

    if log == []:
#        apilog['status'] = 'empty'
        apilog['status'] = LOG_EMPTY #'EG302' #'empty'
        return apilog

    for row in log: # terminate main process and delete input and output files
#        print(row)
#        print("TERM =============   ", row[1], row[2])
        mes= row[MES_COLUMN] 
        if mes == "PID" and task == 'term':
            try:
                os.kill(int(row[MES_VALUE]), signal.SIGTERM) #terminate process
            except:
                pass
        elif mes == "input" or mes == "output":
            try:
                print("DELETE", row[MES_VALUE])
                if row[MES_VALUE+1] == 'file': 
                    os.remove(row[MES_VALUE]) # delete file
                elif row[MES_VALUE+1] == 'folder':
                    shutil.rmtree(row[MES_VALUE]) # delete folder
            except OSError as e:  ## if failed, report it back to the user ##
                print ("Error: %s - %s." % (e.filename, e.strerror))
#                apilog['exception'] = str(e)
#                return apilog

               
    try:    # delete log file
        os.remove(flog)
    except OSError as e:  ## if failed, report it back to the user ##
        print ("Error: %s - %s." % (e.filename, e.strerror))
#        apilog['exception'] = str(e)
        apilog['status'] = LOG_DELETE_ERR #'EG303' # error delete file
        return apilog

#    apilog['status'] = 'ok'
    apilog['status'] = STATUS_OK #'EG000' # ok
    apilog['message']= task #'terminate'
    return apilog


################################################################
def API_process(appkey, apikey, flog, task):
    ''' Read log file, delete files and terminate process  
    '''
#    flog= "%s.%s.log"%(appkey, apikey)
#    flog= API_logfname(appkey, apikey)
    
    if task == 'log':
        log= API_log(flog) #appkey, apikey)
#        result= "log check"
    elif task == 'term' or task == 'clean':
        log= API_terminate(flog, task) #appkey, apikey)
#        result= "terminate"
    else:
        log={}
        log['status'] = LOG_TASK_ERR #'EG301' # Unknown task 'error'
#        log['error'] = 'unknown task'
        
    log['task'] = task    
#    return API_Response(appkey, apikey, flog, "EG000","", result, log)
    return API_Response(appkey, apikey, flog, STATUS_OK,"", "", log)

#################################################################
def API_Response(appkey, key, flog, status, error="", result="", log={}):
    data={}
    data['appkey']= appkey
    data['key']= key
    data['status']= status
    data['result']= result
#    data['error']= error
    data['logname']= flog #API_logfname(appkey, key)
    if log != {}:
        data['log']= log

    return flsk.jsonify( data )
