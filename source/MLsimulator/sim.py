#!/usr/bin/env python2.7

import matplotlib.pyplot as plt
import numpy as np
import random as rand
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
        self.w = w
        self.r = r
        self.b = b

        self.weights = weights.copy()

        self.fitness = INFINITY

        self.resolution = LED_RESOLUTION

    def random_start(self):
        for key in self.weights.keys():
            rand.seed()
            self.weights[key] = float(rand.randint(0,LED_RESOLUTION)) / float(LED_RESOLUTION)


    def get_fitness(self):
        return self.fitness

    def get_PAR_output(self, a=-1, b=-1, c=-1):
        if a == -1:
            a = self.weights['a']
        if b == -1:
            b = self.weights['b']
        if c == -1:
            c = self.weights['c']

        return (self.w * a) + (self.r * b) + (self.b * c)

    def print_stats(self):
        print (self.w, self.r, self.b, self.fitness)

    def probe(self, key, step, plant_response):
        weights = self.weights.copy()

        weights[key] += step
        if (weights[key] > 1):
            weights[key] = 1.0

        up = Individual(self.w, self.r, self.b, weights)
        fitness_up = up.eval(up.get_PAR_output(), plant_response)

        weights[key] -= (step*2)
        if (weights[key] < 0):
            weights[key] = 0.0
        down = Individual(self.w, self.r, self.b, weights)
        fitness_down = down.eval(down.get_PAR_output(), plant_response)

        # lower fitness is better
        if fitness_up < fitness_down:
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


    def local_search(self, plant_response):
        """
        Try changing the weights a, b and c one by one, in both directions, and evaluate them to see which
        neighbour is the most promising.
        """

        best_individual = self
        best_fitness = self.fitness
        step = float(1.0 / self.resolution)

        new_best = False

        for key in self.weights.keys():
             individual = self.probe(key, step, plant_response)
             fitness = individual.eval(individual.get_PAR_output(), plant_response)
             if fitness < best_fitness:
                 new_best = True
                 best_fitness = fitness
                 best_individual = individual

        if new_best:
            for key in self.weights.keys():
                self.weights[key] = best_individual.weights[key]
        else:
            self.adjust_search_resolution(10)



        self.fitness = self.eval(self.get_PAR_output(), plant_response)




    def eval(self, PAR, plant_response):
        """
        Evaluate the input PAR values and return the fitness (lower is better)
        """
        diff = plant_response - PAR

        fitness = np.sum(np.sqrt(diff**2))

        # print("fitness: ", fitness)

        return fitness



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
    ax.legend()

    for i in range(1000):
        time.sleep(1)
        test.local_search(pr)
        LED_response.set_ydata(test.get_PAR_output())
        LED_response.set_xdata(spectrum_range)

        test2.local_search(pr)
        LED_response2.set_ydata(test2.get_PAR_output())
        LED_response2.set_xdata(spectrum_range)

        ax.relim()
        ax.axis([spectrum_range[0], spectrum_range[-1], 0, 2])
        plt.draw()


    plt.show()
