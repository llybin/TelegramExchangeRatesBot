import logging.config
import configparser

config_file = 'app/config.ini'

config = configparser.ConfigParser()
config_read_ok = config.read(config_file)

if len(config_read_ok) == 0:
    print('No config file.')
    exit()

logging.config.fileConfig(config_file)

__all__ = ("config", "logging")
