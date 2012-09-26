#!/curc/admin/benchmarks/bin/python

import os
import create_node_test
import create_bandwidth_test
import create_hpl_test
from util import read_node_list, categorize, create_directory_structure
 
#==============================================================================  
if __name__ == '__main__':  
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-q", "--queue", dest="queue", help="PBS Queue")
    parser.add_option("-l", "--list", dest="list", help="A list of nodes to run on")
    (options, args) = parser.parse_args()
    
    # default options
    queue = "janus-admin"
    node_list_name = None
    
    # get the options
    if options.queue != None:
        queue = options.queue
    if options.list != None:
        node_list_name = options.list
        tmp = read_node_list(node_list_name)
        print tmp
        node_lists = categorize(tmp)
    else:
        print "please specify a node list."
        exit()    
    
    # Create scripts
    for name, name_list in node_lists.iteritems():
        if len(name_list) > 0:
            
            # Node test
            create_node_test.create(name_list, queue)
    
            # Bandwidth test
            create_bandwidth_test.create(name_list, queue)
            
            # HPL test
            create_hpl_test.create(name_list, queue, 5, 20, "hpl.5")
            #create_hpl_test.create(name_list, queue, 5, 50, "hpl.5.70")
            create_hpl_test.create(name_list, queue, 10, 20, "hpl.10")
            create_hpl_test.create(name_list, queue, 20, 20, "hpl.20")
            #create_hpl_test.create(name_list, queue, 40, 20,"hpl.40")
            #create_hpl_test.create(name_list, queue, 80, 20)
            
            
            #create_hpl_test.create(name_list, queue, 30, 30)
            #create_hpl_test.create(name_list, queue, 50, 30)
            #create_hpl_test.create(name_list, queue, 60, 30)
            #create_hpl_test.create(name_list, queue, 70, 30)
            #create_hpl_test.create(name_list, queue, 80, 30)
