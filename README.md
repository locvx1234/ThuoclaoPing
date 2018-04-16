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
(env)$ cd ThuoclaoPing/thuoclao
(env)$ pip install -r requirements.txt
```

Create databate : 

```
(env)$ python manage.py makemigratetions
(env)$ python manage.py migrate
```

Create superuser:

```
(env)$ python manage.py createsuperuser
```

Runserver: 

```
(env)$ python manage.py runserver 
```




