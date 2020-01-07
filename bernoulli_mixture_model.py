'''
Inspired by https://github.com/rdorado/bernoulli-mixture-model
'''
import numpy as np

from datetime import datetime

TIME_ANALYSIS = False


class BernoulliMixtureModel:
    def __init__(self):
        self.data = None
        self.N = None
        self.D = None
        self.K = None
        self.z = None
        self.pi = None
        self.mu = None

    def _probability(self, data, k):
        cluster_prob = 1
        for i in data:
            cluster_prob *= self.mu[k][i]
        return cluster_prob * self.pi[k]

    def _predict_probability(self, data):
        total_prob = 0
        for k in range(self.K):
            cluster_prob = 1
            for i in data:
                cluster_prob *= self.mu[k][i]
            total_prob += cluster_prob * self.pi[k]
        return total_prob

    def fit(self, data, clusters):
        if TIME_ANALYSIS:
            print('Starting building time: {0}'.format(str(datetime.now())))

        self.data = data
        self.N = len(data)
        self.D = max([v for l in self.data for v in l]) + 1
        self.K = clusters
        self.z = np.zeros((self.N, self.K))
        self.z.fill(1.0 / self.K)
        self.pi = np.zeros([self.K])
        self.pi.fill(1.0 / self.K)
        self.mu = np.random.random([self.K, self.D])

        niter = 0

        change = True
        while change:
            change = False
            for n in range(self.N):
                sumz = 0
                for k in range(self.K):
                    self.z[n][k] = self._probability(self.data[n], k)
                    sumz += self.z[n][k]
                for k in range(self.K):
                    self.z[n][k] /= sumz

            if TIME_ANALYSIS:
                print('Finished expectation step at {0}'.format(str(datetime.now())))

            N_m = np.zeros([self.K])
            z_x = np.zeros([self.K, self.D])
            newpi = np.zeros([self.K])
            newpi.fill(1.0 / self.K)
            newmu = np.zeros([self.K, self.D])
            newmu.fill(1.0 / self.D)
            for k in range(self.K):
                for n in range(self.N):
                    N_m[k] += self.z[n][k]
                    for d in data[n]:
                        # if d in data[n]:
                        z_x[k][d] += self.z[n][k] * 1
                for d in range(self.D):
                    newmu[k][d] = z_x[k][d]/N_m[k]
                newpi[k] = N_m[k]/self.N

            for k in range(self.K):
                if round(self.pi[k], 3) != round(newpi[k], 3):
                    change = True
                    self.pi[k] = newpi[k]
                for d in range(self.D):
                    if round(self.mu[k][d], 3) != round(newmu[k][d], 3):
                        change = True
                        self.mu[k][d] = newmu[k][d]

            if TIME_ANALYSIS:
                print('Finished maximization step at {0}'.format(str(datetime.now())))

            niter += 1
            if niter % 1000 == 0:
                print('Finished with {0} iterations. Still going...'.format(niter))
        print('Finished in {0} iterations'.format(niter))

    def print_model(self):
        for i in range(self.K):
            print('Mu: {0}'.format(np.round(self.mu[i], 2)))
            print('Pi: {0}'.format(np.round(self.pi[i], 2)))

    def predict(self, x):
        return np.prod(self._predict_probability(x))


if __name__ == '__main__':
    sample_data = [
        [0, 1, 2, 3, 4],
        [2, 3],
        [0, 3, 4],
        [2, 3, 6],
        [3, 4],
        [2, 3, 4, 5, 6],
        [0, 1, 2, 3, 4],
        [2, 3, 4, 5, 6],
        [3, 4, 5, 6, 7],
        [6, 7, 8, 9, 10]
    ]

    bmm = BernoulliMixtureModel()
    for i in range(1, 10):
        bmm.fit(sample_data, i)
        bmm.print_model()

        sample_test = [[1, 2], [2, 4]]

    print('Predicting with {0} Clusters...'.format(i))
    print(bmm.predict(sample_test))
