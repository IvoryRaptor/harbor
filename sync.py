import logging.config
import os
import configparser
import re
import shutil

import yaml
from angler.helper import load_yaml_file

logger = logging.getLogger('harbor')
logging.config.fileConfig("./logging.conf")


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info('create directory %s', path)
    else:
        logger.info('exist directory %s', path)


def copy_path(src, dst):
    if not os.path.exists(dst):
        shutil.copytree(src, dst)
        logger.info('copy directory %s', dst)
    else:
        logger.info('exist directory %s', dst)


def copy_file(src, dst, override=False):
    if not os.path.exists(dst) or override:
        shutil.copy(src, dst)
        logger.info('copy file %s', dst)
    else:
        logger.info('exist file %s', dst)


def sync_log_config(paths):
    create_path('./config/log')
    log_conf = configparser.RawConfigParser()
    keys = []
    for path in paths:
        filename = path + '/config/log/logging.conf'
        if os.path.exists(filename):
            config = configparser.RawConfigParser()
            config.read(filename, encoding='utf-8')
            keys = list(set(keys + config['loggers']['keys'].split(',')))
            for section in config.sections():
                if not log_conf.has_section(section):
                    log_conf.add_section(section)
                for item in config.items(section):
                    log_conf.set(section, item[0], item[1])
    if not log_conf.has_section('loggers'):
        log_conf.add_section('loggers')
    log_conf.set('loggers', 'keys', ','.join(keys))
    path = './config/log/logging.conf'
    log_conf.write(open(path, 'w'))
    logger.info('create file %s', path)


def dict_merge(obj, plus):
    for key in plus.keys():
        if isinstance(plus[key], dict):
            if obj.get(key) is None:
                obj[key] = {}
            dict_merge(obj[key], plus[key])
        else:
            obj[key] = plus[key]


def sync_angler_config(paths):
    if not os.path.exists('./config/angler/config.yaml'):
        create_path('./config/angler')
        result = {}
        for path in paths:
            config_path = '{0}/config/angler/config.yaml'.format(path)
            conf = load_yaml_file(config_path)
            dict_merge(result, conf)

        with open('./config/angler/config.yaml', 'w') as outfile:
            text = yaml.dump(result, default_flow_style=False)
            print(text)
            outfile.write(text)


def sync_other_config(paths):
    for path in paths:
        config_path = '{0}/config/'.format(path)
        if os.path.exists(config_path):
            for sub in os.listdir(config_path):
                if sub not in ['log', 'angler'] and sub[0] != '.':
                    sub_path = config_path + sub
                    copy_path(sub_path, './config/' + sub)


def sync_resources(paths):
    for path in paths:
        angler_name = path[path.rfind('/')+1:]
        if re.match('^[a-z|_]+$', angler_name):
            project_resources_path = './resources/{0}/'.format(angler_name)
            create_path(project_resources_path)
            resources_path = '{0}/resources/'.format(path)
            for py_file in os.listdir(resources_path):
                if re.match('^[a-z|_]+.py$', py_file):
                    copy_file(resources_path + py_file, project_resources_path + py_file, True)


def sync_services(paths):
    create_path('./services')
    for path in paths:
        filters_path = '{0}/services/'.format(path)
        if os.path.exists(filters_path):
            for py_file in os.listdir(filters_path):

                if re.match('^[a-z|_]+.py$', py_file) and py_file != '__init__.py':
                    copy_file(filters_path + py_file, 'services/' + py_file, True)


def sync_filters(paths):
    create_path('./filters')
    for path in paths:
        filters_path = '{0}/filters/'.format(path)
        if os.path.exists(filters_path):
            for py_file in os.listdir(filters_path):
                if re.match('^[a-z|_]+.py$', py_file) and py_file != '__init__.py':
                    copy_file(filters_path + py_file, 'filters/' + py_file, True)


# def sync_angler(paths):
#     for path in paths:
#         angler_name = path[path.rfind('/')+1:]
#         if re.match('^[a-z|_]+$', angler_name):
#             project_resources_path = 'resources/{0}/'.format(angler_name)
#             if not os.path.exists(project_resources_path):
#                 os.mkdir(project_resources_path)
#             resources_path = '{0}/resources/'.format(path)
#             for py_file in os.listdir(resources_path):
#                 if re.match('^[a-z|_]+.py$', py_file):
#                     shutil.copyfile(resources_path + py_file, project_resources_path + py_file)
#
#             services_path = '{0}/services/'.format(path)
#             if os.path.exists(services_path):
#                 for py_file in os.listdir(services_path):
#                     if re.match('^[a-z|_]+.py$', py_file) and py_file != '__init__.py':
#                         shutil.copyfile(services_path + py_file, 'services/' + py_file)
#
#             filters_path = '{0}/filters/'.format(path)
#             if os.path.exists(filters_path):
#                 for py_file in os.listdir(filters_path):
#                     if re.match('^[a-z|_]+.py$', py_file) and py_file != '__init__.py':
#                         shutil.copyfile(filters_path + py_file, 'filters/' + py_file)
#
#             filters_path = '{0}/config/'.format(path)
#             if os.path.exists(filters_path):
#                 for py_file in os.listdir(filters_path):
#                     if re.match('^[a-z|_]+.py$', py_file) and py_file != '__init__.py':
#                         shutil.copyfile(filters_path + py_file, 'filters/' + py_file)

if __name__ == '__main__':
    anglers = load_yaml_file('./harbor.yaml')['anglers']
    sync_log_config(anglers)
    sync_angler_config(anglers)
    sync_other_config(anglers)
    sync_resources(anglers)
    sync_services(anglers)
    sync_filters(anglers)

    #
    #
    # for angler in conf['anglers']:
    #     conf_file = angler + '/config/log/logging.conf'
    #     if os.path.exists(conf_file):
    #         config = configparser.ConfigParser()
    #         config.read(conf_file)
    # #
    # log_conf.write('./config/log/logging.conf')

    # print(config['loggers']['keys'])
    # print(config.sections())
    # logging.config.fileConfig("./config/log/logging.conf")  # 采用配置文件
    #
    # # create logger
    # logger = logging.getLogger('angler')
    #
    # # "application" code
    # logger.debug("debug message")
    # logger.info("info message")
    # logger.warn("warn message")
    # logger.error("error message")
    # logger.critical("critical message")
    #
    # log2 = logging.getLogger('angler.mongo')
    # log2.info('info')

    # logger.setLevel(logging.INFO)
    # logger.addHandler(logging.StreamHandler(sys.stdout))

    # logger.setLevel(logging.DEBUG)
    # logging.info('123456')
    # paths = ['./config', './resources', './services']

    # for path in paths:
    #     logger.info('clear {0}'.format(path))
    #     shutil.rmtree(path)
    #     os.mkdir(path)


