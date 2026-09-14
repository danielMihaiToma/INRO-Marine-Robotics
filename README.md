# INRO-Marine-Robotics
Teaching resources, ROS 2 simulations and practical exercises for the INRO – Instrumentation, Marine Robotics and Power Systems course at UPC.

## ROS 2 Jazzy Dev Container

Requires Docker Desktop running Linux containers and the VS Code Dev Containers extension.
Keep the checkout on a local disk: Docker could not mount this repository from Google Drive's virtual G: drive.

1. Open this folder in VS Code.
2. Press Ctrl+Shift+P and select **Dev Containers: Reopen in Container**.
3. Wait until the status bar shows **Dev Container: INRO - ROS 2 Jazzy**.
4. Open two Bash terminals inside that same VS Code window.
5. In the first terminal run `ros2 run demo_nodes_cpp talker`.
6. In the second terminal run `ros2 run demo_nodes_py listener`.
7. Confirm the listener prints `I heard: [Hello World: ...]`. Stop both with Ctrl+C.

The image uses Ubuntu 24.04 and ROS 2 Jazzy. Bash terminals source ROS automatically.
Put future ROS packages under `ros2_ws/src`. Gazebo Harmonic will be added in a later step.

Validation on 2026-09-14: image build and Dev Containers CLI startup passed;
Ubuntu 24.04 and ROS_DISTRO=jazzy confirmed; Python listener received nine messages from the C++ talker.
VS Code's graphical connection confirmed: the window title shows Dev Container: INRO - ROS 2 Jazzy and the connection logs report successful management and extension-host connections.
