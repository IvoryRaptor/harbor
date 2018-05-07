import os
from main import main


if __name__ == '__main__':
    main(
        config_file='./config/angler/config.yaml',
        project=os.environ['PROJECT'],
        matrix=os.environ['MATRIX'],
        angler_name=os.environ['ANGLER']
    )
