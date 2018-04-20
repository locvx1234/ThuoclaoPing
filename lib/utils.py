import configparser
from influxdb import InfluxDBClient


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
    def auth(self, host_db=None, port=None,
                 username=None, password=None, database=None):

        conf = GetConfig()
        config = conf.get_config("test.conf")
        host_db = host_db or config['INFLUX']['IP_influx']
        port = port or config['INFLUX']['port']
        username = username or config['INFLUX']['user']
        password = password or config['INFLUX']['password']
        database = database or config['INFLUX']['database']
        client = InfluxDBClient(host= host_db, port= port, username= username,
                                password= password, database= database)
        return client


auth_test = Auth()
client = auth_test.auth()
data = client.query('select * from fping where host=\'192.168.100.30\' and time > now() - 1m')
print(data)
