import os
import json
from utils import clear_dir, git, flatten
from generate import generate_html
from save_cmd import SaveCommand

class PublishCommand:
    def __init__(self):
        print('---> generating blog to www/ directory')
        clear_dir('www')
        config = json.load(open('config.json', 'r'))
        generate_html(config, 'www')
        print('---> done')

        SaveCommand()

        print('---> pushing contents of www/ to master')
        git(['checkout', 'master'])
        clear_dir(os.getcwd())
        git(['checkout', 'dev', '--', 'www'])
        flatten('www')
        git(['add', '.'])
        git(['commit', '-m', '"blogctl deploy"'])
        git(['push', 'origin', 'master'])
        git(['checkout', 'dev'])
        print('---> done')
