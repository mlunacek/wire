from django.shortcuts import get_object_or_404, render
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import Context, loader, RequestContext

from wire.models import Stream, Linpack, Bandwidth, Summary, Nodes
from datetime import datetime, date

def static_render(request, template):
    data ={}
    data["current_date"] = get_current_date(request)
    data["date_list"]= date_list()
    return render(request,template, data, context_instance=RequestContext(request))





class Trial:
    def __init__(self, d):
        self.d = d
        print str(d) + " " + str(d.hour)
        tmp = date(int(d.year), int(d.month),int(d.day))
        tmp_url = str(tmp.isoformat())+"/"+str(d.hour)+"/"
        self.u = tmp_url
        self.p = d.strftime("%b %d, %Y")+"  trial "+ str(d.hour)

def date_list():
    date_list = list(set(Stream.objects.values_list('test_date', flat=True)))
    date_list.sort(reverse=True)
    data = []
    for d in date_list[0:5]:
        print "date = " + str(d)
        data.append(Trial(d))
    return data

def create_current_date(y,m,d,h):
    tmp = datetime(year=int(y), month=int(m), day=int(d), hour=int(h))
    return Trial(tmp)

def get_current_date(request):
    datelist = date_list()
    current_date=datelist[0]
    return current_date

def add_summary_nodes(nodes, index):
    for xid in nodes:
        try:
            summary = Summary.objects.get(node=xid)
            if index=="stream":
                summary.stream = True
            if index=="linpack":
                summary.linpack = True
            if index=="bandwidth":
                summary.bandwidth = True  
            summary.save()
        except Summary.DoesNotExist:
            if index=="stream":
                summary= Summary(xid,True,False,False); 
            if index=="linpack":
                summary= Summary(xid,False,True,False); 
            if index=="bandwidth":
                summary= Summary(xid,False,False,True); 
            summary.save()

def create_reservation(objects):
    res = "export NODE_LIST="
    for x in objects:
        res += x.node+","
    return res[:-1]

def create_reservation_nodes(objects):
    res = "export NODE_LIST="
    for x in objects:
        res += x+","
    return res[:-1]    
    

def bandwidth_nodes(d):    
    return set(Bandwidth.objects.filter(test_date=d).values_list('node1', flat=True))

def stream_nodes(d):    
    return set(Stream.objects.filter(test_date=d).values_list('node', flat=True))

def linpack_nodes(d):    
    return set(Linpack.objects.filter(test_date=d).values_list('node', flat=True))
 
def nodes_not_tested(data):
    
    stream = stream_nodes(data['current_date'].d)
    linpack = linpack_nodes(data['current_date'].d)
    bandwidth = bandwidth_nodes(data['current_date'].d)
     
    tested = stream.union(linpack)
    tested = tested.union(bandwidth)
    allnodes =set(Nodes.objects.values_list('node',flat=True))
    
    tested = allnodes.intersection(tested)
    not_tested = list(allnodes.difference(tested))
    not_tested.sort()
    print not_tested
    print len(not_tested)
    
    return not_tested
    
        
def get_summary(data):
        
    stream_bad_nodes = list(set(Stream.objects.filter(effective=False, test_date=data['current_date'].d).values_list('node', flat=True)))    
    linpack_bad_nodes = list(set(Linpack.objects.filter(effective=False, test_date=data['current_date'].d).values_list('node', flat=True)))   
    bandwidth_bad_nodes = list(set(Bandwidth.objects.filter(effective=False, test_date=data['current_date'].d).values_list('node1', flat=True)))  
    
    Summary.objects.all().delete()
    add_summary_nodes(stream_bad_nodes,"stream")
    add_summary_nodes(linpack_bad_nodes,"linpack")
    add_summary_nodes(bandwidth_bad_nodes,"bandwidth")   
    summary = Summary.objects.all()
    data['summary'] = summary
    data['reservation'] = create_reservation(summary)
    tmp = nodes_not_tested(data)
    data['not_tested'] = create_reservation_nodes(tmp)

    
    
    
    
    
    
    