import sys

class Forward:
        def __init__(self, model, emission_sequence):

            self.transition_matrix = model[0]
            self.initial_matrix = model[2]
            self.emission_matrix = model[1]
            self.emission_sequence = emission_sequence

        def compute_alpha0(self):
            obs_0 = self.emission_sequence[0]
            alpha0 = [0.0] * len(self.initial_matrix)
            for i in range(len(alpha0)):
                alpha0[i] = self.initial_matrix[i] * self.emission_matrix[i][obs_0]

            return alpha0

        def compute_intermediate_sum(self, i, alpha):
            sum = 0
            for j in range(len(alpha)):
                sum += alpha[j] * self.transition_matrix[j][i]
            return sum

        def compute_alphas(self, prev_alpha):
            new_alpha = [0.0] * len(prev_alpha)
            num_obs = len(self.emission_sequence)
            for t in range(1, num_obs):
                for i in range(len(prev_alpha)):
                    intermediate_sum = self.compute_intermediate_sum(i, prev_alpha)
                    new_alpha[i] = intermediate_sum * self.emission_matrix[i][self.emission_sequence[t]]
                prev_alpha = new_alpha
                new_alpha = [0.0] * len(prev_alpha)
            return sum(prev_alpha)

        def compute_prob(self):
            alpha0 = self.compute_alpha0()
            prob = self.compute_alphas(alpha0)
            #print(prob)

            return prob


