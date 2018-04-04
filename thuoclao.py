import subprocess
import re
import threading
from influxdb import InfluxDBClient

fping_regex = re.compile(
    r"(?P<host>[^ ]+)\s*:.+=\s*(?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)"
    r"(.+=\s*(?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+))?")


def cmd_fping():
    number_packet = '20'
    cmd = ['fping', '-c', '{}'.format(number_packet)]
    hosts = ['192.168.100.30', '192.168.100.31',
             '192.168.100.57', '192.168.100.134',
             '192.168.100.58', 'dantri.vn', '8.8.8.8',
             'facebook.com', 'youtube.com', '192.168.100.104' ]
    cmd.extend([host for host in hosts])
    return cmd


def exc():
    cmd = cmd_fping()
    print(cmd)
    result = subprocess.run(cmd,stderr=subprocess.PIPE)
    result_lines = result.stderr.decode("utf-8")
    list_lines = []
    for line in result_lines.split('\n'):
        list_lines.append(line)
    return list_lines


def write_influxdb(data, host_db= None, port= None, username= None,
                   password= None, database= None):
    host_db = host_db or '192.168.100.57'
    port = port or 8086
    username = username or 'minhkma'
    password = password or 'minhkma'
    database = database or 'thuoclao'
    client = InfluxDBClient(host=host_db, port=port, username=username,
                            password=password, database=database)
    json_body = [
        {
            "measurement": "fping",
            "tags": {
                "host": str(data.group("host")) if data.group("host") else 0
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
    # print(str(data.group("host")))
    client.write_points(json_body)


def main():
    threading.Timer(30.0, main).start()
    list_lines = exc()
    for line in list_lines:
        data = fping_regex.match(line)
        write_influxdb(data=data)


main()