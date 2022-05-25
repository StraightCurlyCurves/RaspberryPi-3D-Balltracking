# Raspberry Pi 3D Balltracker

The Raspberry Pi 3D Balltracker allows you to track a ball in 3D with a 2D camera on the Raspberry Pi.
The 3D coordinates of the ball are then transmitted over the network to a computer where the camera and the ball are visualized with Open3D.

There are cases in which Open3D has trouble to calculate stuff under Windows with integrated graphics cards. Use a VM with Linux instead.

## Setup

### Raspberry

- Activate ssh: https://www.raspberrypi.com/documentation/computers/remote-access.html#setting-up-an-ssh-server.
- Make sure `picamera`, `opencv`,`numpy` ,`socket` ,`pickle` and `pandas` is installed for python 3.
- Install a VNC server. For example "tightvncserver" with `sudo apt install tightvncserver` (outdated, consider to use a different one).

### Computer

#### Windows

- Make sure `open3d` ,`socket` ,`pickle` ,`collections`, `pandas` and `numpy` is installed for python 3.
- Install a VNC Viewer. For example TightVNC: https://www.tightvnc.com/.

#### Linux (VM)
- Make sure `open3d` ,`socket` ,`pickle` ,`collections`, `pandas` and `numpy` is installed for python 3.
- Install a VNC Viewer. For example realvnc: https://www.realvnc.com/.
- Change network settings in VM to "bridge".

## How to run

- Connect raspberry and computer to the same network.
- Connect to raspberry via ssh.
- Start vnc server on the raspberry: `vncserver :1 -geometry 1920x1080 -depth 16 :1`. The first time a password has to be set.
- Start TightVNC Viewer or realvnc on the computer and connect to the raspberry: raspberry-IP:display, i.e: 192.168.42.42:1.
- Change first four parameters in `tracking_raspberry.py` **AND** `udp_echo_server_and_visualisation.py` accordingly.
- In `network_config.txt`, set the IP address of the computer.
- Run `tracking_raspberry.py` on the raspberry (via UI in vnc, not over ssh).
- Three windows will open; mask your object of interest. The settings will be saved in `settings.csv`. 
- Run `udp_echo_server_and_visualisation.py` on the computer.
- Have fun!

Note: Due the masking parameters will be saved in `settings.csv`, it is possible to set the variable `with_windows` to `False` and run `tracking_raspberry.py` via ssh without VNC server/viewer needed.