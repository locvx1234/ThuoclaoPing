import requests
import time
from influxdb import InfluxDBClient
import threading


def hit_site(url):
    print(url)
    try:
        start = time.time()
        r = requests.get(url, stream=True)
        roundtrip = time.time() - start
        request = {}
        request["url"] = url
        request["RTT"] = roundtrip
        request["http-code"] = r.status_code
        return request
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        pass


def write_influxdb(data, host_db=None, port=None, username= None,
                   password=None, database=None):
    host_db = host_db or '192.168.40.120'
    port = port or 8086
    username = username or 'locvu'
    password = password or '123456'
    database = database or 'thuoclao'
    client = InfluxDBClient(host=host_db, port=port, username=username,
                            password=password, database=database)
    json_body = [
        {
            "measurement": "http",
            "tags": {
                "host": data['url']
            },
            "fields": {
                "code": data['http-code'],
                "rtt": data['RTT']
            }
        }
    ]
    client.write_points(json_body)


def http_check():
    urls = ['http://dantri.vn', 'http://hocfreeit.me',
            'https://facebook.com', 'https://youtube.com', 'http://192.168.100.114', 'https://youtube.com/hihi']
    for url in urls:
        data = hit_site(url)
        if data is not None:
            # print(data)
            write_influxdb(data=data)
    return


def main():
    threading.Timer(30.0, main).start()
    http_check()


if __name__ == '__main__':
    main()