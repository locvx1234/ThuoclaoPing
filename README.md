# ThuoclaoPing


 
Environment 
-----------
python3.6


Install
-------

Clone source code and install dependences:

```
apt update && apt install -y python3-pip fping redis-server mysql-server-5.7 mysql-client-core-5.7 libmysqlclient-dev
git clone https://github.com/locvx1234/ThuoclaoPing
mkdir /code
cp -r ThuoclaoPing/* /code
cd /code
pip3 install -r requirements.txt
```

Mysql:

Start mysql-server

```
systemctl restart mysql-server
```
Create database `thuoclao`

```sh
mysql -u root -p
> CREATE DATABASE thuoclao;
> exit
```

Edit `DATABASES` value in the `/code/thuoclao/thuoclao/settings.py` file

Then import database

```
mysql -h <mysql-server> -u<username> -p thuoclao < docker-entrypoint-initdb.d/thuoclao_init.sql
```

Influx DB: 

Add repo Influxdb

```sh
vi /etc/apt/sources.list.d/influxdb.list
deb https://repos.influxdata.com/ubuntu bionic stable
```
Add key

```
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
```
Install InfluxDB

```sh
apt-get update -y
apt-get install influxdb -y
systemctl start influxdb
```

Create DB user command `influx`

```sh
influx
> CREATE DATABASE thuoclao
> CREATE USER "thuoclao" WITH PASSWORD 'thuoclao' WITH ALL PRIVILEGES
> exit 
```

Turn on mode password

```
sed -i 's/# auth-enabled = false/auth-enabled = true/g'  /etc/influxdb/influxdb.conf
```

Restart Influxdb

```
systemctl restart influxdb
```

Then edit DATABASE_INFLUX value in `/code/thuoclao/thuoclao/settings.py` file

Supervisor:

```
apt install -y supervisor
cp /code/supervisor/supervisord.conf /etc/supervisor/conf.d/
supervisorctl reload
supervisorctl start all
```

Nginx: 

Edit file `/code/nginx/nginx.conf`

Change `web` by `ip-server`

```
apt install -y nginx
ufw allow 'Nginx HTTP'
cp /code/nginx/nginx.conf /etc/nginx/conf.d/
sed -i 's/include \/etc\/nginx\/sites-enabled/#include \/etc\/nginx\/sites-enabled/g' /etc/nginx/nginx.conf
systemctl restart nginx
```

Docker
------

```
$ git clone https://github.com/locvx1234/ThuoclaoPing
$ cd ThuoclaoPing
$ ./rebuild_docker.sh
```

Then, access `http://ip-docker-host`

User : `admin`

Password : `strongpass@@`

Bejoy !


