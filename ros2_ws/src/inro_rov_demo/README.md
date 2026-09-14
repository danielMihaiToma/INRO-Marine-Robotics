# INRO BlueROV2: first ROS exercise

Standard six-thruster BlueROV2, Gazebo Harmonic, ROS 2 Jazzy. This is a simulation-only direct-thrust exercise. ArduSub, tether dynamics, camera and water currents are not modeled here. Water occupies z < 0, the floor is z = -5 m, and the ROV starts at z = -2 m. Blue background represents water; buoyancy and drag supply its physical effects.

## Prepare and build (inside the Dev Container)

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
python3 src/inro_rov_demo/scripts/prepare_model.py
colcon build --packages-select inro_rov_demo --symlink-install
source install/setup.bash
ros2 launch inro_rov_demo demo.launch.py
```

Keep that terminal running. In a second terminal:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
source install/setup.bash
ros2 run inro_rov_demo drive forward --seconds 4 --power 0.4
ros2 run inro_rov_demo drive up --seconds 3 --power 0.4
ros2 run inro_rov_demo drive left --seconds 3 --power 0.4
ros2 topic echo /inro/depth
```

Run commands separately and observe each motion. Other actions: backward, down, right, stop. Stop depth output with Ctrl+C. Ctrl+C in the launch terminal stops the simulation.

Commands stop automatically at their duration. The live mixer sets thrust to zero after 0.5 s without a valid command. Zero thrust does not stop motion instantly or hold depth: inertia, drag and buoyancy still act. If the mixer itself crashes this watchdog cannot operate; stop the simulation. Never connect these teaching commands to the real vehicle.

## ROS topics and units

- `/inro/command`: std_msgs/Float64MultiArray, exactly [surge, heave, yaw] normalized to [-1,1]. Positive means forward, up, left turn. These are effort requests, not m/s or rad/s.
- `/inro/thruster_1/force` through `/inro/thruster_6/force`: signed newtons, capped at 5 N per thruster by the mixer. Direct commands to these topics compete with the mixer; use `/inro/command` for this exercise.
- `/inro/odometry`: nav_msgs/Odometry, simulator ground truth; world coordinates with z up. This is not a simulated DVL estimate.
- `/inro/depth`: std_msgs/Float64, -z in metres below z=0; negative above the surface.
- `/inro/imu`: sensor_msgs/Imu, forward-left-up body frame.
- `/clock`: simulation time.

For headless use: `ros2 launch inro_rov_demo demo.launch.py gui:=false`.
Gazebo uses partition `inro_bluerov2`; standalone `gz` inspection commands must set `GZ_PARTITION=inro_bluerov2` too. Run only one INRO demo at a time.

The original model is untuned and slightly positively buoyant. Values are not calibrated to the lab ROV. See UPSTREAM.md for provenance and mesh terms.

Validated on 2026-09-14 with ROS 2 Jazzy and Gazebo Harmonic 8.15.0. The
automated exercise moved forward, descended, turned left, published odometry
and depth, and zeroed all six thrusters after both a command timeout and an
invalid command.
