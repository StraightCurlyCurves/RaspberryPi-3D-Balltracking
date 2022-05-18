# Raspberry Pi 3D Balltracker

The Raspberry Pi 3D Balltracker allows you to track a ball in 3D with a 2D camera on the Raspberry Pi.
The 3D coordinates of the ball are then transmitted over the network to a computer where the camera and the ball are visualized with `open3d`.

## Setup

### Raspberry

- activate ssh: https://www.raspberrypi.com/documentation/computers/remote-access.html#setting-up-an-ssh-server.
- make sure `picamera`, `opencv`,`numpy` ,`socket` ,`pickle` and `pandas` is installed for python 3.
- install vncserver with `sudo apt install tightvncserver` (outdated, consider to use a different one).

### Computer

#### Windows

- make sure `open3d` ,`socket` ,`pickle` ,`collections`, `pandas` and `numpy` is installed for python 3.
- install TightVNC: https://www.tightvnc.com/.

#### Linux (VM)
- make sure `open3d` ,`socket` ,`pickle` ,`collections`, `pandas` and `numpy` is installed for python 3.
- install realvnc: https://www.realvnc.com/.
- change network settings in VM to "bridge".

## How to run

- connect raspberry and computer to the same network.
- connect to raspberry via ssh.
- start vnc server on the raspberry: `vncserver :1 -geometry 1920x1080 -depth 16`. The first time a password has to be set.
- start TightVNC Viewer or realvnc on the computer and connect to the raspberry: raspberry-IP:display, i.e: 192.168.43.59:1.
- change first four parameters in `tracking_raspberry.py` **AND** `udp_echo_server_and_visualisation.py` accordingly.
- run `tracking_raspberry.py` on the raspberry (via UI in vnc, not over ssh).
- three windows will open; mask your object of interest.
- run `udp_echo_server_and_visualisation.py` on the computer.

Note: Masking parameters will be saved. If light/object doesn't change, it is possible to change the variable `with_windows` to `False` and run `tracking_raspberry.py` via ssh without VNC server/viewer needed. 