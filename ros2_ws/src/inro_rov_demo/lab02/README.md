# Laboratory 2 - Your first ROS 2 subscriber

Student manual: [INRO Laboratory 2 - First ROS 2 Subscriber](INRO_Laboratory_2_First_ROS2_Subscriber.pdf)

Suggested video: [ROS 2 topic and interface inspection](https://youtu.be/od3JwOeyEXc?si=U0yTUsbvdJPLMCP8)

## Learning goals

By the end of this laboratory, students should be able to:

- explain the roles of a node, topic, message type, subscriber and callback;
- discover a topic and inspect its message interface from the terminal;
- understand a complete Python subscriber that records depth in a CSV file;
- create a second subscriber for `/inro/odometry`;
- extract x, y and z and save them in a CSV file.

Motion is generated with the `drive` commands already used in Laboratory 1.
Students do not create a publisher in this laboratory. They may plot their CSV
data later using any language or application.

## 1. Start the simulator

In the first Dev Container terminal:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
python3 src/inro_rov_demo/scripts/prepare_model.py
colcon build --packages-select inro_rov_demo --symlink-install
source install/setup.bash
ros2 launch inro_rov_demo demo.launch.py
```

Use `gui:=false` when a Gazebo window is unavailable.

## 2. Discover the depth topic

Open a second terminal and source the workspace:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
source install/setup.bash
```

Follow the discovery sequence before looking at Python code:

```bash
ros2 topic list
ros2 topic list -t
ros2 topic info /inro/depth
ros2 topic type /inro/depth
ros2 interface show std_msgs/msg/Float64
ros2 topic echo /inro/depth --once
```

The topic type is `std_msgs/msg/Float64`. Its interface contains one field:

```text
float64 data
```

Therefore a Python callback reads the measured depth with `msg.data`.

## 3. Study and run the depth subscriber

Open `lab02/depth_logger.py` and find:

1. the imports for `rclpy`, `Node` and `Float64`;
2. the class that inherits from `Node`;
3. `create_subscription(Float64, '/inro/depth', ...)`;
4. the callback that reads `msg.data`;
5. the line that writes `time_s` and `depth_m` to the CSV file;
6. `rclpy.spin(node)`, which keeps the node running.

Run the example:

```bash
python3 src/inro_rov_demo/lab02/depth_logger.py
```

Move the ROV from a third sourced terminal:

```bash
ros2 run inro_rov_demo drive down --seconds 4 --power 0.4
ros2 run inro_rov_demo drive up --seconds 4 --power 0.4
```

Stop the logger with Ctrl+C. It saves `lab02/depth_log.csv` with these columns:

```text
time_s,depth_m
```

## 4. Student task: create an odometry subscriber

Create this new file:

```text
ros2_ws/src/inro_rov_demo/lab02/odometry_logger.py
```

Use `depth_logger.py` as the pattern and
adapt it one step at a time.

First inspect the new topic and interface:

```bash
ros2 topic info /inro/odometry
ros2 topic type /inro/odometry
ros2 interface show nav_msgs/msg/Odometry
ros2 topic echo /inro/odometry --once
```

Your program must:

- import `Odometry` from `nav_msgs.msg`;
- subscribe to `/inro/odometry` using the `Odometry` message type;
- read `msg.pose.pose.position.x`, `.y` and `.z` in the callback;
- print x, y and z while the node runs;
- create `odometry_log.csv` with the columns `time_s,x_m,y_m,z_m`;
- close the CSV correctly when Ctrl+C is pressed.

## 5. Record the motion experiment

Restart the simulator so the ROV begins from the same pose. Start your
`odometry_logger.py` before moving the vehicle. In a third sourced terminal run
these commands one at a time, allowing the vehicle to settle briefly between
them:

```bash
ros2 run inro_rov_demo drive down --seconds 4 --power 0.4
ros2 run inro_rov_demo drive forward --seconds 4 --power 0.4
ros2 run inro_rov_demo drive up --seconds 4 --power 0.4
```

Stop your logger with Ctrl+C and inspect `odometry_log.csv`.

## 6. Report

Submit:

- your `odometry_logger.py`;
- the recorded `odometry_log.csv`;
- plots of x, y and z versus time, created with any language or application;
- a short explanation of which position changes during down, forward and up;
- answers to the questions below.

Questions:

1. What message type is used by `/inro/odometry`?
2. Which command reveals all fields in that message interface?
3. What event causes the callback to run?
4. Why is z negative underwater, while depth is positive?
5. Why does the ROV continue moving briefly after a drive command ends?

This is a simulation-only exercise. Never run these commands on a real ROV.
