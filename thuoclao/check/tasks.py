from background_task import background
from django.contrib.auth.models import User
from .models import Alert, Host, Service, Group, Group_attribute
import asyncio
import re
from datetime import datetime
from influxdb import InfluxDBClient

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
            hosts.append(item)
        data[user.username] = hosts
    # print(data)
    return data


fping_regex = re.compile(
    r"(?P<host>[^ ]+)\s*:.+=\s*(?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)"
    r"(.+=\s*(?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+))?")


def write_influxdb(data, user, host_db=None, port=None, username=None,
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
                "host": str(data.group("host"))
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


async def custom_sleep(interval, stdout, stderr):
    await asyncio.sleep(interval)
    print(stdout, stderr)
    for line in stderr.decode().split('\n'):
        data = fping_regex.match(line)
        if data:
            write_influxdb(data=data, user='minhkma')
    print('SLEEP {}\n'.format(datetime.now()))


async def factorial(interval, *args):
    process = await asyncio.create_subprocess_shell(
        *args,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    await custom_sleep(interval, stdout, stderr)


async def loop_exec(loop):
    while loop.is_running():
        tasks = [
            asyncio.ensure_future(factorial(2, 'fping -c 4 dantri.vn')),
            asyncio.ensure_future(factorial(3, 'fping -c 4 google.com')),
        ]
        await asyncio.wait(tasks)


# async def loop_exec(loop, tasks):
#     while loop.is_running():
#         # tasks = [
#         #     asyncio.ensure_future(factorial(2, 'fping -c 4 dantri.vn')),
#         #     asyncio.ensure_future(factorial(3, 'fping -c 4 google.com')),
#         # ]
#         await asyncio.wait(tasks)

@background(schedule=0)
def fping():
    data_ping = get_fping()
    data_http = get_http()
    # loop = asyncio.get_event_loop()
    # loop.create_task(loop_exec(loop, tasks))
    # loop.create_task(loop_exec(loop))
    # loop.run_forever()
    print(data_ping)
    print(data_http)
fping()