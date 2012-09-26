#!/curc/admin/benchmarks/bin/python
from django.conf import settings
from django import template
if not settings.configured:
    settings.configure()

import fileinput, os, sys
import math
import numpy
from scipy import stats
import uuid

from util import read_node_list, categorize,  create_directory_structure

HPL_TEMPLATE = """\
#!/bin/bash
#PBS -N job.{{id}}
#PBS -q {{queue}}
#PBS -l walltime={{time_estimate}}
#PBS -l nodes={% for x in node_list %}{{x}}:ppn=12{% if not forloop.last %}+{%endif%}{% endfor %}
#PBS -j oe

cd $PBS_O_WORKDIR

mkdir -p test_{{id}}
cd test_{{id}}

cat >> HPL.dat << EOF
HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
data		 output file name (if any) 
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
{{n}}          Ns
1            # of NBs
128           NBs
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
{{p}}           Ps
{{q}}           Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
EOF

cat >> info << EOF
{{id}}
{{n}}
{{percent}}
{% spaceless %}
{% for x in node_list %}{{x}}
{% endfor %}
{% endspaceless %}	
EOF

. /curc/tools/utils/dkinit
use .openmpi-1.4.5_intel-12.1.2

mpirun -np {{processors}} /curc/admin/benchmarks/bin/xhpl > data

"""
# These are parameters for the script
#==============================================================================   
def processors_per_node():
    return 12
    
def memory_per_node():
     return 20*1073741824  

# The class for modeling time     
#==============================================================================     
class TimeModel:
    def __init__(self):
        # fixed at 20%: processors vs. time
        x1 = [ 12,  24,  48,  96, 192, 384, 768, ]
        y1 = [72.61, 104.29, 150.38, 215.10, 314.19, 455.94, 681.95]
        self.g1, self.i1, r, p, std_err = stats.linregress( numpy.log(x1), numpy.log(y1))
        
        # fixed at 8 nodes: percent vs. time
        x2 = [ 20, 40, 60, 80 ]
        y2 = [ 215.10, 583.83, 1056.89, 1617.62]
        y2 = numpy.divide(y2,215.10)
        self.g2, self.i2, r, p, std_err = stats.linregress( numpy.log(x2), numpy.log(y2))
                        
    def get_time_estimate(self, nodes, percent):
        tmp = self.g1 * numpy.log(nodes*12) + self.i1
        time_est = numpy.exp(tmp)
        
        tmp = self.g2 * numpy.log(percent) + self.i2
        factor_est = numpy.exp(tmp)
        return round(time_est*factor_est)*10
        
def max_matrix_dimension(nodes, percent):
    tmp = memory_per_node()*nodes*percent/8
    return int(math.floor(math.sqrt(tmp)))

def factor(n):
    if n == 1: return [1]
    i = 2
    limit = n**0.5
    while i <= limit:
        if n % i == 0:
            ret = factor(n/i)
            ret.append(i)
            return ret
        i += 1
    return [n]

def closest_match(n):
    factors = factor(n)
    index = 1
    A = numpy.multiply.reduce(factors[:index])
    B = numpy.multiply.reduce(factors[index:])
    diff = abs(A-B)
    while index < len(factors):
        tmpA = numpy.multiply.reduce(factors[:index])
        tmpB = numpy.multiply.reduce(factors[index:])
        if( abs(tmpA-tmpB) < diff):
            diff = abs(tmpA-tmpB)
            A = tmpA
            B = tmpB
        index += 1
    values = [A,B]    
    values.sort()
    return values

def create_pbs_template(mypath, hpl):
    output_file = os.path.join(mypath,"script_" + hpl['job_name'] + "-" + hpl['id'])
    file_out = open(output_file,'w')
    t = template.Template(HPL_TEMPLATE)
    contents = t.render(template.Context(hpl))
    file_out.write(contents)
    file_out.close()    

def create_node_groups(node_list,n):
    total_nodes = len(node_list)
    x = math.floor(total_nodes/float(n))
    y = math.ceil(total_nodes/float(n))
    
    node_groups = []
    
    #print "create " + str(x) + " groups with " + str(n) + " nodes"
    index = 0
    for r in range(int(x)):
        tmp = []
        for i in range(int(n)):
            tmp.append(node_list[index].rstrip())
            index += 1
        #print tmp    
        node_groups.append(tmp)
    
    #print "create 1 group with " + str(total_nodes - x*n) + " nodes"
    if total_nodes - x*n > 0:
        tmp = []
        for i in range(int(total_nodes - x*n)):
            tmp.append(node_list[i].rstrip())
        #print tmp    
        node_groups.append(tmp)
    
    #print node_groups
    return node_groups

def render(mypath, queue, node_list, percent):
    n = len(node_list)
    print n
    hpl = {}
     
    hpl['queue'] = queue 
    # What's the best P and Q
    PQ = closest_match(n*processors_per_node())
    hpl['p'] = PQ[0]
    hpl['q'] = PQ[1]
    hpl['id'] = str(uuid.uuid1())
    #hpl['id'] = str(111)
    hpl['nodes'] = n
    hpl['processors'] = n*processors_per_node()
    hpl['node_list'] = node_list
    hpl['percent'] = percent
    
    time_model = TimeModel()
    time_estimate = time_model.get_time_estimate(n, percent)
    print time_estimate
    hpl['time_estimate'] = time_estimate
    
    # Max problem size?
    N = max_matrix_dimension(n,(float(percent)/100))
    hpl['n'] = N

    job_name = "hpl-" + str(n) + "-" + str(percent)
        
    hpl['job_name'] = job_name
    
    create_pbs_template(mypath, hpl)
    
    
def create(name_list, queue, n, percent, dir_name):
    current_path = os.getcwd()
    mypath = os.path.join(current_path, dir_name)
    create_directory_structure(mypath)
    
    groups = create_node_groups(name_list,n)      
    for i in range(len(groups)):
        render(mypath, queue, groups[i], percent)
            


#==============================================================================  
if __name__ == '__main__':  
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-n", "--nodes", dest="nodes", help="Number of nodes to use")
    parser.add_option("-m", "--memory", dest="memory", help="Percent of memory to use (e.g. -m 20 for 20%)")
    parser.add_option("-q", "--queue", dest="queue", help="PBS Queue")
    parser.add_option("-p", "--prefix", dest="prefix", help="A job prefix string")
    parser.add_option("-l", "--list", dest="list", help="A list of nodes to run on")
    (options, args) = parser.parse_args()
    
    # default options
    nodes = 1
    percent = 20
    queue = "janus-admin"
    prefix = None
    node_list_name = None
    
    # get the options
    if options.nodes:
        nodes = int(options.nodes)
    if options.memory:
        percent = int(options.memory)
    if options.queue:
        queue = options.queue
    if options.prefix:
        prefix = options.prefix
    if options.list:
        node_list_name = options.list
        tmp = read_node_list(node_list_name)
        node_lists = categorize(tmp)
    else:
        print "please specify a node list."
        exit()
        
    for name, name_list in node_lists.iteritems():
        if len(name_list) > 0:    
            create(name_list,queue,nodes,percent,"hpl")
   

