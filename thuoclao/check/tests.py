from django.test import TestCase, Client
from check.models import Group, Group_attribute, Host_attribute, Service, Host, Alert
from django.contrib.auth.models import User
from lib.utils import Auth


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        # self.users = [User(username='test', password='test'),
        #              User(username= 'test1', password='test1')]
        # self.alert = Alert(user= self.users[0],
        #                    email_alert= 'nguyenvanminhkma@gmail.com',
        #                    telegram_id= '481523352',
        #                    webhook= 'https://hooks.slack.com/services/'
        #                             'T43EZN8L8/BAH1W0F2M/'
        #                             'X6j7twjNgLWyu9PKodrD2OQs')
        # self.services = [Service(service_name= 'http'),
        #                 Service(service_name= 'ping')]
        # self.groups = [Group(user = self.users[0],
        #                      service= self.services[0],
        #                      group_name= 'test_http_01',
        #                      ok= 10,
        #                      warning= 40,
        #                      critical= 90),
        #                Group(user = self.users[0],
        #                      service= self.services[1],
        #                      group_name= 'test_ping_01',
        #                      ok= 20,
        #                      warning= 50,
        #                      critical= 80)]
        # self.group_attr = [Group_attribute(group= self.groups[1],
        #                                    attribute_name= 'interval_ping',
        #                                    value= 10,
        #                                    type_value= 0),
        #                    Group_attribute(group= self.groups[1],
        #                                    attribute_name= 'number_packet',
        #                                    value= 10,
        #                                    type_value= 0)]
        # self.hosts = [Host(hostname= 'host_test_1', group= self.groups[1]),
        #               Host(hostname= 'host_test_2', group= self.groups[1])]
        # self.host_attr = [Host_attribute(attribute_name= 'ip_address',
        #                                  value= '8.8.8.8',
        #                                  type_value= 4,
        #                                  host= self.hosts[0]),
        #                   Host_attribute(attribute_name= 'ip_address',
        #                                  value= '1.1.1.1',
        #                                  type_value= 4,
        #                                  host= self.hosts[1])]
        # self.client_influxdb = Auth.auth(host_db= '192.168.30.67',
        #                                  port= 8086,
        #                                  username= 'minhkma',
        #                                  password= 'minhkma',
        #                                  database= 'thuoclao')

    def test_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
    def test_host_ping(self):
        response = self.client.get("/host/ping")
        self.assertEqual(response.status_code, 301)
    def test_host_http(self):
        response = self.client.get("/host/http")
        self.assertEqual(response.status_code, 301)
    # def test_scheme(self):
    #     self.assertEqual('https://192.168.30.67:8086', self.client_influxdb._baseurl)
