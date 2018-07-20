# ThuoclaoPing


 
Environment 
-----------
python3.6

pip9.0.2


Install
-------

Clone source code and install dependences :

```
apt update && apt install -y fping redis-server
git clone https://github.com/locvx1234/ThuoclaoPing
mkdir /code
cp -r ThuoclaoPing/* /code
cd /code
pip install -r requirements.txt
```

Mysql:

Edit `DATABASES` value in the `/code/thuoclao/thuoclao/settings.py` file

Import database 




Supervisor:

```
apt install -y supervisor
cp /code/supervisor/supervisord.conf /etc/supervisor/conf.d/
supervisorctl reload
supervisorctl start all
```

Nginx: 

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

User : admin
Password : strongpass@@

Bejoy !


