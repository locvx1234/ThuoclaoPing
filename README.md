# ThuoclaoPing


 
Environment 
-----------
python3.5

pip9.0.2


Install
-------

Use Virtualenv [Options]

```
$ virtualenv -p python3 env
$ source env/bin/activate
```

Clone and install dependences :

```
(env)$ git clone https://github.com/locvx1234/ThuoclaoPing
(env)$ cd ThuoclaoPing
(env)$ pip install -r requirements.txt
```

Create databate : 

```
(env)$ cd thuoclao
(env)$ python manage.py makemigrations
(env)$ python manage.py migrate
```

Create superuser:

```
(env)$ python manage.py createsuperuser
```

Runserver: 

```
(env)$ python manage.py runserver 0.0.0.0:8000
```

Another session:

```
(env)$ python manage.py process_tasks
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


