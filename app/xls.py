# -*- coding: utf-8 -*-

"""
load Excel(xls) file

"""

import xlrd

import uuid

import json

import requests


def post(data):
    
    """ unique row? get uuid from json string """
    
    URL =  'http://127.0.0.1:6226/api/v1/callproc.call'
    
    #mtp_update_equipemnt_cs1
    payload = {
                "jsonrpc":"2.0",
                "id":"r2",
                "method":"call",
                "params":
                {
                    "method":"mtp_upsert_cs10",
                    "table":"task", 
                    "pkey":"id",
                    "columns":data,
                   "context":{"user":"mt", "languageid":"1033", "sessionid":"123" } 
               }
            }
            
    HEADERS = {'content-type': 'application/json', 'accept':'json','User-Agent':'mabo'}
    #headers = HEADERS
    #headers = {'Accept':'json'}
    payload = json.dumps(payload)

    r = requests.post(URL, data =   payload , headers=HEADERS)
    
    #print  r.headers
    v = json.loads(r.text)
    
    #print type(v)
    #print v
    if v.has_key("error"):
        return {"taskno":data["taskno"],"error":v["error"][:60]}
    else:
        return {"taskno":data["taskno"]}
    #print json.loads(r.text)
    
    #print("%s" % (data) ) 
    
    
    

def load(filename):
    
    info = []
    
    book = xlrd.open_workbook(filename)
    
    sheets = book.sheets()
    
    sheet = sheets[0]
    
    #print sheet.ncols
    #print sheet.nrows
    
    line = 0
    
    datemode = book.datemode
    
    headers = ["productline","projectname","taskno","sampleno","vin","testname","section","planstart","planend"]
    
    for i in xrange(sheet.nrows):
        line = line + 1
        if line == 1:
            continue
        
        row = {}
        
        for j in xrange(sheet.ncols):
            
            #print i,j
            
            val = sheet.cell_value(i,j)

            
            #print type(val)
            
            if isinstance(val, unicode):
                val = val.encode("utf8")
                #print val
            else:
                type = sheet.cell_type(i,j)
            
                if type == xlrd.XL_CELL_DATE:
                    v = xlrd.xldate_as_tuple(val, datemode)
                    val = "%s-%02d-%02d" %(v[0],v[1],v[2])
                else:
                    #print val
                    pass
                    
            colname = headers[j]
            row[colname] = val
        #print "\n"
        s = json.dumps(row)
        
        ## unique id
        
        row['uid'] = uuid.uuid5(uuid.NAMESPACE_OID,s).hex
        
        rtn = post(row)
        
        info.append(rtn)
        #print s
        #v = json.loads(s)
        #print v["section"].encode("utf8")
    
    return info
        


if __name__ =="__main__":
    
    filename = u"下周试验计划导入模板.xls"
    
    load(filename)
    