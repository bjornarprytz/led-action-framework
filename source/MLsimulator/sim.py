#!/usr/bin/env python2.7

import matplotlib.pyplot as plt
import numpy as np
import random as rand
import math
import time
from quantum_yield import *

LED_RESOLUTION = 10
INFINITY = 9999999999


# TODO: Dynamic Plotting seems to work, so fix actual learning.
# Goal: Learn Faster. Take Bigger risks

class Individual:
    """
    An Individual with a set of three weights (a, b, c) as the genotype.
    """
    def __init__(self, w, r, b, weights={'a' : 1.0, 'b' : 1.0, 'c' : 1.0}):
        # w, r and b are arrays representing the documented
        # maximum output profiles for each channel.
        self.w = w
        self.r = r
        self.b = b

        self.weights = weights.copy()

        self.cost = INFINITY

        self.resolution = LED_RESOLUTION

        self._temperature = 1.0     # higher temperature -> more exploration. Diminishes each iteration.
        self._min_temp = 0.00001    # When to stop annealing
        self._alpha = 0.90          # Change in temperature between each iteration

    def cost_func(self, action_spectrum):
        """
            --Cost Function--
            Evaluate the input PAR values and return the cost (lower is better)

            action_spectrum are arrays of equal size, representing the LED output
            and the action spectrum of the plant across a range of wavelengths.
        """

        # TODO: Take energy consumption into account

        diff = action_spectrum - self.get_PAR_output()

        cost = np.sum(np.sqrt(diff**2))

        return cost


    def random_start(self):
        for key in self.weights.keys():
            rand.seed()
            self.weights[key] = float(rand.randint(0,LED_RESOLUTION)) / float(LED_RESOLUTION)


    def get_cost(self):
        return self.cost

    def get_PAR_output(self):
        '''
            Calculate the PAR output from the LED array according to the current
            settings on each channel.
        '''
        a = self.weights['a']
        b = self.weights['b']
        c = self.weights['c']

        return (self.w * a) + (self.r * b) + (self.b * c)

    def print_stats(self):
        print (self.w, self.r, self.b, self.cost)

    def neighbour(self, channel=None):
        '''
            Generate a random neighbour by changing the weight of one channel.
            If channel is None, randomize the choice of channel.
        '''

        if channel == None:
            channel = rand.choice(self.weights.keys())

        new_weights = self.weights.copy()

        new_weights[channel] = rand.random() # Randomize the weight [0-1]

        new_individual = Individual(self.w, self.r, self.b, new_weights)

        return new_individual

    def acceptance_probability(self, old_cost, new_cost):
        ap = math.exp((old_cost - new_cost) / self._temperature)

        return ap

    def anneal(self, action_spectrum):
        '''
            Based on http://katrinaeg.com/simulated-annealing.html

            Simulated annealing for an input number of iterations. If
            iterations is 0, it will run until temperature reaches min_temp
        '''
        old_cost = self.cost_func(action_spectrum)

        best_setting = self

        tries_per_temp = 10

        while self._temperature > self._min_temp:
            for i in range(tries_per_temp):
                new_setting = best_setting.neighbour() # Generate a random neighbour
                new_cost = new_setting.cost_func(action_spectrum) # Evaluate the new solution
                ap = self.acceptance_probability(old_cost, new_cost)

                if ap > rand.random():
                    best_setting = new_setting
                    old_cost = new_cost

            self._temperature *= self._alpha

        return best_setting

    def probe(self, channel, step, action_spectrum):
        weights = self.weights.copy()

        weights[channel] += step
        if (weights[channel] > 1):
            weights[channel] = 1.0

        up = Individual(self.w, self.r, self.b, weights)
        cost_up = up.cost_func(action_spectrum)

        weights[channel] -= (step*2)
        if (weights[channel] < 0):
            weights[channel] = 0.0
        down = Individual(self.w, self.r, self.b, weights)
        cost_down = down.cost_func(action_spectrum)

        # lower cost is better
        if cost_up < cost_down:
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


    def local_search(self, action_spectrum):
        """
        Try changing the weights a, b and c one by one, in both directions, and evaluate them to see which
        neighbour is the most promising.
        """

        best_individual = self
        lowest_cost = self.cost
        step = float(1.0 / self.resolution)

        new_best = False

        for key in self.weights.keys():
             individual = self.probe(key, step, action_spectrum)
             cost = individual.cost_func(action_spectrum)
             if cost < lowest_cost:
                 new_best = True
                 lowest_cost = cost
                 best_individual = individual

        if new_best:
            for key in self.weights.keys():
                self.weights[key] = best_individual.weights[key]
        else:
            self.adjust_search_resolution(10)



        self.cost = self.cost_func(action_spectrum)


if __name__ == "__main__":
    rand.seed()
    w = np.array(wht_LED)
    r = np.array(red_LED)
    b = np.array(blu_LED)
    pr = np.array(plt_PAR)

    plt.ion()

    # plt.plot(w, color="yellow")
    # plt.plot(r, color="red")
    # plt.plot(b, color="blue")
    # plt.plot(pr, color="green")


    test = Individual(w, r, b)
    test.random_start()

    test2 = Individual(w, r, b)
    test2.random_start()

    # plt.pause(0.05)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    white_range = ax.plot(spectrum_range, w, '-k', color='yellow', label='White LED')
    red_range = ax.plot(spectrum_range, r, color='red', label='Red LED')
    blue_range = ax.plot(spectrum_range, b, color='blue', label='Blue LED')
    plant_profile = ax.plot(spectrum_range, pr, color='green', label='Plant PAR-profile')
    LED_response, = ax.plot([], [], '-k', color='black', label='LED output')
    LED_response2, = ax.plot([], [], '-k', color='grey', label='LED output2')
    Annealing_result, = ax.plot([], [], '-k', color='pink', label='Annealing')
    ax.legend()

    for i in range(100):
        # time.sleep(0.25)
        test.local_search(pr)
        LED_response.set_ydata(test.get_PAR_output())
        LED_response.set_xdata(spectrum_range)

        test2.local_search(pr)
        LED_response2.set_ydata(test2.get_PAR_output())
        LED_response2.set_xdata(spectrum_range)

        ax.relim()
        ax.axis([spectrum_range[0], spectrum_range[-1], 0, 2])
        plt.draw()

    anneal_test = Individual(w,r,b)
    an_res = anneal_test.anneal(pr)

    Annealing_result.set_ydata(an_res.get_PAR_output())
    Annealing_result.set_xdata(spectrum_range)

    ax.relim()
    ax.axis([spectrum_range[0], spectrum_range[-1], 0, 2])

    print an_res.cost_func(pr)
    print test.cost_func(pr)

    while True:
        plt.draw()



    plt.show()
