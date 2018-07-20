import datetime
import statistics

from lib import utils


class Display(utils.Auth):
    def __init__(self, group, hostname, username):
        self.hostname = hostname
        self.username = username
        self.group = group  # group_name
        self.client = self.auth()

    def select_http(self, url, query_time):
        data_http = self.client.query('select * from http '
                                      'where \"hostname\" = \'{}\' '
                                      'and \"group\" = \'{}\' '
                                      'and \"url\" = \'{}\' '
                                      'and \"username\" = \'{}\' '
                                      'and time > now() - {}m'
                                      .format(self.hostname, self.group, url,
                                              self.username, query_time), epoch='ms')
        results_http = list(data_http.get_points(measurement='http'))
        return results_http

    def select_ping(self, ip_add, query_time):
        data_ping = self.client.query('select * from ping '
                                      'where \"hostname\" = \'{}\' '
                                      'and \"group\" = \'{}\' '
                                      'and \"ip\" = \'{}\' '
                                      'and \"username\" = \'{}\' '
                                      'and time > now() - {}m'
                                      .format(self.hostname, self.group, ip_add,
                                              self.username, query_time), epoch='ms')
        results_ping = list(data_ping.get_points(measurement='ping'))
        return results_ping

    def check_ping_notify(self, oke, warning, critical):
        data_status = self.client.query('select mean("loss") from ping '
                                        'where \"hostname\" = \'{}\' '
                                        'and \"group\" = \'{}\' '
                                        'and \"username\" = \'{}\' '
                                        'and time > now() -5m '
                                        .format(self.hostname, self.group, self.username))
        results_status = list(data_status.get_points(measurement='ping'))
        print(results_status)
        try:
            val_status = round(results_status[0]['mean'], 2)
            time = results_status[0]['time']
            if val_status < oke:
                status_id = 0
                status_text = "OK"
            elif val_status < warning:
                status_id = 1
                status_text = "Warning"
            else:
                status_id = 2
                status_text = "CRITICAL"
        except IndexError:
            val_status = 100
            time = str(datetime.datetime.now())
            status_id = 2
            status_text = "No data"
        return status_id, val_status, time, status_text

    def check_http_notify(self):
        status_codes = []
        data_status = self.client.query('select code from http '
                                        'where \"hostname\" = \'{}\' '
                                        'and \"group\" = \'{}\' '
                                        'and \"username\" = \'{}\' '
                                        'and time > now() -5m '
                                        .format(self.hostname, self.group, self.username))
        results_status = list(data_status.get_points(measurement='http'))
        # print(results_status)
        for res in results_status:
            status_codes.append(res["code"])
        try:
            mode_code = statistics.mode(status_codes)
            time = results_status[0]['time']
            if mode_code < 300:
                status_id = 0
                status_text = "OK"
            elif mode_code < 400:
                status_id = 1
                status_text = "Warning"
            else:
                status_id = 2
                status_text = "CRITICAL"
        except (statistics.StatisticsError, IndexError) as e:
            mode_code = None
            time = str(datetime.datetime.now())
            status_id = 2
            status_text = "No data"

        print(str(mode_code))
        return status_id, mode_code, time, status_text
