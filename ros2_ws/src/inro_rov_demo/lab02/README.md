# Laboratory 2 - ROS 2 subscribers, publishers and trajectory data

Student manual: [INRO Laboratory 2 - ROS 2 Data and Motion](INRO_Laboratory_2_ROS2_Data_and_Motion.pdf)

## Learning goals

By the end of this laboratory, students should be able to:

- explain what a subscriber callback does;
- read `/inro/odometry` and `/inro/depth` in Python;
- save time, x, y, z and depth in a CSV file;
- create a publisher for `/inro/command`;
- build a safe sequence of surge, heave and yaw commands;
- plot the recorded trajectory for the laboratory report.

The exercise uses open-loop effort commands. It does not ask the ROV to reach
an exact position or speed, and it does not implement depth control.

## 1. Start the simulator

After pulling this laboratory, run **Dev Containers: Rebuild Container** once
so the plotting library is installed.

In the first Dev Container terminal:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
python3 src/inro_rov_demo/scripts/prepare_model.py
colcon build --packages-select inro_rov_demo --symlink-install
source install/setup.bash
ros2 launch inro_rov_demo demo.launch.py
```

Use `gui:=false` when a Gazebo window is unavailable.

## 2. Inspect the data before writing Python

In a second sourced terminal:

```bash
ros2 topic info /inro/odometry
ros2 topic info /inro/depth
ros2 topic echo /inro/odometry --once
ros2 topic echo /inro/depth --once
```

Find `pose.pose.position.x`, `.y` and `.z` in the odometry message. Gazebo uses
z upward. The `/inro/depth` topic reports positive depth downward.

## 3. Subscriber and CSV logger

Open `lab02/trajectory_logger.py` and identify:

1. the two `create_subscription` calls;
2. the message type and topic for each subscriber;
3. the callback that extracts x, y and z;
4. the line that writes one CSV row.

Run the logger in the second terminal:

```bash
python3 src/inro_rov_demo/lab02/trajectory_logger.py
```

Keep it running. It displays one position update per second and writes all
odometry samples to `lab02/rov_trajectory.csv`. Stop it with Ctrl+C after the
motion experiment.

Create `my_trajectory_logger.py`. Use the example as a guide, but type the two
subscription calls and callback functions yourself. Run your own logger before
continuing and submit this file with the report.

## 4. Publisher and motion sequence

Open `lab02/motion_sequence.py`. A command contains:

```text
[surge, heave, yaw]
```

Positive surge moves forward, negative heave moves down, and positive yaw turns
left. These numbers request normalized effort, not metres per second.

The initial mission descends gently, moves forward and ascends. Predict the
shape of x, y and z before running it. In a third sourced terminal:

```bash
python3 src/inro_rov_demo/lab02/motion_sequence.py
```

Observe the Gazebo window and the live values printed by the logger. Run only
one motion script at a time.

## 5. Write your own mission

Create `my_motion_sequence.py` from the example and write your own `MISSION`
list. Keep each effort in `[-0.40, 0.40]` and each duration at or below 5
seconds. Your mission must contain:

- one vertical motion;
- one forward motion;
- a zero-effort pause between motions;
- a final motion that returns the ROV towards its initial depth.

Optional extension: add a short yaw command followed by another forward motion.
This should make both x and y change.

Restart the simulator before recording the final trial. Start the logger first,
run your motion program, wait two seconds, then stop the logger with Ctrl+C.

## 6. Plot and interpret the data

Create the supplied plot:

```bash
python3 src/inro_rov_demo/lab02/plot_trajectory.py
```

It saves `lab02/rov_trajectory.png`. You may also open the CSV in a spreadsheet.

For the report, include:

- `my_motion_sequence.py` and `my_trajectory_logger.py`;
- the CSV file;
- x, y and z versus time;
- one 3D trajectory plot;
- a table describing each command, duration and expected motion;
- a short comparison between the requested effort and the measured motion.

Explain why zero effort does not instantly stop the ROV and why this open-loop
program cannot guarantee an exact final position.

This is a simulation-only exercise. Never run these commands on a real ROV.
