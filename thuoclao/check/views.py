import json
from pprint import pprint
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Host, Service, Alert, Group, Host_attribute, Group_attribute
from .forms import AlertForm
from lib.display_metric import Display
from .serializers import GroupSerializer, GroupAttributeSerializer, HostSerializer, HostAttributeSerializer


def index(request):
    if request.user.is_authenticated:
        user_id = User.objects.get(username=request.user.username).id
        groups = Group.objects.filter(user_id=user_id)
        hosts = Host.objects.filter(group__in=groups)
        services = Service.objects.all()
        context = {'hosts': hosts, 'services': services, 'count_host': len(hosts),
                   'count_service': len(services), 'groups': groups}

        return render(request, 'check/index.html', context)
    else:
        return HttpResponseRedirect('/accounts/login')


def get_data(request, pk_host, service_name, query_time):
    host = Host.objects.get(id=pk_host)
    print(host)
    display = Display(host.group.group_name, host.hostname, host.group.user.username)
    if service_name == 'ping':
        ip_addr = host.host_attribute_set.get(attribute_name='ip_address').value
        res = display.select_ping(ip_addr, query_time)
        # pprint(res)
    if service_name == 'http':
        url = host.host_attribute_set.get(attribute_name='url').value
        res = display.select_http(url, query_time)
        # pprint(res)
    json_data = json.dumps(res)
    return HttpResponse(json_data, content_type="application/json")


def total_parameter(request):
    if request.is_ajax():
        user_id = User.objects.get(username=request.user.username).id
        groups = Group.objects.filter(user_id=user_id)
        hosts = Host.objects.filter(group__in=groups)
        total_ok = hosts.filter(status=0).count()
        total_warning = hosts.filter(status=1).count()
        total_critical = hosts.filter(status=2).count()
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


def host(request, service_name):
    context = {}
    service = Service.objects.get(service_name=service_name)
    user = User.objects.get(username=request.user.username)
    all_groups = Group.objects.filter(user_id=user.id, service=service)
    all_hosts = Host.objects.filter(group__in=all_groups)

    hosts = []
    for host in all_hosts:
        item = {'id': host.id, 'hostname': host.hostname, 'status': host.status,
                'description': host.description, 'group_name': host.group.group_name}
        if service_name == 'ping':
            ip_addr = host.host_attribute_set.get(attribute_name='ip_address')
            item['ip_address'] = ip_addr.value
        if service_name == 'http':
            url = host.host_attribute_set.get(attribute_name='url')
            item['url'] = url.value
        hosts.append(item)

    groups = []
    for group in all_groups:
        item = {'id': group.id, 'group_name': group.group_name, 'hosts': group.host_set.all(),
                'description': group.description, 'ok': group.ok, 'warning': group.warning,
                'critical': group.critical}
        if service_name == 'ping':
            number_packet = group.group_attribute_set.get(attribute_name='number_packet')
            item['number_packet'] = number_packet.value
            interval_ping = group.group_attribute_set.get(attribute_name='interval_ping')
            item['interval_ping'] = interval_ping.value
        if service_name == 'http':
            interval_check = group.group_attribute_set.get(attribute_name='interval_check')
            item['interval_check'] = interval_check.value
        groups.append(item)

    if request.method == 'POST':
        if request.POST.get('hostname'):  # add host
            hostname = request.POST.get('hostname')
            description = request.POST.get('host_description')
            group_id = request.POST.get('group')
            group = Group.objects.get(id=group_id)
            host_data = Host(hostname=hostname, description=description, group=group)
            host_data.save()
            if service_name == 'ping':
                ip_address = request.POST.get('ip-host')
                host_attr_data = Host_attribute(host=host_data, attribute_name="ip_address",
                                                value=ip_address, type_value=4)
            if service_name == 'http':
                url = request.POST.get('url')
                host_attr_data = Host_attribute(host=host_data, attribute_name="url",
                                                value=url, type_value=5)
            host_attr_data.save()

        if request.POST.get('group_name'):  # add group
            group_name = request.POST.get('group_name')
            description = request.POST.get('group_description')
            if service_name == 'ping':
                ok = request.POST.get('ok')
                warning = request.POST.get('warning')
                critical = request.POST.get('critical')
            if service_name == 'http':
                pass
            group_data = Group(user=user, service=service, group_name=group_name, description=description,
                               ok=ok, warning=warning, critical=critical)
            group_data.save()

            if service_name == 'ping':
                interval_ping = request.POST.get('interval_ping')
                number_packet = request.POST.get('number_packet')

                attr_interval_ping = Group_attribute(group=group_data, attribute_name='interval_ping',
                                                     value=interval_ping, type_value=0)
                attr_interval_ping.save()

                attr_num_packet = Group_attribute(group=group_data, attribute_name='number_packet',
                                                  value=number_packet, type_value=0)
                attr_num_packet.save()
            if service_name == 'http':
                interval_check = request.POST.get('interval_check')
                attr_interval_check = Group_attribute(group=group_data, attribute_name='interval_check',
                                                      value=interval_check, type_value=0)
                attr_interval_check.save()

        return HttpResponseRedirect(reverse('host', kwargs={'service_name': service_name}))

    context = {'hosts': hosts, 'groups': groups}
    return render(request, 'check/' + str(service_name) + '.html', context)


