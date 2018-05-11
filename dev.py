from angler.helper import load_yaml_file

from main import main
import sync

if __name__ == '__main__':
    anglers = load_yaml_file('./harbor.yaml')['anglers']

    sync.sync_log_config(anglers)
    sync.sync_angler_config(anglers)
    sync.sync_other_config(anglers)
    sync.sync_resources(anglers)
    sync.sync_services(anglers)
    sync.sync_filters(anglers)

    main(
        config_file='./config/angler/config.yaml',
        project='cloud',
        matrix='a1A325fYEJX',
        angler_name='test'
    )
