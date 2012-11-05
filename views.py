# Create your views here.
import time
from django.utils import simplejson
from django.db import connection, reset_queries
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render_to_response, HttpResponseRedirect, HttpResponse
from django.template import Context, loader, RequestContext
from django.views.generic import TemplateView
from django.views.generic import ListView
from datetime import datetime, date
from django.db.models import Avg,Max,Min
import functions
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from wire.models import Stream, Linpack, Bandwidth
from wire import models as WireModels
from wire import forms

import numpy as np


@login_required(login_url='/benchmarks/login/')
def summary_redirect(request):
    d = functions.get_current_date(request)
    page = '/benchmarks/summary/' + d.u
    return HttpResponseRedirect(page)
    
@login_required(login_url='/benchmarks/login/')
def summary_detail(request, year, month, day, trial):
    data ={}
    data["current_date"]= functions.create_current_date(year,month,day,trial)
    data["date_list"]= functions.date_list()
    functions.get_summary(data)   
    return render(request,'summary.html',data, context_instance=RequestContext(request))

@login_required(login_url='/benchmarks/login/')
def obj_view_redirect(request,obj_type=None):
    d = functions.get_current_date(request)
    page = '/benchmarks/' + obj_type + '/' + d.u
    return HttpResponseRedirect(page)

@login_required(login_url='/benchmarks/login/')
def obj_view(request,obj_type,year,month,day,trial):
    start_time = time.time()
    reset_queries()
    
    data ={}
    data["current_date"]= functions.create_current_date(year,month,day,trial)
    data["date_list"]= functions.date_list()
    data["name"]=obj_type
    data["cap_name"]=obj_type.title()
       
    clas = globals()[obj_type.title()]
    object_list = clas.objects.filter(test_date=data["current_date"].d)   
        
    if request.method == 'POST':   
        print "post now!"
        effective = request.POST.getlist('effective',None) 
        if effective is None:
            return HttpResponse(status=400) 
        else:
            #for xid in object_list:
            #    xid.effective = True
            #    if xid.id in effective:
            #       xid.effective = False
            #    xid.save()
         
            for xid in effective:
                p = get_object_or_404(clas, pk=xid)
                p.effective = False
                p.save()   
           
    m_data = clas.objects.filter(effective=True).aggregate(avg1=Avg('test1'),avg2=Avg('test2'),avg3=Avg('test3'),avg4=Avg('test4'))
     
    for x in object_list:
        x.calculat_pdiff(m_data['avg1'],m_data['avg2'],m_data['avg3'],m_data['avg4'])
        x.save()
        
    object_list = clas.objects.filter(test_date=data["current_date"].d).order_by('-p_index')
            
    paginator = Paginator(object_list, 100) 
    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    
    data["object_list"] = objects
    print len(connection.queries)
    print sum([ float(x['time']) for x in connection.queries   ])
    
    #for x in connection.queries:
    #    print x["time"] + " " + x["sql"][:30]
     
    end_time = time.time()
    print end_time - start_time
   
    return  render_to_response('obj_view.html',data, context_instance=RequestContext(request))
 
@login_required(login_url='/benchmarks/login/')
def obj_view_data(request,obj_type,year,month,day,trial):
    
    data ={}
    data["current_date"]= functions.create_current_date(year,month,day,trial)
    clas = globals()[obj_type.title()]
    object_list = clas.objects.filter(test_date=data["current_date"].d)
    
    test1 = []
    test2 = []
    test3 = []
    test4 = []
    for x in object_list:
        test1.append(x.test1)
        test2.append(x.test2)
        test3.append(x.test3)
        test4.append(x.test4)
    print np.histogram(test1)

    data = []
    data.append(test1)
    data.append(test2)
    data.append(test3)
    data.append(test4)
    return HttpResponse(simplejson.dumps(data))
    
    













