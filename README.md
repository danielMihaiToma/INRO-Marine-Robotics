# INRO-Marine-Robotics
Teaching resources, ROS 2 simulations and practical exercises for the INRO – Instrumentation, Marine Robotics and Power Systems course at UPC.

## ROS 2 Jazzy Dev Container

Requires Docker Desktop running Linux containers and the VS Code Dev Containers extension.
Keep the checkout on a local disk: Docker could not mount this repository from Google Drive's virtual G: drive.

1. Open this folder in VS Code.
2. Press Ctrl+Shift+P and select **Dev Containers: Reopen in Container**.
3. Wait until the status bar shows **Dev Container: INRO - ROS 2 Jazzy + Gazebo Harmonic**.
4. Open two Bash terminals inside that same VS Code window.
5. In the first terminal run `ros2 run demo_nodes_cpp talker`.
6. In the second terminal run `ros2 run demo_nodes_py listener`.
7. Confirm the listener prints `I heard: [Hello World: ...]`. Stop both with Ctrl+C.

The image uses Ubuntu 24.04 and ROS 2 Jazzy. Bash terminals source ROS automatically.
Put future ROS packages under `ros2_ws/src`. Gazebo Harmonic and the ROS/Gazebo bridge are installed with `ros-jazzy-ros-gz`.

The first ROS/Gazebo exercise is a standard six-thruster BlueROV2. See
[`ros2_ws/src/inro_rov_demo/README.md`](ros2_ws/src/inro_rov_demo/README.md)
for model preparation, launch, motion commands, feedback topics, safety behavior,
and the limits of the untuned teaching model.

Laboratory 1 introduces commanded vertical speed, depth holding at 20 m and
50 m, and a CTD-derived density profile. See
[`ros2_ws/src/inro_rov_demo/lab01/README.md`](ros2_ws/src/inro_rov_demo/lab01/README.md).

Validation on 2026-09-14: image build and Dev Containers CLI startup passed;
Ubuntu 24.04 and ROS_DISTRO=jazzy confirmed; Python listener received nine messages from the C++ talker.
VS Code's graphical connection confirmed: the window title shows Dev Container: INRO - ROS 2 Jazzy and the connection logs report successful management and extension-host connections.

## Gazebo Harmonic on Windows (Docker Desktop + WSLg)

The Dev Container mounts Docker Desktop's WSLg X11 socket. This GUI configuration is specific to Windows with Docker Desktop's WSL2 backend and WSLg available.
Software rendering is enabled initially for compatibility; larger simulations may be slow.

After pulling changes to `.devcontainer`, save your work and use **Dev Containers: Rebuild Container** in VS Code.
In a new container terminal:

```bash
gz sim --versions
gz sim -v 4 shapes.sdf
```

A Gazebo window should appear with the bundled shapes world. Press its Play button to run the simulation.
Close the window and press Ctrl+C in the launch terminal to stop it.

To run the physics simulation without a window:

```bash
gz sim -s -r shapes.sdf
```

Official installation reference: https://gazebosim.org/docs/harmonic/ros_installation/

Gazebo validation on 2026-09-14: the updated image built successfully; `gz sim --versions` reported 8.15.0 (Harmonic); the bundled shapes simulation ran; the user confirmed the 3D shapes were visible through WSLg; a Gazebo-to-ROS `/clock` bridge delivered simulation time to `ros2 topic echo /clock --once`.

### VS Code automatic Wayland mount on Windows

In local VS Code User Settings, disable **Dev Containers: Mount Wayland Socket** (`dev.containers.mountWaylandSocket: false`). This is an application-level setting, so it must be set on each Windows host rather than in the container settings. The project already mounts WSLg's X11 socket for Gazebo. Disabling the extra automatic mount avoids a startup failure referencing `/run/guest-services/distro-services/ubuntu-22-04.sock` when Docker cannot access that distribution's mount service.
