# Make ROS 2 available in every login shell
if [ -n "$BASH_VERSION" ]; then
    . /opt/ros/jazzy/setup.bash
else
    . /opt/ros/jazzy/setup.sh
fi
