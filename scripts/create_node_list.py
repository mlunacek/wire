#!/curc/admin/benchmarks/bin/python


import os
import sys
import shutil
from pbs import freePBSnodes, listPBSnodes


#==============================================================================  
if __name__ == '__main__':  
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-x", "--expression", dest="expression", help="Regex of nodes: e.g. create_node_list -x node01[01-80],node03[04-50]")
    (options, args) = parser.parse_args()
    
    # default options
    node_list = "node[01-17][01-80]"
    
    # get the options
    if options.expression != None:
        node_list = options.expression
    
    r = freePBSnodes(node_list)
       
    for node in r:
        print str(node)
    
        
    