def delete_host(request, service_name, host_id):
    host_query = Host.objects.filter(id=host_id)
    host_query.delete()
    return HttpResponseRedirect(reverse('host', kwargs={'service_name': service_name}))


def delete_group(request, service_name, group_id):
    group_query = Group.objects.filter(id=group_id)
    group_query.delete()
    return HttpResponseRedirect(reverse('host', kwargs={'service_name': service_name}))


def edit_host(request, service_name, host_id):
    host_query = Host.objects.get(id=host_id)

    if request.method == 'POST':
        # update host
        host_query.hostname = request.POST.get('hostname')
        host_query.description = request.POST.get('host_description')
        if service_name == 'ping':
            ip_address = request.POST.get('ip-host')
            host_attr_data = Host_attribute.objects.get(host=host_query, attribute_name="ip_address")
            host_attr_data.value = ip_address
        if service_name == 'http':
            url = request.POST.get('url')
            host_attr_data = Host_attribute.objects.get(host=host_query, attribute_name="url")
            host_attr_data.value = url
        host_query.save()
        host_attr_data.save()

    return HttpResponseRedirect(reverse('host', kwargs={'service_name': service_name}))


def edit_group(request, service_name, group_id):
    group_query = Group.objects.get(id=group_id)

    if request.method == 'POST':
        # update group
        group_query.group_name = request.POST.get('group_name')
        group_query.description = request.POST.get('group_description')
        group_query.ok = request.POST.get('ok')
        group_query.warning = request.POST.get('warning')
        group_query.critical = request.POST.get('critical')
        group_query.save()

        if service_name == 'ping':
            attr_interval_ping = Group_attribute.objects.get(group=group_query, attribute_name="interval_ping")
            attr_interval_ping.value = request.POST.get('interval_ping')
            attr_interval_ping.save()
            attr_number_packet = Group_attribute.objects.get(group=group_query, attribute_name="number_packet")
            attr_number_packet.value = request.POST.get('number_packet')
            attr_number_packet.save()
        if service_name == 'http':
            attr_interval_check = Group_attribute.objects.get(group=group_query, attribute_name="interval_check")
            attr_interval_check.value = request.POST.get('interval_check')
            attr_interval_check.save()
    return HttpResponseRedirect(reverse('host', kwargs={'service_name': service_name}))


def alert(request):
    try:
        alert_data = Alert.objects.get(user=request.user)
    except Alert.DoesNotExist:
        alert_data = None

    if request.method == 'POST':
        alert_form = AlertForm(request.POST, instance=alert_data)
        if alert_form.is_valid():
            email_alert = alert_form.data["email_alert"]
            telegram_id = alert_form.data["telegram_id"]
            webhook = alert_form.data["webhook"]

            if alert_data:
                alert_form.save()
            else:
                alert = Alert(user=request.user, email_alert=email_alert, telegram_id=telegram_id, webhook=webhook)
                alert.save()
        return HttpResponseRedirect(reverse('alert'))
    context = {'alert': alert_data}
    return render(request, 'check/alert.html', context)


class GroupList(APIView):
    def get(self, request, format=None):
        groups = Group.objects.filter(user=request.user)
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Group.objects.filter(user=user)
        return queryset


class GroupAttributeViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupAttributeSerializer

    def get_queryset(self):
        user = self.request.user
        groups = Group.objects.filter(user=user)
        queryset = Group_attribute.objects.filter(group__in=groups)
        return queryset


class HostViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = HostSerializer

    def get_queryset(self):
        user = self.request.user
        group = Group.objects.filter(user=user)
        queryset = Host.objects.filter(group__in=group)
        return queryset


class HostAttributeViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = HostAttributeSerializer

    def get_queryset(self):
        user = self.request.user
        groups = Group.objects.filter(user=user)
        hosts = Host.objects.filter(group__in=groups)
        queryset = Host_attribute.objects.filter(host__in=hosts)
        return queryset
