#!/curc/admin/benchmarks/bin/python

import os,sys
from datetime import datetime 

appsdir = '/Users/mlunacek/Sites/performance/benchmarks_2.0/apps'
if not appsdir in sys.path:
    sys.path.insert(0,appsdir)
    
appsdir = '/Users/mlunacek/Sites/performance/benchmarks_2.0'
if not appsdir in sys.path:
    sys.path.insert(1,appsdir)    
    
os.environ["DJANGO_SETTINGS_MODULE"] = "benchmarks_site.settings"
from django.db import models
from wire.models import Nodes
from django.db import IntegrityError



#==============================================================================  
if __name__ == '__main__':  
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-d", "--date", dest="date", help="test date (e.g. -d 2012-7-11 )")
    parser.add_option("-t", "--trial", dest="trial", help="trial number")
    (options, args) = parser.parse_args()
    
    # default options
    current_time = datetime.now()
    d = datetime(current_time.year, current_time.month, current_time.day)
    t = 0
    
    # get the options
    if options.date:
        tmp = options.date
        base = tmp.split("-")
        d = datetime(int(base[0]),int(base[1]),int(base[2]))
    if options.trial:
        test_trial = options.trial
        
    print "test date = " + str(d)
    print "test trial = " + str(t)

    from wire.models import Stream, Linpack, Bandwidth
    from django.db import IntegrityError

    tmp = datetime(year=d.year, month=d.month, day=d.day, hour=int(t))

    Stream.objects.filter(test_date=tmp).delete()
    Linpack.objects.filter(test_date=tmp).delete()
    Bandwidth.objects.filter(test_date=tmp).delete()
    

    #import_node_test.import_data(os.path.join(test_path,"nodes"), test_date) 
    #import_bandwidth_test.import_data(os.path.join(test_path,"bandwidth"), test_date) 
    #import_hpl_test.import_data(os.path.join(test_path,"hpl.5"), test_date) 
    #import_hpl_test.import_data(os.path.join(test_path,"hpl.20"), test_date) 
    #import_hpl_test.import_data(os.path.join(test_path,"hpl.40"), test_date) 