from pprint import pprint
from lib import utils

class Display(utils.Auth):
    def __init__(self, service_name, IP, user, range_time):
        self.service_name = service_name
        self.ip = IP
        self.user = user
        self.range_time = range_time
        self.client = self.auth()

    def select(self):
        # data = self.client.query('select * from fping where host=\'192.168.100.30\' and time > now() - 1m')
        data = self.client.query('select * from {}'
                     ' where \"host\" = \'{}\''
                     ' and \"user\" = \'{}\' and time > now() - {}m'
                     .format(self.service_name, self.ip,
                             self.user, self.range_time), epoch='ms')
        # print(data)
        results = list(data.get_points(measurement='ping'))
        # results = list(data.get_points(measurement='{}'
        #                                .format(self.service_name)))
        # print(results)
        return results
    
     def check_notify(self, host, username, oke, warnning, critical):
        data_status = self.client.query('select mean("loss") from ping '
                                        'where \"host\" = \'{}\' '
                                        'and time > now() -5m '
                                        'and \"user\" = \'{}\''
                                        .format(host, username))
        results_status = list(data_status.get_points(measurement='ping'))
        val_status = results_status[0]['mean']
        time = results_status[0]['time']
        if val_status > oke and val_status < warnning:
            status_id = 0
        elif val_status <= warnning and val_status < critical:
            status_id = 1
        else:
            status_id = 2
        return time, status_id, host, username


# display = Display('ping', '8.8.8.8', 'minhkma', '1m')
# res = display.select()
# pprint(res)
