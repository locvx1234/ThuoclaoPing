from background_task import background
from django.contrib.auth.models import User
from .models import Alert, Host, Service, Group, Group_attribute
import asyncio
import re
from datetime import datetime
from influxdb import InfluxDBClient
from requests_futures.sessions import FuturesSession
import time


def get_fping():
    users = User.objects.all()
    data = {}
    for user in users:
        # print(user.username)
        service = Service.objects.get(service_name='ping')
        user = User.objects.get(username=user.username)
        all_groups = Group.objects.filter(user_id=user.id, service=service)
        all_hosts = Host.objects.filter(group__in=all_groups)
        hosts = []
        for host in all_hosts:
            item = {'id': host.id, 'hostname': host.hostname, 'status': host.status,
                'description': host.description, 'group_name': host.group.group_name}
            ip_addr = host.host_attribute_set.get(attribute_name='ip_address')
            item['ip_address'] = ip_addr.value
            item['number_packet'] = host.group.group_attribute_set.get(attribute_name='number_packet').value
            item['interval_ping'] = host.group.group_attribute_set.get(attribute_name='interval_ping').value
            hosts.append(item)
        data[user.username] = hosts
    # print(data)
    return data


def get_http():
    users = User.objects.all()
    data = {}
    for user in users:
        # print(user.username)
        service = Service.objects.get(service_name='http')
        user = User.objects.get(username=user.username)
        all_groups = Group.objects.filter(user_id=user.id, service=service)
        all_hosts = Host.objects.filter(group__in=all_groups)
        hosts = []
        for host in all_hosts:
            item = {'id': host.id, 'hostname': host.hostname, 'status': host.status,
                'description': host.description, 'group_name': host.group.group_name}
            item['interval_check'] = host.group.group_attribute_set.get(attribute_name='interval_check').value
            url = host.host_attribute_set.get(attribute_name='url')
            item['url'] = url.value
            hosts.append(item)
        data[user.username] = hosts
    # print(data)
    return data


fping_regex = re.compile(
    r"(?P<host>[^ ]+)\s*:.+=\s*(?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)"
    r"(.+=\s*(?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+))?")


def write_influxdb(data, user, hostname, group_name,
                   host_db=None, port=None, username=None,
                   password=None, database=None):
    host_db = host_db or '192.168.30.67'
    port = port or 8086
    username = username or 'minhkma'
    password = password or 'minhkma'
    database = database or 'thuoclao'
    client = InfluxDBClient(host=host_db, port=port, username=username,
                            password=password, database=database)
    json_body = [
        {
            "measurement": "ping",
            "tags": {
                "user": str(user),
                "ip": str(data.group("host")),
                "group": str(group_name),
                "hostname": str(hostname)
            },
            "fields": {
                "sent": int(data.group("sent")) if data.group("sent") else 0,
                "recv": int(data.group("recv")) if data.group("recv") else 0,
                "loss": int(data.group("loss")) if data.group("loss") else 0,
                "min": float(data.group("min")) if data.group("min") else 0.0,
                "avg": float(data.group("avg")) if data.group("avg") else 0.0,
                "max": float(data.group("max")) if data.group("max") else 0.0
            }
        }
    ]
    client.write_points(json_body)


async def custom_sleep(interval, user, hostname, group_name, stdout, stderr):
    await asyncio.sleep(interval)
    print(type(interval))
    print(stdout, stderr)
    for line in stderr.decode().split('\n'):
        data = fping_regex.match(line)
        if data:
            write_influxdb(data=data, user= user, hostname= hostname,
                           group_name= group_name)
    print('SLEEP {}\n'.format(datetime.now()))


async def factorial(interval, user, hostname, group, *args):
    process = await asyncio.create_subprocess_shell(
        *args,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    await custom_sleep(interval, user, hostname, group, stdout, stderr)


async def loop_exec(loop, interval, user,
                    hostname, group_name, number_packet, ip):
    while loop.is_running():
        tasks = [
            asyncio.ensure_future(factorial(interval,
                                            user,
                                            hostname,
                                            group_name,
                                            'fping -c {0} {1}'
                                            .format(number_packet, ip)))
        ]
        await asyncio.wait(tasks)
    loop.call_soon(loop.create_task, loop_exec(loop, interval, user,
                                               hostname, group_name,
                                               number_packet, ip))


session = FuturesSession()

def bg_cb(sess, resp, hostname, group_name, user,
          host_db= None, port= None, username= None,
                   password= None, database= None):
    host_db = host_db or '192.168.30.67'
    port = port or 8086
    username = username or 'minhkma'
    password = password or 'minhkma'
    database = database or 'thuoclao'
    client = InfluxDBClient(host=host_db, port=port, username=username,
                            password=password, database=database)
    json_body = [
        {
            "measurement": "http",
            "tags": {
                "url": str(resp.url),
                'hostname': str(hostname),
                'group': str(group_name),
                'username': str(user)
            },
            "fields":
                {
                    "code": int(resp.status_code),
                    "response": float(resp.elapsed.total_seconds())
                }

        }
    ]
    client.write_points(json_body)
    # print("<---  {}".format(time.time()))


async def http_exec(loop, url, interval, hostname, group_name, user):
    future = session.get(url,
                         background_callback=lambda sess,
                                                    resp: bg_cb(sess,
                                                                resp,
                                                                hostname= hostname,
                                                                group_name=group_name,
                                                                user=user))
    # response = future.result()
    # pprint(response.data)
    loop.call_later(int(interval), loop.create_task, http_exec(loop, url, int(interval),
                                                          hostname, group_name,
                                                          user))


@background(schedule=0)
def http():
    data_http = get_http()
    print(data_http)
    loop = asyncio.get_event_loop()
    for user in data_http:
        for count, info_url in enumerate(data_http[user]):
            url = info_url['url']
            # print(url)
            hostname = info_url['hostname']
            group_name = info_url['group_name']
            interval = int(info_url['interval_check'])
            print(url, hostname, group_name, interval)
            loop.call_soon(loop.create_task, http_exec(loop, url, int(interval),
                                                      hostname, group_name,
                                                       user))
    loop.run_forever()
http()

@background(schedule=0)
def fping():
    loop = asyncio.get_event_loop()
    data_ping = get_fping()
    print(data_ping)
    for user in data_ping:
        for count, info_ping in enumerate(data_ping[user]):
            ip = info_ping['ip_address']
            hostname = info_ping['hostname']
            group_name = info_ping['group_name']
            interval = int(info_ping['interval_ping'])
            number_packet = info_ping['number_packet']
            print('fping -c {} {}'.format(number_packet, ip))
            loop.call_soon(loop.create_task, loop_exec(loop, interval, user,
                                               hostname, group_name,
                                               number_packet, ip))
            # tasks.append(asyncio.ensure_future(factorial(interval,
            #                                              user,
            #                                              hostname,
            #                                              group_name,
            #                                              'fping -c {0} {1}'
            #                                              .format(number_packet,
            #                                                      ip)
            #                                              )))
    # loop.create_task(loop_exec(loop))
    loop.run_forever()
fping()