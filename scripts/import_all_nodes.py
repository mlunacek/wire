#!/curc/admin/benchmarks/bin/python

import os, sys
from datetime import datetime 
from optparse import OptionParser

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

def insert_node(node_name):
    nodes = Nodes(node=node_name)
    try:
        nodes.save()
    except IntegrityError as e:
        print "Nodes import error: " + str(e)

def import_data(file):
    print file
    if os.path.exists(file):
        in_file = open(file,"r")
        data = in_file.readline()   
        while data:
            node_name=data.split()[0]
            data = in_file.readline()   
            if len(node_name) == 8:
                insert_node(node_name)
                                    
        in_file.close()
                
#==============================================================================  
if __name__ == '__main__':      
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="file", help="nodes data file")
    (options, args) = parser.parse_args()
    
    # default options
    test_path = os.getcwd()
     
    # get the options
    if options.file:
        test_path = options.file
    else:
        print "please specify a file"
        exit()
        
    print "test path = " + test_path
    
    import_data(test_path) 
    
    