from lib import utils


class Display(utils.Auth):
    def __init__(self, group, hostname, username):
        # self.service_name = service_name
        self.hostname = hostname
        self.username = username
        self.group = group  # group_name
        self.client = self.auth()
    #
    # def select(self, iterval_time_query):
    #     # data = self.client.query('select * from fping where host=\'192.168.100.30\' and time > now() - 1m')
    #     data = self.client.query('select * from {}'
    #                              ' where \"host\" = \'{}\''
    #                              ' and \"user\" = \'{}\' and time > now() - {}m'
    #                              .format(self.service_name, self.host,
    #                                      self.user, iterval_time_query), epoch='ms')
    #     # print(data)
    #     results = list(data.get_points(measurement='ping'))
    #     # results = list(data.get_points(measurement='{}'
    #     #                                .format(self.service_name)))
    #     # print(results)
    #     return results

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
        return status_id, val_status, time, status_text


# display = Display('ping', '8.8.8.8', 'minhkma', '1m')
# res = display.select()
# pprint(res)
