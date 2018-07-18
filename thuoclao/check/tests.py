from django.test import TestCase, Client
from check.models import Group, Group_attribute, Host_attribute, Service, Host, Alert
from django.contrib.auth.models import User
from lib.utils import Auth


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        # self.users = [User(username='test', password='test'),
        #              User(username= 'test1', password='test1')]
        self.users = [User.objects.create(username='test', password='test'),
                      User.objects.create(username= 'test1', password='test1')]
        self.alert = Alert.objects.create(user= self.users[0],
                           email_alert= 'nguyenvanminhkma@gmail.com',
                           telegram_id= '481523352',
                           webhook= 'https://hooks.slack.com/services/'
                                    'T43EZN8L8/BAH1W0F2M/'
                                    'X6j7twjNgLWyu9PKodrD2OQs')
        self.services = [Service.objects.create(service_name= 'http'),
                        Service.objects.create(service_name= 'ping')]
        self.groups = [Group.objects.create(user = self.users[0],
                             service= self.services[0],
                             group_name= 'test_http_01',
                             ok= 10,
                             warning= 40,
                             critical= 90),
                       Group.objects.create(user = self.users[0],
                             service= self.services[1],
                             group_name= 'test_ping_01',
                             ok= 20,
                             warning= 50,
                             critical= 80)]
        self.group_attr = [Group_attribute.objects.create(group= self.groups[1],
                                           attribute_name= 'interval_ping',
                                           value= 10,
                                           type_value= 0),
                           Group_attribute.objects.create(group= self.groups[1],
                                           attribute_name= 'number_packet',
                                           value= 10,
                                           type_value= 0)]
        self.hosts = [Host.objects.create(hostname= 'host_test_1',
                                          group= self.groups[1]),
                      Host.objects.create(hostname= 'host_test_2',
                                          group= self.groups[1])]
        self.host_attr = [Host_attribute.objects.create
                          (attribute_name= 'ip_address',
                                         value= '8.8.8.8',
                                         type_value= 4,
                                         host= self.hosts[0]),
                          Host_attribute.objects.create
                          (attribute_name= 'ip_address',
                                         value= '1.1.1.1',
                                         type_value= 4,
                                         host= self.hosts[1])]
        # self.client_influxdb = Auth.auth(host_db= '192.168.30.67',
        #                                  port= 8086,
        #                                  username= 'minhkma',
        #                                  password= 'minhkma',
        #                                  database= 'thuoclao')
    def test_user(self):
        # user1 = User.objects.get(username= "test")
        # self.assertEqual(user1.username, 'test')
        self.assertEqual(User.objects.get(username= "test"), self.users[0])
        self.assertEqual(User.objects.get(username= "test1"), self.users[1])
    def test_alert(self):
        user = User.objects.get(username= "test")
        self.assertEqual(Alert.objects.get(user_id = user.id), self.alert)
    def test_services(self):
        self.assertEqual(Service.objects.get(service_name = 'http'),
                                           self.services[0])
        self.assertEqual(Service.objects.get(service_name = 'ping'),
                                           self.services[1])
    def test_group(self):
        self.assertEqual(Group.objects.get(group_name= 'test_http_01'),
                         self.groups[0])
        self.assertEqual(Group.objects.get(group_name= 'test_ping_01'),
                         self.groups[1])
    def test_group_attr(self):
        self.assertEqual(Group_attribute.objects.get
                         (attribute_name= 'interval_ping'), self.group_attr[0])
        self.assertEqual(Group_attribute.objects.get
                         (attribute_name= 'number_packet'), self.group_attr[1])
    def test_host(self):
        self.assertEqual(Host.objects.get(hostname= 'host_test_1'),
                         self.hosts[0])
        self.assertEqual(Host.objects.get(hostname= 'host_test_2'),
                         self.hosts[1])
    def test_host_attr(self):
        self.assertEqual(Host_attribute.objects.get(host= self.hosts[0]),
                         self.host_attr[0])
        self.assertEqual(Host_attribute.objects.get(host= self.hosts[1]),
                         self.host_attr[1])
    def test_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
    def test_host_ping(self):
        response = self.client.get("/host/ping")
        self.assertEqual(response.status_code, 301)
    def test_host_http(self):
        response = self.client.get("/host/http")
        self.assertEqual(response.status_code, 301)
