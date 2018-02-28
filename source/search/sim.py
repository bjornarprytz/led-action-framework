#!/usr/bin/env python2.7

import matplotlib.pyplot as plt
import numpy as np
import random as rand
import math
import time
import individual as indi
from quantum_yield import *


if __name__ == "__main__":
    rand.seed()
    w = np.array(wht_LED)
    r = np.array(red_LED)
    b = np.array(blu_LED)
    pr = np.array(radish_PAR)

    plt.ion()

    # plt.pause(0.05)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    white_range = ax.plot(spectrum_range, w, '-k', color='yellow', label='White LED')
    red_range = ax.plot(spectrum_range, r, color='red', label='Red LED')
    blue_range = ax.plot(spectrum_range, b, color='blue', label='Blue LED')
    plant_profile = ax.plot(spectrum_range, pr, color='green', label='Action Spectrum')
    LED_response, = ax.plot([], [], '-k', color='black', label='Hill Climbing')
    Annealing_result, = ax.plot([], [], '-k', color='magenta', label='Annealing')
    ax.legend()


    num_tests = 100

    for k in range(num_tests):
        hill_climber = indi.Individual(w,r,b)
        step_size = (k+1)*0.005
        for i in range(100):
            # time.sleep(0.25)
            hill_climber.hill_climb(pr, step=step_size)

        LED_response.set_ydata(hill_climber.get_PAR_output())
        LED_response.set_xdata(spectrum_range)
        print hill_climber.reward_func(pr),"with step size:",step_size



    ax.axis([spectrum_range[0], spectrum_range[-1], 0, 2])
    plt.draw()

    anneal_test = indi.Individual(w,r,b)
    an_res, n_iter = anneal_test.anneal(pr)

    Annealing_result.set_ydata(an_res.get_PAR_output())
    Annealing_result.set_xdata(spectrum_range)

    ax.relim()
    ax.axis([spectrum_range[0], spectrum_range[-1], 0, 2])

    print an_res.reward_func(pr)
    print hill_climber.reward_func(pr)

    while True:
        plt.draw()



    plt.show()
