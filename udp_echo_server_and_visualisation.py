"""
Project Name:
    BALLTRACKER

Function of the Program:
    - recognize a ball, track the 3D position of it and send the position over the network to a PC
	- (this file) receive the data from the client and display the ball position with Open3D 

Author:
    Jan Schuessler, FHGR

Latest Version:
    1.0.1 - 2022.05.17 - uploaded to github

Version History:
	1.0 - 2021.05.26 - submitted
    0.1 - 2020.05.24 (started with coding)
"""

import pickle
import signal
import socket
import sys
import open3d as o3d
import threading
import collections
import numpy as np

# these settings has to match with the ones in the tracking file on the Raspberry Pi
img_width = 608
img_height = 400
FOV = np.pi*33/180
OBJECT_RADIUS = 0.02

# Set up CTRL-C handler
def signal_handler(sig, frame):
	print('Closing server socket ...')	
	sock.close()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Config
server_port = 10000
block_size_bytes = 4096

# Create a UDP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
print(f'Listening to port {server_port}')
sock.bind(('', server_port))

def vis3d():
	try:
		global pos, new_data
		sphere = o3d.geometry.TriangleMesh.create_sphere(radius=OBJECT_RADIUS, resolution=100)
		# sphere.compute_triangle_normals()
		sphere.compute_vertex_normals()
		sphere.paint_uniform_color((241/255, 193/255, 0))
		sphere.translate((0,0,-0.1), relative=False)
		cs = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=(0,0,0))

		f = img_width / (2 * np.tan(FOV))
		e = [img_width/2,img_height/2,f]/np.linalg.norm([img_width/2,img_height/2,f])
		cam_end = e*1.5

		camera_points =[
			[0, 0, 0],
			cam_end,
			[cam_end[0], -cam_end[1], cam_end[2]],
			[-cam_end[0], -cam_end[1], cam_end[2]],
			[-cam_end[0], cam_end[1], cam_end[2]]
		]
		camera_lines = [
			[0, 1],
			[0, 2],
			[0, 3],
			[0, 4],
			[1, 2],
			[2, 3],
			[3, 4],
			[4, 1]
		]
		cam_line_set = o3d.geometry.LineSet(
				points=o3d.utility.Vector3dVector(camera_points),
				lines=o3d.utility.Vector2iVector(camera_lines)
			)

		vis = o3d.visualization.Visualizer()
		vis.create_window()
		# vis.get_render_option().background_color = (197/255, 225/255, 247/255)
		vis.get_render_option().background_color = (195/255, 233/255, 244/255)
		vis.add_geometry(cs, reset_bounding_box=False)
		vis.add_geometry(sphere, reset_bounding_box=False)
		vis.add_geometry(cam_line_set, reset_bounding_box=True)

		buf_size = 120
		spheres = collections.deque(maxlen=buf_size-1)
		pos_track = collections.deque(maxlen=buf_size)
		while True:
			# add new position, if new data from the server has arrived
			if new_data:
				n_points = len(pos_track)		
				sphere.translate((pos[0], pos[1], pos[2]), relative=False)
				if pos != [0,0,-0.1]:
					pos_track.appendleft(pos)
				if n_points > 1:
					if len(spheres) == buf_size-1:
						vis.remove_geometry(spheres[buf_size-2], reset_bounding_box=False)
					spheres.appendleft(o3d.geometry.TriangleMesh.create_sphere(radius=OBJECT_RADIUS/2, resolution=20))
					spheres[0].paint_uniform_color((0, 1, 0))
					spheres[0].compute_vertex_normals()
					spheres[0].translate(pos_track[1], relative=False)
					vis.add_geometry(spheres[0], reset_bounding_box=False)
				new_data = False
			vis.update_geometry(sphere)
			vis.poll_events()
			vis.update_renderer()
	except KeyboardInterrupt:
		vis.destroy_window()

pos = [0,0,-0.1]
new_data = False

visualizer = threading.Thread(target=vis3d, args=[])
visualizer.daemon = True
visualizer.start()

while True:
	data, client_address = sock.recvfrom(block_size_bytes)
	if data:
		data = pickle.loads(data)
		pos_old = pos
		pos = [data[0], data[1], data[2]]
		if pos != pos_old:
			new_data = True
			print("X:", round(pos[0], 3), "; Y:", round(pos[1], 3), "; Z:", round(pos[2], 3))