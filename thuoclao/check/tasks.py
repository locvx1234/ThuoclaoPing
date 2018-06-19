import asyncio
import signal
import re
import aiohttp

from background_task import background
from django.contrib.auth.models import User
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, SmallInteger, String, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, aliased
from sqlalchemy import event
from pathlib import Path
from influxdb import InfluxDBClient

from check.models import Alert, Host, Service
from thuoclao import settings
from lib.display_metric import Display


Base = declarative_base()
metadata = Base.metadata


class AuthGroup(Base):
    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)


class AuthGroupPermission(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        Index('auth_group_permissions_group_id_permission_id_0cd325b0_uniq', 'group_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('auth_group.id'), nullable=False)
    permission_id = Column(ForeignKey('auth_permission.id'), nullable=False, index=True)

    group = relationship('AuthGroup')
    permission = relationship('AuthPermission')


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        Index('auth_permission_content_type_id_codename_01ab375a_uniq', 'content_type_id', 'codename', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id'), nullable=False)
    codename = Column(String(100), nullable=False)

    content_type = relationship('DjangoContentType')


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime)
    is_superuser = Column(Integer, nullable=False)
    username = Column(String(150), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False)
    is_staff = Column(Integer, nullable=False)
    is_active = Column(Integer, nullable=False)
    date_joined = Column(DateTime, nullable=False)


class AuthUserGroup(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        Index('auth_user_groups_user_id_group_id_94350c0c_uniq', 'user_id', 'group_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False)
    group_id = Column(ForeignKey('auth_group.id'), nullable=False, index=True)

    group = relationship('AuthGroup')
    user = relationship('AuthUser')


class AuthUserUserPermission(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        Index('auth_user_user_permissions_user_id_permission_id_14a6b632_uniq', 'user_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False)
    permission_id = Column(ForeignKey('auth_permission.id'), nullable=False, index=True)

    permission = relationship('AuthPermission')
    user = relationship('AuthUser')


class CheckHost(Base):
    __tablename__ = 'check_host'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(45), nullable=False)
    ip_address = Column(String(39), nullable=False)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False, index=True)

    user = relationship('AuthUser')


class CheckService(Base):
    __tablename__ = 'check_service'

    id = Column(Integer, primary_key=True)
    service_name = Column(String(45), nullable=False)
    ok = Column(Integer)
    warning = Column(Integer)
    critical = Column(Integer)
    interval_check = Column(Integer)


class CheckAlert(CheckService):
    __tablename__ = 'check_alert'

    service_id = Column(ForeignKey('check_service.id'), primary_key=True)
    email_alert = Column(String(100), nullable=False)
    telegram_id = Column(String(10), nullable=False)
    webhook = Column(String(200), nullable=False)


class CheckServiceHost(Base):
    __tablename__ = 'check_service_host'
    __table_args__ = (
        Index('check_service_host_service_id_host_id_56d890ff_uniq', 'service_id', 'host_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    service_id = Column(ForeignKey('check_service.id'), nullable=False)
    host_id = Column(ForeignKey('check_host.id'), nullable=False, index=True)

    host = relationship('CheckHost')
    service = relationship('CheckService')


class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'

    id = Column(Integer, primary_key=True)
    action_time = Column(DateTime, nullable=False)
    object_id = Column(String)
    object_repr = Column(String(200), nullable=False)
    action_flag = Column(SmallInteger, nullable=False)
    change_message = Column(String, nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id'), index=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False, index=True)

    content_type = relationship('DjangoContentType')
    user = relationship('AuthUser')


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        Index('django_content_type_app_label_model_76bd3d3b_uniq', 'app_label', 'model', unique=True),
    )

    id = Column(Integer, primary_key=True)
    app_label = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)


class DjangoMigration(Base):
    __tablename__ = 'django_migrations'

    id = Column(Integer, primary_key=True)
    app = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    applied = Column(DateTime, nullable=False)


class DjangoSession(Base):
    __tablename__ = 'django_session'

    session_key = Column(String(40), primary_key=True)
    session_data = Column(String, nullable=False)
    expire_date = Column(DateTime, nullable=False, index=True)


class GetDataFping():
    def __init__(self, username, password, ip, db):
        self.e = create_engine("mysql+pymysql://{}:{}@{}/{}".format(username, password, ip, db), echo=True)
        self.s = Session(self.e)
        # self.c = self.s.close()

    def get_data_from_mysql(self):
        dict_users = {}
        users = self.s.query(AuthUser).all()
        for user in users:
            service_info = {}
            hosts_id = []
            ips = []
            hosts = self.s.query(CheckHost).filter(CheckHost.user_id == user.id).all()
            for host in hosts:
                hosts_id.append(host.id)
            services = self.s.query(CheckServiceHost).filter(CheckServiceHost.host_id.in_(hosts_id)).all()
            for service in services:
                if service.service.service_name == "PING":
                    ips.append(service.host.ip_address)
            service_info['PING'] = ips
            dict_users[user.username] = service_info
        self.s.close()
        return dict_users


fping_regex = re.compile(
    r"(?P<host>[^ ]+)\s*:.+=\s*(?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)"
    r"(.+=\s*(?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+))?")


def cmd_fping(hosts):
    number_packet = '20'
    cmd = ['fping', '-c', '{}'.format(number_packet)]
    cmd.extend(hosts)
    cmd = ' '.join(cmd)
    return cmd


def write_influxdb(data, user, host_db=None, port=None, username=None,
                   password=None, database=None):
    host_db = host_db or settings.INFLUXDB_HOST
    port = port or settings.INFLUXDB_PORT
    username = username or settings.INFLUXDB_USER
    password = password or settings.INFLUXDB_USER_PASSWORD
    database = database or settings.INFLUXDB_DB
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


async def run_command(*args, user):
    process = await asyncio.create_subprocess_shell(
        *args,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    for line in stderr.decode().split('\n'):
        # print('line ne: {}'.format(line))
        data = fping_regex.match(line)
        if data:
            print("PRE WRITE DB")
            write_influxdb(data=data, user=user)
            print("AFTER WRITE DB")
    return stderr.decode().strip()


@background(schedule=5)
def demo():
    SQL = GetDataFping(username=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
                       ip=settings.DATABASES['default']['HOST'], db=settings.DATABASES['default']['NAME'])
    data_sql = SQL.get_data_from_mysql()
    SQL.s.close()
    # print(data_sql)
    print("demo called")
    loop = asyncio.get_event_loop()
    cmds = []
    for user in data_sql:
        if data_sql[user]["PING"]:
            hosts = []
            hosts.extend(data_sql[user]["PING"])
            for host in hosts:
                cmd = cmd_fping([host])
                cmds.append(run_command(cmd, user=user))
        # print(hosts)
    commands = asyncio.gather(*cmds)
    loop.run_until_complete(commands)


demo(repeat=30)


@background(schedule=5, )
def notify_user(user_id):
    # print(user_id)
    user = User.objects.get(id=user_id)
    alert = Alert.objects.get(user=user)
    hosts = Host.objects.filter(user=user)

    for host in hosts:
        ping = Service.objects.get(host=host, service_name="PING")
        display = Display(ping.service_name.lower(), host.ip_address, user.username)
        alert_data = display.check_ping_notify(ping.ok, ping.warning, ping.critical)
        print(alert_data)
        if alert_data[0] != host.status_ping:  # status changed
            host.status_ping = alert_data[0]
            host.save()
            message = """
            *[{0}] Notify to check !!! {1}*
            ```
            Host : {1}
            Adress : {2}
            Loss : {3}%
            Status : {0}
            ```
            """.format(alert_data[3], host.hostname, host.ip_address, alert_data[1])
            if alert.email_alert:
                alert.send_email(settings.FROM_EMAIL, [],
                                 "[{}] Notify to check {}".format(alert_data[3], host.hostname),
                                 "Hostname {} \nAddress {} \nLoss {}% - {}"
                                 .format(host.hostname, host.ip_address,
                                         alert_data[1], alert_data[3]),
                                 settings.PASSWD_MAIL, settings.SMTP_SERVER)

            if alert.telegram_id:
                alert.send_telegram_message(settings.TOKEN, message)

            if alert.webhook:
                alert.send_slack_message(message)


all_user = User.objects.all()


for user in all_user:
    print(user)
    try:
        alert = Alert.objects.get(user=user)
    except Alert.DoesNotExist:
        break
    notify_user(user.id, repeat=alert.delay_check)
