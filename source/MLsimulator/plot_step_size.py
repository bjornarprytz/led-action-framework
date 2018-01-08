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
    pr = np.array(plt_PAR)

    plt.ion()

    # plt.pause(0.05)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    step_result, = ax.plot([], [], '-k', color='black', label='Cost ')
    ax.legend()


    num_tests = 100

    stepsz_x = []
    result_y = []

    best_result = 10000.0
    worst_result = 0.0
    best_res_idx = 0
    worst_res_idx = 0

    fewest_iters = 100000000000
    most_iters = 0
    fewest_iters_idx = 0
    most_iters_idx = 0


    records = []
    for k in range(num_tests):
        hill_climber = indi.Individual(w,r,b)

        hill_climber.random_start()
        step_size = (k+1)*0.01

        iterations = hill_climber.hc_get_iterations(pr, 0.000001, step=step_size)

        result = hill_climber.cost_func(pr)

        stepsz_x.append(step_size)
        result_y.append(result)

        if result <= best_result:
            # lower is better
            best_result = result
            best_res_idx = k

        if result >= worst_result:
            worst_result = result
            worst_res_idx = k

        if iterations <= fewest_iters:
            fewest_iters = iterations
            fewest_iters_idx = k

        if iterations >= most_iters:
            most_iters = iterations
            most_iters_idx = k


        print result,"with step size:",step_size

        records.append({'step_size' : step_size, 'result' : result, 'iterations' : iterations})



    step_result.set_ydata(result_y)
    step_result.set_xdata(stepsz_x)

    print "best result:       ",records[best_res_idx]
    print "worst result:      ",records[worst_res_idx]
    print "fewest iterations: ",records[fewest_iters_idx]
    print "most iterations:   ",records[most_iters_idx]

    ax.axis([stepsz_x[0], stepsz_x[-1], 3.0, 4.0])
    while True:
        plt.draw()
