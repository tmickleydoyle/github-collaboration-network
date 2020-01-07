from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from collections import defaultdict
from itertools import chain

from file_manager import (
    PULLS_ISSUES_EXT, PULL_ISSUE_COMMENT_EXT,
    ORGANIZATION, GITHUB_USERNAME, GITHUB_TOKEN, REPOS_EXT,
    NETWORK_TEXT, NETWORK_HTML
)

import requests
import json
import fileinput


def build_html_content(json_data):
    output_file = open(NETWORK_HTML, 'w')
    for line in fileinput.FileInput(NETWORK_TEXT, inplace=False):
        if 'json_data_input' in line:
            line = line.replace('json_data_input', json.dumps(json_data, indent=4, sort_keys=True))
        output_file.write(line)
    output_file.close()


class GithubRequests:
    def __init__(self):
        self.github_session = None
        self.username = GITHUB_USERNAME
        self.token = GITHUB_TOKEN

    def authenticate(self):
        self.github_session = requests.Session()
        self.github_session.auth = (self.username, self.token)
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.github_session.mount('https://', adapter)
        return self.github_session

    def requests_to_json(self, request_url):
        request_data = self.github_session.get(request_url)
        return json.loads(request_data.text)

    def get_org_repos(self):
        org_repos_url = REPOS_EXT.format(ORGANIZATION)
        return self.requests_to_json(org_repos_url)

    def org_repo_list(self, repos_json):
        repos_list = []
        for repo in repos_json:
            repos_list.append(repo['name'])
        return repos_list

    def created_prs(self, repo_list, request_url=PULLS_ISSUES_EXT, org=ORGANIZATION):
        created_dict = defaultdict(dict)
        for repo in repo_list:
            for comment_type in ['pulls', 'issues']:
                issues = self.requests_to_json(request_url.format(org, repo, comment_type))
                for issue in issues:
                    created_dict[repo][issue['number']] = {
                        'comment_type': comment_type,
                        'login': issue['user']['login']
                    }
        return created_dict

    def comments_on_prs(self, created_dict, requests_url=PULL_ISSUE_COMMENT_EXT, org=ORGANIZATION):
        comment_dict = defaultdict(dict)
        for repo, pr_data in created_dict.items():
            for number, pr_user in pr_data.items():
                request_data = self.requests_to_json(
                    requests_url.format(org, repo, pr_user['comment_type'], number)
                )
                for comment in request_data:
                    try:
                        comment_dict[repo][number].append(comment['user']['login'])
                    except KeyError:
                        comment_dict[repo][number] = [comment['user']['login']]
        return comment_dict

    def build_network(self, author_dict, commenter_dict):
        network_list = []
        id_list = []
        for repo, repo_data in author_dict.items():
            for number, number_data in repo_data.items():
                try:
                    comment_list = commenter_dict[repo][number]
                    for commenter in comment_list:
                        if number_data['login'] != commenter:
                            network_list.append(
                                {'source': str(number_data['login']), 'target': str(commenter)}
                            )
                            id_list.append(number_data['login'])
                            id_list.append(commenter)
                except KeyError:
                    pass
        try:
            id_list = list(set(id_list))
            id_list = [{'id': u_id} for u_id in id_list]
        except KeyError:
            pass

        return {'links': network_list, 'nodes': id_list}

    def build_groups(self, author_dict, commenter_dict):
        network_group = []
        for repo, repo_data in author_dict.items():
            for number, number_data in repo_data.items():
                try:
                    group_list = []
                    comment_list = commenter_dict[repo][number]
                    for commenter in comment_list:
                        if number_data['login'] != commenter:
                            group_list.append(number_data['login'])
                            group_list.append(commenter)
                    network_group.append(list(set(group_list)))
                except KeyError:
                    pass

        try:
            temp_groups = []
            login_dict = self._convert_logins(network_group)

            for group in network_group:
                temp_list = []
                for login in group:
                    temp_list.append(login_dict[login])
                temp_groups.append(temp_list)
            temp_groups = [x for x in temp_groups if x]
            network_group = temp_groups

        except KeyError:
            pass

        return network_group, login_dict

    def _convert_logins(self, network_group):
        login_dict = {}
        network_group = list(set(list(chain(*network_group))))
        for num, login in enumerate(network_group):
            login_dict[login] = num
        return login_dict
