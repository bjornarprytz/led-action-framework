# Approximation of 3000K LED [white.png]
wht_LED = [0.0, 0.0, 0.0, 0.6, 0.44, 0.21, 0.37, 0.5, 0.63, 0.69, 0.80, 0.95, 0.96, 0.80, 0.44, 0.1, 0.0]
blu_LED = [0.0, 0.0, 0.0, 0.1, 1.0, 0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
red_LED = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.8, 0.55, 0.05, 0.0, 0.0]


# From K.J. McCree (Table III)
mean_PAR = [0.09, 0.28, 0.43, 0.52, 0.54, 0.51, 0.56, 0.55, 0.61, 0.75, 0.88, 0.95, 0.96, 1.0, 0.42, 0.09, 0.02]

radish_PAR = [0.24, 0.48, 0.50, 0.52, 0.53, 0.53, 0.56, 0.52, 0.58, 0.70, 0.85, 0.92, 0.98, 1.0, 0.41, 0.08, 0.02]

spectrum_range = range(350, 751, 25)


if __name__ == "__main__":
    print len(spectrum_range)