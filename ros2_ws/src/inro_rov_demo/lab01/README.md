# Laboratory 1 — BlueROV2 depth mission

## Objective

Write your first ROS 2 Python controller for a standard BlueROV2. The vehicle
must descend at a specified speed, hold 20 m for 60 seconds, descend and hold
50 m for 60 seconds, then return to 2 m at a specified ascent speed.

This laboratory controls depth only. Horizontal station keeping is reserved
for a later exercise.

## Start the simulator

Inside the VS Code Dev Container:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
python3 src/inro_rov_demo/scripts/prepare_model.py
colcon build --packages-select inro_rov_demo --symlink-install
source install/setup.bash
ros2 launch inro_rov_demo lab1.launch.py
```

In Gazebo, right-click `bluerov2` and choose **Move to** first. This centers the
camera on the ROV. Zoom with the mouse wheel, then right-click the ROV again
and choose **Follow**. Follow preserves the current camera distance; it does
not zoom by itself.

## Inspect the data

Open a second terminal and source the workspace:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
source install/setup.bash
ros2 topic echo /inro/depth
```

Useful topics:

| Topic | Meaning | Units |
|---|---|---|
| `/inro/depth` | ROV depth, positive downward | m |
| `/inro/odometry` | Simulator position and velocity | m, m/s |
| `/inro/ctd/temperature` | Interpolated profile temperature | °C |
| `/inro/ctd/density` | Original CTD profile density | kg/m³ |
| `/inro/ctd/simulation_density` | Density used for the amplified demonstration | kg/m³ |
| `/inro/target_depth` | Controller target | m |
| `/inro/vertical_effort` | Normalized vertical command | −1 to 1 |
| `/inro/mission/state` | Current mission phase | text |

## Student task

Open `student_depth_mission.py` and complete the two functions marked `TODO`:

1. A proportional vertical-speed controller.
2. A depth-hold controller with proportional feedback and speed damping.

Tune the speed gain so the measured speed approaches the requested 0.5 m/s.
Explain the remaining steady error of a proportional controller; adding an
integral term is an optional improvement.

Set `QUICK_TEST = True` while developing. This changes the mission to 5 m and
12 m with five-second holds. Restore `QUICK_TEST = False` for the assessed
20 m and 50 m mission with one-minute holds.

Conventions:

- Depth and depth rate are positive downward.
- Heave effort is positive upward.
- Every effort must be limited to `[-0.65, 0.65]`.
- The mission publishes `[surge, heave, yaw]` on `/inro/command`.

Run your program from the source folder:

```bash
python3 src/inro_rov_demo/lab01/student_depth_mission.py
```

Stop it with Ctrl+C. The program sends zero effort when it exits, and the
thruster mixer also stops all thrusters if commands disappear for 0.5 seconds.
The terminal prints mission state, depth, target, vertical speed and effort
once per second.

## CTD profile experiment

The supplied CSV retains the original temperature and density values. Between
20 m and 50 m its density changes from 1024.3 to 1024.8 kg/m³. That physical
change is too subtle for an introductory visual exercise, so the Gazebo world
uses 10 m layers and multiplies the density anomaly around the surface value
by 8. The published `/inro/ctd/density` remains the original profile; the
explicitly named
`/inro/ctd/simulation_density` reports the amplified value used in the lesson.

At 20 m and 50 m, record the depth error and vertical effort. Explain why the
effort needed to hold depth changes with density.

## Measurements to submit

- Plot or table of target depth and measured depth versus time.
- Mean and maximum absolute depth error during each 60-second hold.
- Mean vertical effort during each hold.
- Measured descent and ascent speeds.
- A short explanation of the density effect and one suggested controller
  improvement.

## Instructor reference run

The repository includes a reference controller for checking the environment:

```bash
ros2 run inro_rov_demo lab1_reference_mission
```

For a quick check without waiting two minutes:

```bash
ros2 run inro_rov_demo lab1_reference_mission \
  --first-depth 5 --second-depth 12 --hold-seconds 3 \
  --descent-speed 0.5 --ascent-speed 0.5
```

The BlueROV2 hydrodynamic model is intentionally untuned. Results demonstrate
control concepts and must not be interpreted as predictions for the real ROV.
