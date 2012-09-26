#!/curc/admin/benchmarks/bin/python

import os, sys
from datetime import datetime 
from optparse import OptionParser

appsdir = '/home/molu8455/admin/benchmarks/django/benchmarks/apps/'
if not appsdir in sys.path:
    sys.path.insert(0,appsdir)
    
appsdir = '/home/molu8455/admin/benchmarks/django/benchmarks/'
if not appsdir in sys.path:
    sys.path.insert(1,appsdir)    

    
os.environ["DJANGO_SETTINGS_MODULE"] = "benchmarks_site.settings"
from django.db import models
from wire.models import Stream, Linpack
from django.db import IntegrityError

def stream_data(in_file):
    test = in_file.readline().split()[0]
    data = in_file.readline().split()
    
    data_copy = 0
    data_scale = 0
    data_add = 0
    data_triad = 0
        
    if data:
        try:
            data_copy = data[0]
            data_scale = data[1]
            data_add = data[2]
            data_triad = data[3]
        except IndexError:
            print "missing stream data"

    return {'t0': data_copy, 't1': data_scale, 't2': data_add, 't3': data_triad}
    
def linpack_data(in_file):  
    for i in range(6):  
        data = in_file.readline()            
    data = in_file.readline().split()   
    
    data_linpack = {'t0':0,'t1':0,'t2':0,'t3':0}
    for i in range(4):
        try:
            data_linpack['t'+str(i)] = (data[3])
        except IndexError:
            continue
        data = in_file.readline().split()
   
    return data_linpack

def insert_stream(data, node_name, td, tr):
    tmp = datetime(year=td.year, month=td.month, day=td.day, hour=int(tr))
    stream = Stream(test_date=tmp, name=node_name, node=node_name, test1=data['t0'], test2=data['t1'], test3=data['t2'], test4=data['t3'], effective=True)
    try:
        stream.save()
        print "Stream worked"
    except IntegrityError as e:
        print "Stream import error: " + str(e)

def insert_linpack(data, node_name, td, tr):
    tmp = datetime(year=td.year, month=td.month, day=td.day, hour=int(tr))
    linpack = Linpack(test_date=tmp,  name=node_name, node=node_name, test1=data['t0'], test2=data['t1'], test3=data['t2'], test4=data['t3'], effective=True)
    try:
        linpack.save()
        print "linpack worked"
    except IntegrityError as e:
        print "linpack import error: " + str(e)   
    
def import_data(path, date, trial):
    print "Importing Node level data: " + str(path)
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            if subdirname.find("node") == 0:
                data_file = os.path.join(path,subdirname,"data")
                if os.path.exists(data_file):
                    in_file = open(os.path.join(path,subdirname,"data"),"r")
                    
                    # Stream data
                    s = stream_data(in_file)
                    insert_stream(s,subdirname,date, trial)
                    
                    # Linpack
                    l = linpack_data(in_file)
                    insert_linpack(l,subdirname,date, trial)
                                                      
                    in_file.close()
                
#==============================================================================  
if __name__ == '__main__':      
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", help="path to nodes data")
    parser.add_option("-t", "--trial", dest="trial", help="trial number")
    parser.add_option("-d", "--date", dest="date", help="test date (e.g. -d 2012-7-11 )")
    (options, args) = parser.parse_args()
    
    # default options
    test_path = os.getcwd()
    test_trial = 0
    current_time = datetime.now()
    test_date = datetime(current_time.year, current_time.month, current_time.day)
    
    # get the options
    if options.path:
        test_path = options.path
    if options.trial:
        test_trial = options.trial    
    if options.date:
        tmp = options.date
        base = tmp.split("-")
        test_date = datetime(int(base[0]),int(base[1]),int(base[2]))
    
    print "test path  = " + test_path
    print "test date  = " + str(test_date)
    print "test trial = " + str(test_trial)
      
    import_data(test_path, test_date, test_trial) 
    
    