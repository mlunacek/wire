#!/curc/admin/benchmarks/bin/python

import os
import sys
import shutil

from django.conf import settings
from django import template
if not settings.configured:
    settings.configure()


from util import read_node_list, categorize,  create_directory_structure

PBS_TEMPLATE = """\
#!/bin/bash
#PBS -N output.{{job_name}}
#PBS -q {{queue_name}}
#PBS -l walltime=00:10:00
#PBS -l nodes={{node_list}}
#PBS -j oe

. /curc/tools/utils/dkinit

use Torque
use Moab
use .openmpi-1.4.3_ics-2011.0.013_torque-2.5.7_ib

cd $PBS_O_WORKDIR
mkdir -p {{job_name}}
cd {{job_name}}

mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_bw > data_bw
mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_latency > data_latency
mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/stress | grep aggregate > data_stress
mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/mpi_latency > data_mpi_latency
mpirun -pernode /home/molu8455/projects/software/cbench/cbench-1.2.2/bin/osu_bcast > data_bcast

"""



def create_node_pairs(node_list):
    pair_list = []
    
    odd_list = node_list[::2]
    even_list = node_list[1::2]
    
    tmp1 = odd_list[0]
    if len(odd_list) > len(even_list):
        tmp1 = odd_list.pop(len(odd_list)-1)

    # create list
    for i in range(len(odd_list)):
        node_pair = odd_list[i], even_list[i]
        node_pair = sorted(node_pair)
        if node_pair not in pair_list:
            pair_list.append(node_pair)
    
    # create second list
    odd_list.append(tmp1)
    tmp2 = odd_list.pop(0)

    for i in range(len(odd_list)):
        node_pair = odd_list[i], even_list[i]
        node_pair = sorted(node_pair)
        if node_pair not in pair_list:
            pair_list.append(node_pair)
            
    # add the last pair if odd size list
    if tmp1 != tmp2:
        node_pair = tmp1, tmp2
        node_pair = sorted(node_pair)
        pair_list.append(node_pair)

    return sorted(pair_list)    

def create_pbs_template(values, mypath):
    output_file = os.path.join(mypath,"script_" + values['job_name'])
    file_out = open(output_file,'w')
    t = template.Template(PBS_TEMPLATE)
    contents = t.render(template.Context(values))
    file_out.write(contents)
    file_out.close()    
 
def create(name_list, queue):
    current_path = os.getcwd()
    mypath = os.path.join(current_path,"bandwidth")
    create_directory_structure(mypath)
        
    pair_list = create_node_pairs(name_list)    
        
    for pair in pair_list:
        node_list = pair[0] + ":ppn=12+" + pair[1] + ":ppn=12"
        job_name = pair[0] + "-" + pair[1]
        values = {}
        values['job_name'] = job_name
        values['queue_name'] = queue
        values['node_list'] = node_list
        create_pbs_template(values, mypath)
    
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
        node_lists = categorize(tmp)
    else:
        print "please specify a node list."
        exit()    
    
    for name, name_list in node_lists.iteritems():
        print name
        if len(name_list) > 0:    
            create(name_list,queue)
            


