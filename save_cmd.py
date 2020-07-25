from utils import git

class SaveCommand:
    def __init__(self):
        print('---> saving to github')
        git(['pull', '--allow-unrelated-history', 'origin', 'master'])
        git(['add', '.'])
        git(['commit', '-m', 'blogctl save'])
        git(['push', 'origin', 'master'])
        print('---> done')
