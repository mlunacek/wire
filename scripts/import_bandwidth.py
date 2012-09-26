#!/curc/admin/benchmarks/bin/python
import os, sys
from datetime import datetime 
from optparse import OptionParser

appsdir = '/root/srv/www/benchmarks/apps/'
if not appsdir in sys.path:
    sys.path.insert(0,appsdir)
    
appsdir = '/root/srv/www/benchmarks/'
if not appsdir in sys.path:
    sys.path.insert(1,appsdir)    
    
os.environ["DJANGO_SETTINGS_MODULE"] = "benchmarks_site.settings"
from django.db import models
from wire.models import Bandwidth
from django.db import IntegrityError

def bandwidth_data(in_file):
    
    data_bandwidth = {'4194304':0,'1048576':0,'262144':0,'65536':0}
    while in_file:
        line = in_file.readline()
        #print line
        split = line.split()
        if not split:
            break
        if split[0] == '#':
            continue
        try:
            data_bandwidth[split[0]] = split[1]
        except IndexError:
            print "missing linpack data"
                  
    return data_bandwidth
    
def insert_bandwidth(data, subdirname, td, tr):
    node1 = subdirname[:8]
    node2 = subdirname[9:]
    tmp = datetime(year=td.year, month=td.month, day=td.day, hour=int(tr))
    
    bw = Bandwidth(test_date=tmp, name=node1, node1=node1, node2=node2, test1=data['65536'], test2=data['262144'], test3=data['1048576'], test4=data['4194304'], effective=True)
    try:
        bw.save()
    except IntegrityError as e:
        print "Bandwidth import error: " + str(e)

def import_data(path, date, trial):
    print "Importing Bandwidth data: " + str(path)
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            if subdirname.find("node") == 0:
                data_file = os.path.join(path,subdirname,"data_bw")
                #print subdirname
                if os.path.exists(data_file):   
                    in_file = open(data_file,"r")
                  
                    b = bandwidth_data(in_file)
                    insert_bandwidth(b,subdirname,date, trial)
   
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

    
    
