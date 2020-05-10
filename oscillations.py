import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.ndimage import convolve1d
from scipy.signal import hilbert, welch
import seaborn as sns
from mne.filter import filter_data
from worldometers_parser import WorldMetersParser
matplotlib.use('QT5Agg')
plt.ion()
sns.set()
my_colors = ["#9b59b6", "#3498db", "#2ecc71"]
sns.set_palette(my_colors)

def rose_plot(ax, angles, bins=16, density=None, offset=0, lab_unit="degrees",
              start_zero=False, color='#fd5e53', edgecolor='k', **param_dict):
    """
    Plot polar histogram of angles on ax. ax must have been created using
    subplot_kw=dict(projection='polar'). Angles are expected in radians.
    Adapted from https://stackoverflow.com/questions/22562364/circular-histogram-for-python
    """
    # Wrap angles to [-pi, pi)
    angles = (angles + np.pi) % (2*np.pi) - np.pi

    # Set bins symetrically around zero
    if start_zero:
        # To have a bin edge at zero use an even number of bins
        if bins % 2:
            bins += 1
        bins = np.linspace(-np.pi, np.pi, num=bins+1)

    # Bin data and record counts
    count, bin = np.histogram(angles, bins=bins)

    # Compute width of each bin
    widths = np.diff(bin)

    # By default plot density (frequency potentially misleading)
    if density is None or density is True:
        # Area to assign each bin
        area = count / angles.size
        # Calculate corresponding bin radius
        radius = (area / np.pi)**.5
    else:
        radius = count

    # Plot data on ax
    ax.bar(bin[:-1], radius, zorder=1, align='edge', width=widths,
           edgecolor=edgecolor, fill=True, linewidth=3, color=color, alpha=0.5)

    # Set the direction of the zero angle
    ax.set_theta_offset(offset)

    # Remove ylabels, they are mostly obstructive and not informative
    ax.set_yticks([])


def compute_ma(country='us', N=3):
    cp = WorldMetersParser()
    dates = cp.country_dict[country]['dates']
    infections_perday = np.array(cp.country_dict[country]['graph-cases-daily'])
    deaths_perday = np.array(cp.country_dict[country]['graph-deaths-daily'])
    infections_perday = convolve1d(infections_perday, np.ones((N,)) / N)
    deaths_perday = convolve1d(deaths_perday, np.ones((N,)) / N)
    return dates, infections_perday, deaths_perday


countries = ['us', 'china', 'italy', 'south-korea', 'france', 'spain', 'germany', 'uk', 'united-arab-emirates', 'saudi-arabia']
offset = 14

dates, infections_perday, deaths_perday = compute_ma()

dates = np.array(dates[offset:])


us_max_cases = infections_perday.max()
us_max_deaths = deaths_perday.max()

plt.figure(figsize=(10,6))

plt.plot(infections_perday[offset:]/us_max_cases, linewidth=4)
plt.plot(deaths_perday[offset:]/us_max_deaths, linewidth=4)


dates, infections_perday, deaths_perday = compute_ma('germany')

plt.plot(infections_perday[offset:]/us_max_cases, linewidth=4, linestyle='--', color="#9b59b6")
plt.plot(deaths_perday[offset:]/us_max_deaths, linewidth=4, linestyle='--', color="#3498db")

plt.xlim([0, 69])
plt.ylim([0, 1.01])
plt.show()
plt.savefig('1usa-germany.svg')




dates, infections_perday, deaths_perday = compute_ma()

s1 = infections_perday[offset+40:]
s2 = deaths_perday[offset+40:]

f, p1 = welch(s1, nperseg=20, noverlap=19, detrend='linear', nfft=256, scaling='density')
f, p2 = welch(s2, nperseg=20, noverlap=19, detrend='linear', nfft=256, scaling='density')
plt.figure()
plt.plot(1/f, p1/p1.max(), linewidth=2);plt.xlim([2,20])
plt.plot(1/f, p2/p2.max(), linewidth=2);plt.xlim([2,20])


dates, infections_perday, deaths_perday = compute_ma('germany')

s1 = infections_perday[offset+40:]
s2 = deaths_perday[offset+40:]

f, p1 = welch(s1, nperseg=20, noverlap=19, detrend='linear', nfft=256, scaling='density')
f, p2 = welch(s2, nperseg=20, noverlap=19, detrend='linear', nfft=256, scaling='density')

plt.plot(1/f, p1/p1.max(), linewidth=2, linestyle='--', color="#9b59b6");plt.xlim([2,20])
plt.plot(1/f, p2/p2.max(), linewidth=2, linestyle='--', color="#3498db");plt.xlim([2,20])


plt.savefig('2usa-germany.svg')


dates, infections_perday, deaths_perday = compute_ma()
s1 = infections_perday[offset+20:]
s2 = deaths_perday[offset+20:]

s11 = np.squeeze(filter_data(s1[np.newaxis, :].astype(float), 1, 0.116, 0.151, pad='reflect'))
s22 = np.squeeze(filter_data(s2[np.newaxis, :].astype(float), 1, 0.116, 0.151, pad='reflect'))

s11 = np.angle(hilbert(s11/s11.max()))
s22 = np.angle(hilbert(s22/s22.max()))

fig = plt.figure()
ax = fig.add_subplot(111, projection='polar')
rose_plot(ax, s22-s11, bins=16)



dates, infections_perday, deaths_perday = compute_ma('germany')
s1 = infections_perday[offset+20:]
s2 = deaths_perday[offset+20:]

s11 = np.squeeze(filter_data(s1[np.newaxis, :].astype(float), 1, 0.116, 0.151, pad='reflect'))
s22 = np.squeeze(filter_data(s2[np.newaxis, :].astype(float), 1, 0.116, 0.151, pad='reflect'))

s11 = np.angle(hilbert(s11/s11.max()))
s22 = np.angle(hilbert(s22/s22.max()))

rose_plot(ax, s22-s11, bins=16, edgecolor='#006400', color='#00A4EF')

plt.savefig('3usa-germany.svg')