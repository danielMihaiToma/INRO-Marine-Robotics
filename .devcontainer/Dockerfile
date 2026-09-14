FROM ros:jazzy-ros-base-noble

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-demo-nodes-cpp \
    ros-jazzy-demo-nodes-py \
    ros-jazzy-ros-gz \
    libgl1-mesa-dri \
    mesa-utils \
    x11-utils \
    python3-colcon-common-extensions \
    git \
    && rm -rf /var/lib/apt/lists/*

# VS Code terminals start Bash directly, without the ROS entrypoint.
RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc
