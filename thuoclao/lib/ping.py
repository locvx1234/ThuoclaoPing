import subprocess
import re
import threading
from influxdb import InfluxDBClient
import thuoclao.lib.utils


fping_regex = re.compile(
    r"(?P<host>[^ ]+)\s*:.+=\s*(?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)"
    r"(.+=\s*(?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+))?")


def cmd_fping(number_packet, hosts):
    cmd = ['fping', '-c', '{}'.format(number_packet)]
    cmd.extend([host for host in hosts])
    return cmd


def exc(number_packet, hosts):
    cmd = cmd_fping(number_packet, hosts)
    result = subprocess.run(cmd,stderr=subprocess.PIPE)
    result_lines = result.stderr.decode("utf-8").strip()
    list_lines = []
    for line in result_lines.split('\n'):
        list_lines.append(line)
    return list_lines


def write_influx(self, data, host_db=None, port=None,
                 username=None, password=None, database=None):
    influx = utils.Base()
    config = influx.get_conf('test.conf')
    host_db = host_db or config['INFLUX']['IP_influx']
    port = port or config['INFLUX']['port']
    username = username or config['INFLUX']['user']
    password = password or config['INFLUX']['password']
    database = database or config['INFLUX']['database']
    client = InfluxDBClient(host=host_db, port=port, username=username,
                            password=password, database=database)
    json_body = [
        {
            "measurement": "thuoclao",
            "tags": {
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


def main():
    threading.Timer(30.0, main).start()
    list_lines = exc()
    for line in list_lines:
        data = fping_regex.match(line)
        write_influx(data=data)