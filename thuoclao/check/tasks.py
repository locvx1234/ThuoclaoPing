from background_task import background
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, SmallInteger, String, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, aliased
from sqlalchemy import event
import time
from pathlib import Path
import functools
import asyncio
import aiohttp
import logging
import signal
import yaml
import re
import time



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
        return  dict_users


logger = logging.getLogger(__name__)
escapeseq = str.maketrans({',': '\,', ' ': '\ ', '=': '\=', '\n': ''})


class Dest:
    def __init__(self, user, IP):
        self.user = user
        self.ip = IP
        self._tags = {
            "user": self.user,
            "host": self.ip,
        }
    def tags(self):
        t = self._tags.copy()
        # print(t)
        return t


class Point:
    def __init__(self, mesurement, ts=None, *, fields={}, tags={}):
        self.mesurement = mesurement
        self.fields = fields
        self.tags = tags
        self.timestamp = ts

    def __str__(self):
        return f"{self.mesurement} fields={self.fields} tags={self.tags}"

    def _encode(self, string):
        return str(string).translate(escapeseq)

    def _encode_field(self, field, value):
        f = self._encode(field)
        v = self._encode(value)
        if isinstance(value, int):
            return f"{f}={v}i"
        elif isinstance(value, (bool, float)):
            return f"{f}={v}"
        else:
            return f'{f}="{v}"'

    def encode_line(self):
        timestamp = ''  # Server calculated timestamp
        if self.timestamp:
            timestamp = ' {}'.format(self.timestamp)
        if self.tags:
            tags = ','.join(
                [''] + [
                    "{}={}".format(self._encode(k), self._encode(v))
                    for k, v in self.tags.items()
                ]
            )
        else:
            tags = ''
        mesurement = self._encode(self.mesurement)
        fields = ','.join([self._encode_field(k, v) for k, v in self.fields.items()])
        # print('{}{} {}{}\n'.format(mesurement, tags, fields, timestamp))
        return f"{mesurement}{tags} {fields}{timestamp}\n".encode("utf-8")


class InfluxDBClient:
    def __init__(self, url, database, username, password, *, loop=None):
        auth = None
        if username and password:
            auth = aiohttp.BasicAuth(username, password)
        self.session = aiohttp.ClientSession(
            loop=asyncio.get_event_loop() if loop is None else loop,
            auth=auth)
        self.db = database
        if not url.endswith("/"):
            url += "/"
        self._url = url

    def url(self, endpoint):
        url = self._url
        if endpoint == "ping":
            return f"{url}{endpoint}"
        else:
            db = self.db
            return f"{url}{endpoint}?db={db}"

    async def ping(self):
        async with self.session.get(self.url("ping")) as r:
            return r.status == 204

    async def write(self, point):
        data = point.encode_line()
        logger.debug("write {}".format(data))
        async with self.session.post(self.url("write"), data=data) as r:
            if r.status != 204:
                logger.error("influxdb write failed: %s", await r.text())
            return r

