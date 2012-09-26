#!/curc/admin/benchmarks/bin/python

import os
import sys
import shutil

from django.conf import settings
from django import template

if not settings.configured:
    settings.configure()

from util import read_node_list, create_directory_structure

NODE_TEMPLATE = """\
#!/bin/bash
#PBS -N output.{{node_name}}
#PBS -q {{queue_name}}
#PBS -l walltime=00:45:00
#PBS -l nodes={{node_name}}:ppn=12
#PBS -j oe

cd $PBS_O_WORKDIR
mkdir -p {{node_name}}

# copy linpack 
cd {{node_name}}

cat >> linpack_input << EOF
Sample Intel(R) Optimized LINPACK Benchmark data file (lininput_xeon64)
Intel(R) Optimized LINPACK Benchmark data
6                     # number of tests
1000 2000 5000 10000 20000 25000# problem sizes
1000 2000 5000 10000 20000 25000 # leading dimensions
2 2 2 1 1 1  # times to run a test
4 4 4 4 4 4  # alignment values (in KBytes)
EOF

. /curc/tools/utils/dkinit
use .openmpi-1.4.5_intel-12.1.2
use Benchmarks

echo "STREAM Memory Bandwidth Test:" > data
#----------------------------------------------------------------------------
export OMP_NUM_THREADS=12
NUM_TRIALS=2
COPYTOTAL=0
SCALETOTAL=0
ADDTOTAL=0
TRIADTOTAL=0

for ((i=0; i < NUM_TRIALS ; i++ ))
do
# Grab the 3 lines in addition to the line starting with Copy	
VAR=`stream | grep -A 3 Copy`

COPY=`echo $VAR | awk '{ print $2 }' | awk -F. '{ print $1 }'`
COPYTOTAL=$(($COPY + $COPYTOTAL))

SCALE=`echo $VAR | awk '{ print $7 }' | awk -F. '{ print $1 }'`
SCALETOTAL=$(($SCALE + $SCALETOTAL))

ADD=`echo $VAR | awk '{ print $12 }' | awk -F. '{ print $1 }'`
ADDTOTAL=$(($ADD + $ADDTOTAL))

TRIAD=`echo $VAR | awk '{ print $17 }' | awk -F. '{ print $1 }'`
TRIADTOTAL=$(($TRIAD + $TRIADTOTAL))

done

echo $((COPYTOTAL/NUM_TRIALS)) " " $((SCALETOTAL/NUM_TRIALS)) " " $((ADDTOTAL/NUM_TRIALS)) " " $((TRIADTOTAL/NUM_TRIALS)) >> data

# Linpack
echo "Linpack CPU Test:" >> data
#----------------------------------------------------------------------------
xlinpack_xeon64 linpack_input | grep -A 9 Performance >> data

"""

def create_pbs_template(values, mypath):
    output_file = os.path.join(mypath,"script_" + values['node_name'])
    file_out = open(output_file,'w')
    t = template.Template(NODE_TEMPLATE)
    contents = t.render(template.Context(values))
    file_out.write(contents)
    file_out.close()    
    
def create(node_list, queue):
    current_path = os.getcwd()
    mypath = os.path.join(current_path,"nodes")
    create_directory_structure(mypath)
    
    for node in node_list:
           
        # create the pbs command
        values = {}
        values['node_name'] = node
        values['queue_name'] = queue
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
        node_list = read_node_list(node_list_name)
        print node_list
    else:
        print "please specify a node list."
        exit()
    
    create(node_list, queue)
        
    








