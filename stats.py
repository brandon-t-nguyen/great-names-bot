import numpy as np
import matplotlib.pyplot as plt

import roller

def success_histogram(sample_size, attr, n, bins=0, path='/tmp/stats.png'):
    """Generates a histogram plot, returns (success data, figure bytes or path string)
    """
    data = np.empty(sample_size)
    for i in range(sample_size):
        data[i] = roller.roll(attr, 0, n).total

    if bins <= 0:
        bins = int(max(data))

    fig, ax = plt.subplots(1,1)

    ax.set_title("Attribute score = {attr}, {n}d10; {samples} {sample_noun}".format(attr=attr, n=n, die_noun='die' if n==1 else 'dice', samples=sample_size, sample_noun='sample' if sample_size == 1 else 'samples'))
    ax.set_xlabel("Successes")
    ax.set_ylabel("Instances")
    ax.hist(data, bins=bins)

    # neat trick with np.unique for data for bar graph
    #labels, counts = np.unique(data, return_counts=True)
    #ax.bar(labels, counts, align='center')

    plt.savefig(path)
    return path
