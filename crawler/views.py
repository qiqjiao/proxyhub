import logging
import io
import re 
import subprocess

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.views import generic
from datetime import datetime
from .forms import SourceForm
from .models import Endpoint, Source, PROXYTYPE

# Create your views here.
def index(request):
    sources = Source.objects.all()
    endpoints = Endpoint.objects.all()
    return render(request, 'index.html', {'sources':sources, 'endpoints':endpoints})

def list_endpoints(request, source_id):
    endpoints = Endpoint.objects.all()
    return render(request, 'list_endpoints.html', {'endpoints': endpoints})

def list_sources(request):
    sources = Source.objects.all()
    return render(request, 'list_sources.html', {'sources': sources})

def show_source(request, id):
    source = Source.objects.get(pk=id)
    return render(request, 'show_source.html', {'source': source})

@login_required
def create_source(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SourceForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            source = form.save()
            return HttpResponseRedirect('/crawler/show_source/%s/' % source.id)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = SourceForm()

    return render(request, 'edit_source.html', {
              'action': '/crawler/create_source',
              'form': form
           })

@login_required
def edit_source(request, id):
    source = Source.objects.get(pk=id)
    form = SourceForm(request.POST or None, instance=source)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/crawler/show_source/%s/' % source.id)

    return render(request, 'edit_source.html', {
              'action': '/crawler/edit_source/%s/' % id,
              'form': form
           })

@login_required
def refresh(request):
    logger_io = io.StringIO()
    ch = logging.StreamHandler(logger_io)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger = logging.getLogger('refresh')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    logger.info('Start refreshing all souces')

    sources = Source.objects.all()
    for s in sources:
        logger.info('Handling %s', s.name)
        args = ['python', '-c', s.script]
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        s.last_fetch_resources_found = 0
        #s.last_fetch_time = datetime.now()
        if p.returncode != 0:
            logger.error('Failed to execute script [%s],\nstdout=[%s],\nstderr=[%s]',
                         s.script, stdout, stderr)
            s.last_fetch_success = False
            s.save()
            continue
        s.last_fetch_success = True
        #logger.debug('Successfully executed, output [%s]', stdout)
        records = stdout.decode("utf-8").split('\n')
        logger.debug('Successfully executed, output [%s] lines', len(records))

        for r in records:
            if not re.match(r'\d+\.\d+\.\d+.\d+ \d+ [a-zA-Z|]+', r):
                logger.warning('Invalid redord: [%s]', r)
                continue

            logger.debug('Processing redord: [%s]', r)
            (ip, port, proxy_types_str) = r.split(' ')
            proxy_types = 0
            for t in proxy_types_str.split('|'):
                for m in PROXYTYPE:
                    if t.upper() == m[1]:
                        proxy_types |= m[0]
            e = Endpoint.objects.filter(ip=ip, port=port)
            if e:
                logger.debug('existing endpoint %s', r)
                e[0].sources.add(s)
                e[0].proxy_types |= proxy_types
                e[0].save()
            else:
                logger.debug('new endpoint %s', r)
                e = Endpoint.objects.create(ip=ip, port=port)
                e.proxy_types |= proxy_types
                e.sources.add(s)
                e.save()
            s.last_fetch_resources_found += 1
        s.save()
    l = logger_io.getvalue()
    logger_io.close()
    return HttpResponse("<pre>----%s</pre>" % l)
