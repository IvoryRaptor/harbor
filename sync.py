import logging.config
import os
import configparser
import re
import shutil
import yaml
from angler import helper

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


def sync_angler_config(paths, override=False):
    if not os.path.exists('./config/angler/config.yaml') or override:
        create_path('./config/angler')
        result = {}
        for path in paths:
            config_path = '{0}/config/angler/config.yaml'.format(path)
            conf = helper.load_yaml_file(config_path)
            dict_merge(result, conf)

        with open('./config/angler/config.yaml', 'w') as outfile:
            text = yaml.dump(result, default_flow_style=False)
            outfile.write(text)
            logger.info('create file %s', './config/angler/config.yaml')


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
                if re.match('^[a-z|_]+.py$', py_file) and py_file != '__init__.py':
                    copy_file(resources_path + py_file, project_resources_path + py_file, True)


def sync_services(paths):
    create_path('./services')
    imports = {}
    froms = {}
    voluations = {}
    codes = {}

    for path in paths:
        filters_path = '{0}/services/'.format(path)
        if os.path.exists(filters_path):
            for py_file in os.listdir(filters_path):
                if py_file == '__init__.py':
                    lines = helper.load_strings_file(filters_path + '__init__.py')
                    for line in lines:
                        data = re.search('from (.+) import (.+)', line)
                        if data is not None:
                            l = froms.get(data.group(1))
                            if l is None:
                                l = {}
                                froms[data.group(1)] = l
                            for item in data.group(2).split(','):
                                if l.get(item) is None:
                                    l[item] = ''
                            continue
                        data = re.search('import (.+)', line)
                        if data is not None:
                            imports[data.group(1)] = ''
                            continue
                        data = re.search('(.+) = (.+)', line)
                        if data is not None:
                            voluations[data.group(1)] = data.group(2)
                            continue
                        codes[line] = ''
                elif re.match('^[a-z|_]+.py$', py_file):
                    copy_file(filters_path + py_file, 'services/' + py_file, True)
    file = open('./services/__init__.py', 'w', encoding='utf8')
    for item in imports.keys():
        file.write('import {0}\n'.format(item))
    for item in froms.keys():
        file.write('from {0} import {1}\n'.format(item, ','.join(froms[item].keys())))
    file.write('\n\n')
    for item in voluations.keys():
        file.write('{0} = {1}\n'.format(item, voluations[item]))
    for item in codes.keys():
        file.write('{0}\n'.format(item))
    file.close()
    logger.info('create services/__init__.py')


def sync_filters(paths):
    create_path('./filters')
    for path in paths:
        filters_path = '{0}/filters/'.format(path)
        if os.path.exists(filters_path):
            for py_file in os.listdir(filters_path):
                if re.match('^[a-z|_]+.py$', py_file) and py_file != '__init__.py':
                    copy_file(filters_path + py_file, 'filters/' + py_file, True)


if __name__ == '__main__':
    anglers = helper.load_yaml_file('./harbor.yaml')['anglers']
    sync_log_config(anglers)
    sync_angler_config(anglers, True)
    sync_other_config(anglers)
    sync_resources(anglers)
    sync_services(anglers)
    sync_filters(anglers)
