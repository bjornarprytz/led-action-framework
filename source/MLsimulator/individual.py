#!/usr/bin/env python2.7

import numpy as np
import random as rand
import math
LED_RESOLUTION = 256
INFINITY = 9999999999

red_channel_wattage = 3.4
white_channel_wattage = 6.0
blue_channel_wattage = 1.0

class Individual:
    """
    An Individual with a set of three weights (a, b, c) as the genotype.
    """
    def __init__(self, w, r, b, energy_allowance, allowance_tolerance=0.0001, weights={'a' : 1.0, 'b' : 1.0, 'c' : 1.0}):
        # w, r and b are arrays representing the documented
        # maximum output profiles for each channel.
        self.w = w
        self.r = r
        self.b = b

        self.weights = weights.copy()
        self.reward = 0
        self.resolution = LED_RESOLUTION

        self.energy_allowance = energy_allowance
        self.allowance_tolerance = allowance_tolerance

        self._temperature = 1.0     # higher temperature -> more exploration. Diminishes each iteration.
        self._min_temp = 0.00001    # When to stop annealing
        self._alpha = 0.90          # Change in temperature between each iteration

    def energy_consumption(self, weights):
        """
            The Petunia LED units have 5 red LEDs, 6 white LEDs and 1 blue LED, so
            the energy consumption estimate should reflect that.

            At 500 mA, the estimate in watts is:
                    (normalized)
            R: 5.25  (3.4)
            W: 9.3   (6)
            B: 1,55  (1)
        """

        return (weights['a'] * red_channel_wattage) +(weights['b'] * white_channel_wattage) + (weights['c'] * blue_channel_wattage)

    def quantum_yield(self, action_spectrum):
        """
            Simulate plant utilization of the output radiance based on the model action spectrum

            The best possible quantum_yield would be if the action spectrum were flat 1.0. Then
            all radiance would be efficiently turned into product
        """

        spectral_QY = action_spectrum * self.get_PAR_output()


        # print spectral_QY

        quantum_yield = np.mean(spectral_QY)

        # print quantum_yield
        # exit()

        return quantum_yield

    def reward_func(self, action_spectrum):
        """
            --Reward Function--
            Evaluate the input PAR values and return the reward

            action_spectrum and self.get_PAR_output() are arrays of equal size,
            representing the LED output and the action spectrum of the plant
            across a range of wavelengths.
        """

        quantum_yield = self.quantum_yield(action_spectrum)

        # print quantum_yield

        reward = quantum_yield #/ energy

        # print reward
        #
        # exit()

        return reward


    def random_start(self):
        for key in self.weights.keys():
            rand.seed()
            self.weights[key] = float(rand.randint(0,LED_RESOLUTION)) / float(LED_RESOLUTION)


    def get_reward(self):
        return self.reward

    def get_PAR_output(self):
        '''
            Calculate the PAR output from the LED array according to the current
            settings on each channel.
        '''
        a = self.weights['a']
        b = self.weights['b']
        c = self.weights['c']

        return (self.r * a) + (self.w * b) + (self.b * c)

    def print_stats(self):
        print (self.w, self.r, self.b, self.reward)

    def leftover_energy(self, weights):
        consumption = self.energy_consumption(weights)

        return self.energy_allowance - consumption

    def adjust_channels(self, weights, adjustable_channels):
        '''
            Adjust one (or more) of the adjustable channels until the
            energy allowance is spent
        '''
        rand.shuffle(adjustable_channels)
        # print adjustable_channels
        for channel in adjustable_channels:
            budget = self.leftover_energy(weights)
            print budget
            if budget > self.allowance_tolerance:
                if channel == 'a':
                    weights[channel] += budget / red_channel_wattage
                if channel == 'b':
                    weights[channel] += budget / white_channel_wattage
                if channel == 'c':
                    weights[channel] += budget / blue_channel_wattage

                print weights[channel]
                if weights[channel] > 1.0:
                    weights[channel] = 1.0



    def neighbour(self, channel=None):
        '''
            Generate a random neighbour by changing the weight of one channel.
            If channel is None, randomize the choice of channel.
        '''


        new_weights = self.weights.copy()

        available_channels = adjustable_channels = self.weights.keys()


        if channel == None:
            channel = rand.choice(available_channels)

        while new_weights[channel] == 0.0:
            if channel in available_channels:
                available_channels.remove(channel)
            if len(available_channels) == 0:
                print "all channels are zero, please reinitialize weights before trying this again"
                return
            channel = rand.choice(available_channels)

        if channel in adjustable_channels:
            adjustable_channels.remove(channel)

        new_weights[channel] = rand.uniform(0.0, new_weights[channel]) # Randomize the weight to a lower number

        print new_weights

        self.adjust_channels(new_weights, adjustable_channels)

        new_individual = Individual(self.w, self.r, self.b, new_weights)

        return new_individual

    def acceptance_probability(self, old_reward, new_reward):
        try:
            ap = math.exp((new_reward - old_reward) / self._temperature)
        except OverflowError:
            ap = 1
        if ap > 1:
            ap = 1

        return ap

    def anneal(self, action_spectrum, iterations=-1):
        '''
            Based on http://katrinaeg.com/simulated-annealing.html

            Simulated annealing for an input number of iterations. If
            iterations is -1, it will run until temperature reaches min_temp
        '''
        old_reward = self.reward_func(action_spectrum)

        best_setting = self

        tries_per_temp = 10

        n_iter = 0

        while self._temperature > self._min_temp:
            if iterations == 0:
                break
            for i in range(tries_per_temp):
                new_setting = best_setting.neighbour() # Generate a random neighbour
                new_reward = new_setting.reward_func(action_spectrum) # Evaluate the new solution
                ap = self.acceptance_probability(old_reward, new_reward)

                if ap > rand.random():
                    best_setting = new_setting
                    old_reward = new_reward

            self._temperature *= self._alpha
            if iterations > 0:
                iterations-=1

            n_iter += 1


        return best_setting, n_iter

    def probe(self, channel, step, action_spectrum):
        weights = self.weights.copy()

        weights[channel] += step
        if (weights[channel] > 1):
            weights[channel] = 1.0

        up = Individual(self.w, self.r, self.b, weights)
        reward_up = up.reward_func(action_spectrum)

        weights[channel] -= (step*2)
        if (weights[channel] < 0):
            weights[channel] = 0.0
        down = Individual(self.w, self.r, self.b, weights)
        reward_down = down.reward_func(action_spectrum)

        # higher reward is better
        if reward_up > reward_down:
            return up
        else:
            return down

    def adjust_search_resolution(self, delta, low_limit=1, hi_limit=10000):
        res = self.resolution + delta

        # Clamp within limits
        if low_limit < res:
            res = low_limit
        if res < hi_limit:
            res = hi_limit

        self.resolution = res


    def hill_climb(self, action_spectrum, step=0.0):
        """
        Try changing the weights a, b and c one by one, in both directions, and evaluate them to see which
        neighbour is the most promising.
        """

        best_individual = self
        highest_reward = self.reward
        if step == 0.0:
            step = float(1.0 / self.resolution)

        new_best = False

        for key in self.weights.keys():
             individual = self.probe(key, step, action_spectrum)
             reward = individual.reward_func(action_spectrum)
             if reward > highest_reward:
                 new_best = True
                 highest_reward = reward
                 best_individual = individual

        if new_best:
            for key in self.weights.keys():
                self.weights[key] = best_individual.weights[key]

        new_reward = self.reward_func(action_spectrum)

        delta = new_reward - self.reward
        self.reward = new_reward
        return delta

    def hc_get_iterations(self, action_spectrum, tolerance, step=0.0):
        delta = 100.0
        iterations = 0
        while delta>tolerance:
            delta = self.hill_climb(action_spectrum, step)
            iterations += 1

        return iterations

import quantum_yield

if __name__ == "__main__":
    w = quantum_yield.wht_LED
    b = quantum_yield.blu_LED
    r = quantum_yield.red_LED
    energy_allowance = 3.0
    I = Individual(w, r, b, energy_allowance, weights={'a' : 0.01, 'b' : 0.01, 'c' : 0.01})

    print I.energy_consumption(I.weights)


    print I.neighbour().weights
