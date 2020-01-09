from sklearn.model_selection import train_test_split

from data_processing import GithubRequests, build_html_content
from bernoulli_mixture_model import BernoulliMixtureModel
from file_manager import MODEL_FILE, LOGIN_LOOKUP

import pickle

build_model = False
save_model = True
train_model = True


def build_network():
    # Authenticate and pull data
    GitHub = GithubRequests()
    GitHub.authenticate()
    repos_json = GitHub.get_org_repos()
    repo_list = GitHub.org_repo_list(repos_json)
    created_dict = GitHub.created_prs(repo_list)

    # Build social network
    comments_dict = GitHub.comments_on_prs(created_dict)
    network_connections = GitHub.build_network(created_dict, comments_dict)
    build_html_content(network_connections)

    # Build Bernoulli Mixture Model data
    if build_model:
        group_data, login_lookup = GitHub.build_groups(created_dict, comments_dict)

        # Train model
        bmm_train = BernoulliMixtureModel()

        if train_model:
            train_data, test_data = train_test_split(group_data, test_size=0.33)
            bmm_train.fit(train_data, 100)
            for group in test_data:
                try:
                    prediction = bmm_train.predict(group)
                    print(prediction)
                except IndexError:
                    pass

        # Fit final model
        bmm = BernoulliMixtureModel()
        bmm.fit(group_data, 100)

        # Save Model
        if save_model:
            with open(MODEL_FILE, 'wb') as model:
                pickle.dump(bmm, model)
            with open(LOGIN_LOOKUP, 'wb') as lookup:
                pickle.dump(login_lookup, lookup)


if __name__ == "__main__":
    build_network()
