import numpy as np
import matplotlib.pyplot as plt

import roller

def success_histogram(sample_size, attr, n, bins=0, path='/tmp/stats.png'):
    """Generates a histogram plot, returns (success data, figure bytes or path string)
    """
    data = np.empty(sample_size)
    for i in range(sample_size):
        data[i] = roller.roll(attr, 0, n, min_success=-attr-n).total

    # neat trick with np.unique for data for bar graph
    labels, counts = np.unique(data, return_counts=True)
    fig, ax = plt.subplots(1,1)

    ax.set_title("Attribute score = {attr}, {n}d10; {samples} {sample_noun}".format(attr=attr, n=n, die_noun='die' if n==1 else 'dice', samples=sample_size, sample_noun='sample' if sample_size == 1 else 'samples'))
    ax.set_xlabel("Successes")
    ax.set_ylabel("Instances")
    ax.set_xticks(labels)

    # https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html
    rects = ax.bar(labels, counts, align='center')
    for rect in rects:
        h = rect.get_height()
        w = rect.get_width()
        percentage = h / sample_size * 100

        # annotate each rect with a label
        ax.annotate('{:.1f}%'.format(percentage),
                    xy=(rect.get_x() + w / 2, h), # xy coord tuple of annotation
                    xytext=(0,3),                 # offset of text
                    textcoords="offset points",   #
                    ha='center', # center horizontal alignment
                    va='bottom'  # bottom vertical alignment
                    )
        ax.annotate('{}'.format(h),
                    xy=(rect.get_x() + w / 2, h), # xy coord tuple of annotation
                    xytext=(0,12),                # offset of text
                    textcoords="offset points",   #
                    ha='center', # center horizontal alignment
                    va='bottom'  # bottom vertical alignment
                    )

    ax.set_ymargin(0.15) # add 15% extra space at top to fit labels

    # increase figure width with more data
    # TODO figure out a more elegant way to handle this
    fig.set_figwidth(1 * len(labels), forward=True)

    plt.savefig(path)
    return path
