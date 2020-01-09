import os

GITHUB_USERNAME = os.environ['GITHUB_USERNAME']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
ORGANIZATION = os.environ['GITHUB_ORGANIZATION']

NETWORK_TEXT = 'network_temp.html'
NETWORK_HTML = 'index.html'

PAGE_LENGTH = '?per_page=1000'

BASE_URL = 'https://api.github.com'
REPOS_EXT = BASE_URL + '/orgs/{}/repos' + PAGE_LENGTH
PULLS_ISSUES_EXT = BASE_URL + '/repos/{}/{}/{}'
PULL_ISSUE_COMMENT_EXT = PULLS_ISSUES_EXT + '/{}/comments'

MODEL_FILE = 'model.pickle'
LOGIN_LOOKUP = 'login_lookup.pickle'
