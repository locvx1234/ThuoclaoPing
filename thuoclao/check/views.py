from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.urls import reverse
from pprint import pprint

from .models import Host, Service
from lib.display_metric import Display


def index(request):
    if request.user.is_authenticated:
        context = {}
        user_id = User.objects.get(username=request.user.username).id
        hosts = Host.objects.filter(user_id=user_id)
        services = Service.objects.filter(host__in=hosts).distinct()
        # hosts = hosts.filter(service__in=services)
        context['hosts'] = hosts
        context['services'] = services
        context['count_host'] = len(hosts)
        context['count_service'] = len(services)

        display = Display('ping', '8.8.8.8', 'minhkma', '1m')
        res = display.select()
        pprint(res)
        context['res'] = res
        return render(request, 'check/index.html', context)
    else:
        return HttpResponseRedirect('/accounts/login')


def view_html(request):
    context = {}
    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('./' + load_template)
    return HttpResponse(template.render(context, request))


def host(request):
    context = {}
    user = User.objects.get(username=request.user.username)
    hosts = Host.objects.filter(user_id=user.id)
    services = Service.objects.filter(host__in=hosts).distinct()

    list_service = [service.service_name for service in services]   # ex ['HTTP', 'PING']
    context['list_service'] = list_service
    context['hosts'] = hosts
    if request.method == 'POST':
        hostname = request.POST.get('hostname')
        ip_address = request.POST.get('ip-host')
        host_data = Host(hostname=hostname, ip_address=ip_address, user=user)
        host_data.save()

        check = request.POST.getlist('checks[]')  # checklist: HTTP, Ping

        for item in check:
            if item.upper() in list_service:  # service existed
                for service in services.filter(service_name=item.upper()):
                    service.host.add(host_data.id)
            else:  # service does not exist
                service_data = Service(service_name=item.upper(), ok=0, warning=0, critical=0, interval_check=0)
                service_data.save()
                service_data.host.add(host_data)
        return HttpResponseRedirect(reverse('host'))
    return render(request, 'check/host.html', context)


def delete_host(request, host_id):
    host_data = Host.objects.filter(id=host_id)
    host_data.delete()
    return HttpResponseRedirect(reverse('host'))


def edit_host(request, host_id):
    host_data = Host.objects.filter(id=host_id)
    user = User.objects.get(username=request.user.username)
    # services = Service.objects.filter(host__in=hosts).distinct()

    if request.method == 'POST':
        hostname = request.POST.get('hostname')
        ip_address = request.POST.get('ip-host')
        host_data.update(hostname=hostname, ip_address=ip_address, user=user)
        check = request.POST.getlist('checks[]')
        # for item in check:
        #     for service in services:
        #         if service.service_name.lower() == item:
        #             service.host.add(host_data.id)
    return HttpResponseRedirect(reverse('host'))


def service(request):
    context = {}
    user_id = User.objects.get(username=request.user.username).id
    hosts = Host.objects.filter(user_id=user_id)
    services = Service.objects.filter(host__in=hosts).distinct()
    context['services'] = services
    return render(request, 'check/service.html', context)


def config_service(request, service_id):
    service_data = Service.objects.filter(id=service_id)
    if request.method == 'POST':
        ok = request.POST.get('ok')
        warning = request.POST.get('warning')
        critical = request.POST.get('critical')
        interval_check = request.POST.get('interval_check')
        service_data.update(ok=ok, warning=warning, critical=critical, interval_check=interval_check)
    return HttpResponseRedirect(reverse('service'))


def remove_service(request, service_id):
    service_data = Service.objects.filter(id=service_id)
    service_data.delete()
    return HttpResponseRedirect(reverse('service'))