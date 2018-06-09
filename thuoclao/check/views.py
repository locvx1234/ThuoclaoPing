import json

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string
from pprint import pprint

from .models import Host, Service, Alert
from .forms import AlertForm
from lib.display_metric import Display


def index(request):
    if request.user.is_authenticated:
        user_id = User.objects.get(username=request.user.username).id
        hosts = Host.objects.filter(user_id=user_id)
        services = Service.objects.filter(host__in=hosts).distinct()
        # hosts = hosts.filter(service__in=services)
        context = {'hosts': hosts, 'services': services, 'count_host': len(hosts), \
                'count_service': len(services)}
        
        return render(request, 'check/index.html', context)
    else:
        return HttpResponseRedirect('/accounts/login')


def get_data(request, pk_host, service_name):
    host = Host.objects.get(id=pk_host)
    service = host.service_set.get(service_name=service_name.lower())
    display = Display(service_name.lower(), host.ip_address, host.user.username)
    res = display.select(service.interval_check)
    json_data = json.dumps(res)
    # pprint(res)
    print(pk_host)
    print(service_name)
    print("#$#$#$#$#$#$#$#$#$#$#$#$#$")
    return HttpResponse(json_data, content_type="application/json")


def total_parameter(request):
    if request.is_ajax():
        user_id = User.objects.get(username=request.user.username).id
        hosts = Host.objects.filter(user_id=user_id)
        total_ok = hosts.filter(status_ping=0).count() + hosts.filter(status_http=0).count()
        total_warning = hosts.filter(status_ping=1).count() + hosts.filter(status_http=1).count()
        total_critical = hosts.filter(status_ping=2).count() + hosts.filter(status_http=2).count()
        context = {'total_ok': total_ok, 'total_warning': total_warning, 'total_critical': total_critical}
        json_data = json.dumps(context)
        print(json_data)
        return HttpResponse(json_data, content_type="application/json")


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
    context['services'] = services
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
                service_data = Service(service_name=item.upper(), ok=10, warning=40, critical=70, interval_check=20)
                service_data.save()
                service_data.host.add(host_data)
        return HttpResponseRedirect(reverse('host'))
    return render(request, 'check/host.html', context)


def delete_host(request, host_id):
    host_data_query = Host.objects.filter(id=host_id)
    host_data_query.delete()
    return HttpResponseRedirect(reverse('host'))


def edit_host(request, host_id):
    host_data_query = Host.objects.filter(id=host_id)
    user = User.objects.get(username=request.user.username)
    hosts = Host.objects.filter(user_id=user.id)
    services = Service.objects.filter(host__in=hosts).distinct()    # cac service hien co cua user do
    services_name = [service.service_name for service in services]

    if request.method == 'POST':
        # update host
        hostname = request.POST.get('hostname')
        ip_address = request.POST.get('ip-host')
        host_data_query.update(hostname=hostname, ip_address=ip_address, user=user)

        # update service
        host_data = Host.objects.get(id=host_id)
        checked = [element for element in request.POST.getlist('checks[]')]  # service_name
        for item in checked:
            if item in services_name:  # update

                service = services.get(service_name=item)

                service.host.add(host_data)
            # else:  # add new
            #     service_data = Service(service_name=item[0], ok=0, warning=0, critical=0, interval_check=0)
            #     service_data.save()
            #     service_data.host.add(host_data.id)
        uncheck_list = list(set(services_name) - set([item for item in checked]))
        for item_uncheck in uncheck_list:
            service = services.get(service_name=item_uncheck)
            service.host.remove(host_data)
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


def alert(request):
    try:
        alert_data = Alert.objects.get(user=request.user)
    except Alert.DoesNotExist:
        alert_data = None

    if request.method == 'POST':
        print(request.user)
        print(request.POST)
        alert_form = AlertForm(request.POST, instance=alert_data)
        if alert_form.is_valid():
            email_alert = alert_form.data["email_alert"]
            telegram_id = alert_form.data["telegram_id"]
            webhook = alert_form.data["webhook"]
            delay_check = alert_form.data["delay_check"]

            if alert_data:
                alert_form.save()
            else:
                alert = Alert(user=request.user, email_alert=email_alert, telegram_id=telegram_id, webhook=webhook, delay_check=delay_check)
                alert.save()
        return HttpResponseRedirect(reverse('alert'))
    context = {'alert': alert_data}
    return render(request, 'check/alert.html', context)

