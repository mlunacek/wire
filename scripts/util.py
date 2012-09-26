import os
import sys

def read_node_list(node_list_name):
    node_list = []
    file_in = open(os.path.join(os.getcwd(), node_list_name),'r') 
    node_name = file_in.readline()
 
    while node_name:
        if len(node_name.strip()) == 8:
            node_list.append(node_name.strip())
        node_name = file_in.readline()
    file_in.close()
    
    return node_list

def categorize(node_list):

    # long node01
    # special node02* + node0301
    # janus node0302 - *
    
    long_nodes = []
    special_nodes = []
    janus_nodes = []
    
    for x in node_list:
        if x[4:6] == "01":
            long_nodes.append(x)
        elif (x[4:6] == "02" or x == "node0301"):
            special_nodes.append(x)
        else:
            janus_nodes.append(x)
    
    return {'long':long_nodes,'special':special_nodes,'janus':janus_nodes}

def create_directory_structure(dir_name):
    
    if os.path.exists(dir_name):
        print "WARNING: " + dir_name + " directory already exists "
    else:
        try:
            os.mkdir(dir_name)
        except os.error as e:
            print "ERROR: " + e.strerror
