import configparser


class Base(object):
    def get_conf(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config
