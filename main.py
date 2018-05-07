import logging
import time
import sys
import yaml
from angler.angler import Angler
from angler.helper import load_file


def set_config(filename, project, matrix, angler_name):
    config = yaml.load(load_file(filename))
    config['matrix'] = matrix
    config['angler'] = angler_name
    config['services']['mongo']['database'] = project
    config['source']['query'] = '{0}_{1}'.format(matrix, angler_name)
    config['source']['group'] = angler_name

    config['services']['registry']['url'] = load_file('./registry/registry').replace('\n', '')
    file = open(filename, 'w', encoding='utf8')
    text = yaml.dump(config, default_flow_style=False)
    file.write(text)
    file.close()


def main(config_file, project, matrix, angler_name):
    set_config(config_file, project, matrix, angler_name)
    logger = logging.getLogger('kafka')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    angler = Angler()
    conf = yaml.load(load_file(config_file))
    angler.config(conf)
    angler.start()
    logging.info('start')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    angler.stop()
