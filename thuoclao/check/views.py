from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse

from .models import Host, Service


def index(request):
    if request.user.is_authenticated:
        context = {}
        hosts = Host.objects.all()
        services = Service.objects.all()
        context['hosts'] = hosts
        context['services'] = services
        context['count_host'] = len(hosts)
        context['count_service'] = len(services)

        return render(request, 'check/index.html', context)
    else:
        return HttpResponseRedirect('/accounts/login')


def view_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('./' + load_template)
    return HttpResponse(template.render(context, request))


def host(request):
    context = {}
    hosts = Host.objects.all()
    context['hosts'] = hosts
    return render(request, 'check/host.html', context)


def service(request):
    context = {}
    services = Service.objects.all()
    context['services'] = services
    return render(request, 'check/service.html', context)
