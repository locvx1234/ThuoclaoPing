from pprint import pprint
from lib import utils

class Display(utils.Auth):
    def __init__(self, service_name, host, user):
        self.service_name = service_name
        self.host = host
        self.user = user
        # self.range_time = range_time
        self.client = self.auth()

    def select(self, iterval_time_query):
        # data = self.client.query('select * from fping where host=\'192.168.100.30\' and time > now() - 1m')
        data = self.client.query('select * from {}'
                     ' where \"host\" = \'{}\''
                     ' and \"user\" = \'{}\' and time > now() - {}m'
                     .format(self.service_name, self.host,
                             self.user, iterval_time_query), epoch='ms')
        # print(data)
        results = list(data.get_points(measurement='ping'))
        # results = list(data.get_points(measurement='{}'
        #                                .format(self.service_name)))
        # print(results)
        return results
    
    def check_ping_notify(self, oke, warning, critical):
        data_status = self.client.query('select mean("loss") from ping '
                                        'where \"host\" = \'{}\' '
                                        'and time > now() -5m '
                                        'and \"user\" = \'{}\''
                                        .format(self.host, self.user))
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
