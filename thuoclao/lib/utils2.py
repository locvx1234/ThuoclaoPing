import configparser
from influxdb import InfluxDBClient
from django.contrib.auth.models import User
from check.models import Host, Service


class GetConfig(object):

    def get_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config


class Auth(GetConfig):
    # def get_conf(self, config_file):
    #     config = configparser.ConfigParser()
    #     config.read(config_file)
    #     return config
    def auth(self, host_db=None, port=None, username=None, password=None, database=None):

        conf = GetConfig()
        config = conf.get_config("lib/test.conf")
        host_db = host_db or config['INFLUX']['IP_influx']
        port = port or config['INFLUX']['port']
        username = username or config['INFLUX']['user']
        password = password or config['INFLUX']['password']
        database = database or config['INFLUX']['database']
        client = InfluxDBClient(host=host_db, port= port, username=username,
                                password=password, database=database)
        return client


class Sqlite(object):
    def get_sql(self):
        dict_users = {}
        users = User.objects.all()
        for user in users:
            dict_hosts = {}
            hosts = Host.objects.filter(user_id= user.id)
            services = Service.objects.filter(host__in= hosts).distinct()
            for ser in services:
                IPs = []
                for ser_info in ser.host.all():
                    IPs.append(ser_info.ip_address)
                dict_hosts[ser.service_name] = IPs
            dict_users[user.username] = dict_hosts
        return dict_users



# auth_test = Auth()
# client = auth_test.auth()
# data = client.query('select * from ping where host=\'8.8.8.8\' and time > now() - 1m', epoch=True)
# print(data)
# print("==========")
# print(data.raw)