class Prober:
    fping_re = re.compile(
        r"(?P<host>[^ ]+)\s*:.+=\s*(?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)(.+=\s*(?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+))?")
    def __init__(self, influxclient, dests):
        # self.probername = probername
        self.dests = {d.ip: d for d in dests}  # Fast lookup
        # print('day la dests {}'.format(self.dests))
        self.process = None
        self.influxclient = influxclient
        self.stop_event = asyncio.Event()

    def __repr__(self):
        return "<Prober of {}>".format(','.join(self.dests.keys()))

    def get_process(self):
        base_cmd = [
            "fping",
            "-c", "20"
        ]
        cmd = base_cmd + [d.ip for d in self.dests.values()]
        print("execute {}".format(' '.join(cmd)))
        print(time.time())
        # print(cmd)
        return asyncio.create_subprocess_exec(
            *cmd,
            stdin=None,
            stdout=None,
            stderr=asyncio.subprocess.PIPE)

    def stop(self):
        self.stop_event.set()

    def readline(self, task):
        result = task.result()
        # print(result)
        m = self.fping_re.match(result.decode("utf-8").strip())
        # print("Day la m:{}\n".format(m))
        if m:
            destname = m.group("host")
            # print(destname)
            dest = self.dests.get(destname)
            if not dest:
                print("{} not found in {}".format(destname, self.dests.keys()))
                return
            asyncio.async(self.influxclient.write(
                Point(
                    "ping",
                    fields={
                        "sent": int(m.group("sent")),
                        "recv": int(m.group( "recv")),
                        "loss": int(m.group("loss")),
                        "min": float(m.group("min")) if m.group("min") else 0.0,
                        "avg": float(m.group("avg")) if m.group("avg") else 0.0,
                        "max": float(m.group("max")) if m.group("max") else 0.0,
                    },
                    tags=dest.tags(),
                )
            ))
            # print(Point)

    def stopped(self, process, task):
        if process.returncode is None:
            process.terminate()

    async def run(self):
        process = await self.get_process()
        stop_future = asyncio.ensure_future(self.stop_event.wait())
        stop_future.add_done_callback(functools.partial(self.stopped, process))
        # readline_future = asyncio.ensure_future(process.stderr.readline())
        # readline_future.add_done_callback(self.readline)
        while not self.stop_event.is_set():
            readline_future = asyncio.ensure_future(process.stderr.readline())
            readline_future.add_done_callback(self.readline)
            # self.get_process().close()
            await asyncio.wait([
                readline_future,
                stop_future],
                return_when=asyncio.FIRST_COMPLETED)
            # self.get_process().close()
            # process.kill()
            # # Prober.stop()
            # print('tao dang o day')
            # break
            # if process.returncode is not None and not self.stop_event.is_set():
            #     process = await self.get_process()
        process.kill()
        return self


def parse_conf(yamlf):
    confdata = yaml.load(yamlf)
    return confdata


def chunker(l, pool):
    # print('{} : {}'.format(l, pool))
    lists = [[] for x in range(pool)]
    # print(lists)
    for i, e in enumerate(l):
        # print("{} : {}".format(i, e))
        lists[i % pool].append(e)
    # print(lists)
    return lists


def get_fping_probers(data, influxclient, worker_count):
    dests = []
    for user in data:
        for ip in data[user]['PING']:
            dests.append(Dest(user= user, IP= ip))
    return [
        Prober(
            # probername=conf["prober"]["name"],
            influxclient=influxclient,
            dests=pool_dests
        )
        for pool_dests in chunker(dests, worker_count)
    ]


async def monitor_tasks(loop, data):
    # conf = parse_conf(conffile)
    # influxconf = conf["output"]["influxdb"]
    influxclient = InfluxDBClient(
        url="http://192.168.30.67:8086",
        database='thuoclao',
        username='minhkma',
        password='minhkma')
    print("Testing InfluxDB connection: {}".format(
        "OK" if await influxclient.ping() else "FAILED"))

    reload_event = asyncio.Event(loop=loop)
    loop.add_signal_handler(signal.SIGHUP, reload_event.set)
    probers = get_fping_probers(
        data, influxclient=influxclient, worker_count=10)
    tasks = [
        loop.create_task(prober.run())
        for prober in probers
    ]
    # print(tasks)
    # while True:
    #     await reload_event.wait()
    #     if reload_event.is_set():
    #         print("reload")
    #         # conffile.seek(0)
    #         # conf = parse_conf(conffile)
    #         reload_event.clear()
    #         for p in probers:
    #             p.stop()
    #         for task in tasks:
    #             task.cancel()
    #         probers = get_fping_probers(
    #             data, influxclient=influxclient, worker_count=10)
    #         tasks = [
    #             loop.create_task(prober.run())
    #             for prober in probers
    #         ]
        # loop.stop()
        # print('---------', tasks)

@background(schedule=0)
def test():
    SQL = GetDataFping(username= 'thuoclao', password= 'thuoclao',
                   ip= '192.168.30.61', db= 'thuoclao')
    data = SQL.get_data_from_mysql()
    print(data)
    # import argparse
    # parser = argparse.ArgumentParser(
    #     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # parser.add_argument(
    #     "-w", "--workers", type=int, default=10,
    #     help="parallel probes")
    # parser.add_argument(
    #     "-c", "--config", type=argparse.FileType('r', encoding='utf-8'),
    #     help="configuration",
    #     default=str(Path.home() / "repo" / "aping" / "examples" / "testconf.yml"))
    # print(str(Path.home() / "repo" / "aping" / "examples" / "testconf.yml"))
    # parser.add_argument("--debug", action="store_true")
    # args = parser.parse_args()
    # # print(args.workers)
    # logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor_tasks(loop, data))

test(repeat=30)

