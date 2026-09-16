# Laboratory 1 — Getting started with ROS 2 and the BlueROV2

This first laboratory is for students who have not used Python or ROS 2. You
will launch a simulation, discover nodes and topics, observe the ROV's sensors
and thrusters, and edit **one number** in a provided Python script. Feedback
control, depth holds, and the CTD profile belong to [Laboratory 2](../lab02/README.md).

## Before class: prepare the computer

Install Git for Windows, Docker Desktop with its WSL 2 backend, VS Code, and
the Microsoft Dev Containers extension. Ask for access to the private course
repository. Clone it into a normal local folder, then open the repository root
in VS Code:

```powershell
git clone https://github.com/danielMihaiToma/INRO-Marine-Robotics.git
cd INRO-Marine-Robotics
code .
```

Start Docker Desktop. In VS Code, press Ctrl+Shift+P and select **Dev
Containers: Reopen in Container**. If the menu says **Reopen Folder Locally**,
you are already inside the container. The first build may take several minutes.
See the [student manual](INRO_Laboratory_1_Getting_Started.pdf) for detailed
installation and troubleshooting instructions.

## Start the simulator

In a terminal **inside the Dev Container**:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
python3 src/inro_rov_demo/scripts/prepare_model.py
colcon build --packages-select inro_rov_demo --symlink-install
source install/setup.bash
ros2 launch inro_rov_demo demo.launch.py
```

Keep this terminal open. In Gazebo, right-click `bluerov2`, select **Move to**,
zoom with the mouse wheel, then select **Follow** if desired. The demo pool
starts near 2 m depth and has a floor near 5 m. Run only one demo at a time.

## A. Discover the ROS graph

Open a second terminal in the same Dev Container, then run:

```bash
cd /workspaces/INRO-Marine-Robotics/ros2_ws
source install/setup.bash
ros2 node list
ros2 topic list -t
ros2 topic info /inro/command
```

Find the depth, odometry, IMU, command, and six thruster-force topics. The
thruster topics are `/inro/thruster_1/force` through
`/inro/thruster_6/force`; there is no single `/inro/thrusters` topic.

## B. Observe a short movement

In the second terminal, watch depth:

```bash
ros2 topic echo /inro/depth
```

Open a third terminal, source `install/setup.bash`, and command a short dive:

```bash
ros2 run inro_rov_demo drive down --seconds 4 --power 0.4
```

Watch depth change. Stop the echo with Ctrl+C. Repeat while observing
`/inro/odometry`, `/inro/imu`, and `/inro/thruster_5/force` or
`/inro/thruster_6/force`. Use `ros2 topic echo TOPIC_NAME` for each. Try
`drive forward` and `drive left` for a few seconds and note which thruster
forces change.

| Motion | Which thrusters change? | What happens to depth or heading? |
|---|---|---|
| Down | Student observation | Student observation |
| Forward | Student observation | Student observation |
| Left turn | Student observation | Student observation |
| Zero command after motion | Student observation | Student observation |

**Zero command is not depth hold.** The ROV may still drift due to inertia and
buoyancy. The `drive` command is timed; the mixer also sets forces to zero
after 0.5 s without a command.

## C. Your first Python edit

Open [`first_dive.py`](first_dive.py). Read the comments, but edit only the
line `HEAVE_EFFORT = -0.40`. Predict whether negative effort will move the ROV
up or down. Then, after restarting the simulator from its initial pose, run:

```bash
python3 src/inro_rov_demo/lab01/first_dive.py
```

Observe `/inro/depth` in another terminal. Repeat with `HEAVE_EFFORT = -0.20`
and compare. A smaller magnitude requests less thrust, **not a specific speed**.
You may try a positive value to see the direction reverse. Keep effort within
`[-0.65, 0.65]` and the duration at or below 10 s. Restart the simulator
between comparisons so each trial starts near the same depth.

## Submit

- Your edited `first_dive.py`.
- A short table of the ROS topics you found and what they mean.
- The completed motion/thruster table above.
- Depth before and after each of two Python trials, and two or three sentences
  explaining how the sign and magnitude of heave effort affected motion.

This is a simulation-only exercise. Do not connect these commands to a real
ROV. In Laboratory 2 you will use feedback to stop automatically at a target
depth and hold it despite changing buoyancy.
