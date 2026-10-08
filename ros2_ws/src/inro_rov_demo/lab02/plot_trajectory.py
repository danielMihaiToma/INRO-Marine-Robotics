#!/usr/bin/env python3
"""Create report-ready plots from the Laboratory 2 CSV file."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


CSV_FILE = Path(__file__).with_name('rov_trajectory.csv')
OUTPUT_FILE = Path(__file__).with_name('rov_trajectory.png')


with CSV_FILE.open(newline='', encoding='utf-8') as csv_file:
    rows = list(csv.DictReader(csv_file))

if not rows:
    raise RuntimeError(f'No data found in {CSV_FILE}')

time_s = [float(row['time_s']) for row in rows]
x_m = [float(row['x_m']) for row in rows]
y_m = [float(row['y_m']) for row in rows]
z_m = [float(row['z_m']) for row in rows]
depth_time_s = [float(row['time_s']) for row in rows if row['depth_m']]
depth_m = [float(row['depth_m']) for row in rows if row['depth_m']]

figure = plt.figure(figsize=(11, 8))

time_plot = figure.add_subplot(2, 2, 1)
time_plot.plot(time_s, x_m, label='x')
time_plot.plot(time_s, y_m, label='y')
time_plot.plot(time_s, z_m, label='z')
time_plot.set_xlabel('Time [s]')
time_plot.set_ylabel('Position [m]')
time_plot.grid(True)
time_plot.legend()

depth_plot = figure.add_subplot(2, 2, 2)
depth_plot.plot(depth_time_s, depth_m)
depth_plot.set_xlabel('Time [s]')
depth_plot.set_ylabel('Depth [m]')
depth_plot.grid(True)
depth_plot.invert_yaxis()

trajectory_plot = figure.add_subplot(2, 1, 2, projection='3d')
trajectory_plot.plot(x_m, y_m, z_m)
trajectory_plot.scatter(x_m[0], y_m[0], z_m[0], label='start')
trajectory_plot.scatter(x_m[-1], y_m[-1], z_m[-1], label='end')
trajectory_plot.set_xlabel('x [m]')
trajectory_plot.set_ylabel('y [m]')
trajectory_plot.set_zlabel('z [m]')
trajectory_plot.legend()

figure.suptitle('BlueROV2 trajectory')
figure.tight_layout()
figure.savefig(OUTPUT_FILE, dpi=180)
print(f'Plot saved to {OUTPUT_FILE}')
