#!/usr/bin/env python3

'''

This python file runs a ROS-node of name drone_control which holds the position of Swift-Drone on the given dummy.
This node publishes and subsribes the following topics:

		PUBLICATIONS			SUBSCRIPTIONS
		/drone_command			/whycon/poses
		/alt_error			/pid_tuning_altitude
		/pitch_error			/pid_tuning_pitch
		/roll_error			/pid_tuning_roll
					
								

Rather than using different variables, use list. eg : self.setpoint = [1,2,3], where index corresponds to x,y,z ...rather than defining self.x_setpoint = 1, self.y_setpoint = 2
CODE MODULARITY AND TECHNIQUES MENTIONED LIKE THIS WILL HELP YOU GAINING MORE MARKS WHILE CODE EVALUATION.	
'''

# Importing the required libraries
from swift_msgs.msg import *
from luminosity_drone.msg import Biolocation
from geometry_msgs.msg import PoseArray
from std_msgs.msg import Int16
from std_msgs.msg import Int64
from std_msgs.msg import Float64
from pid_tune.msg import PidTune
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import rospy
import cv2 as cv
import numpy as np
import time


class swift ():

	def __init__(self):
		
		rospy.init_node('drone_control')	# initializing ros node with name drone_control

		# This corresponds to your current position of drone. This value must be updated each time in your whycon callback
		# [x,y,z]
		self.drone_position = [0.0,0.0,0.0]	

		# [x_setpoint, y_setpoint, z_setpoint]
		# self.setpoint = [0,-6,15]
		# self.startpoint = [6.5,-6.5,15]
		# self.endpoint =[6.5,6.5,15]self.Kp = [24, 24, 28]
		self.Ki = [0.0016, 0.0016, 0.0016]
		self.Kd = [800, 800, 800]
		# self.final_setpoint = [11,11,37]
		# self.start = False
		# self.finish = False
		# self.reverse = False
		#self.setpoint = [[-9,-9,25],[0,-9,25],[9,-9,25],[9,0,25],[0,0,25],[-9,0,25],[-9,9,25],[0,9,25],[9,9,25],[11,11,30]] # whycon marker at the position of the dummy given in the scene. Make the whycon marker associated with position_to_hold dummy renderable and make changes accordingly
		self.setpoint = [[-8.5,-8.5,25],[-3.5,-8.5,25],[3.5,-8.5,25],[8.5,-8.5,25],[8.5,-3.5,25],[3.5,-3.5,25],[-3.5,-3.5,25],[-8.5,-3.5,25],[-8.5,3.5,25],[-3.5,3.5,25],[3.5,3.5,25],[8.5,3.5,25],[8.5,8.5,25] ,[3.5,8.5,25] ,[-3.5,8.5,25],[-8.5,8.5,25],[11,11,28]]
		self.l = 0
		self.alien = "zero"
	
		#Declaring a cmd of message type swift_msgs and initializing values
		self.cmd = swift_msgs()
		self.cmd.rcRoll = 1500
		self.cmd.rcPitch = 1500
		self.cmd.rcYaw = 1500
		self.cmd.rcThrottle = 1500
		self.cmd.rcAUX1 = 1500
		self.cmd.rcAUX2 = 1500
		self.cmd.rcAUX3 = 1500
		self.cmd.rcAUX4 = 1500


		#initial setting of Kp, Kd and ki for [roll, pitch, throttle]. eg: self.Kp[2] corresponds to Kp value in throttle axis
		#after tuning and computing corresponding PID parameters, change the parameters

		self.Kp = [26, 26, 28]
		self.Ki = [0.0016, 0.0016, 0.0016]
		self.Kd = [800, 800, 800]
		
		#-----------------------Add other required variables for pid here ----------------------------------------------

		self.error = [0.0,0.0,0.0] 
		self.prev_error = [0.0,0.0,0.0]
		self.sum_error= [0.0,0.0,0.0]
		self.min_values = [1000,1000,1000]
		self.max_values = [2000,2000,2000]
		







		# Hint : Add variables for storing previous errors in each axis, like self.prev_error = [0,0,0] where corresponds to [pitch, roll, throttle]		#		 Add variables for limiting the values like self.max_values = [2000,2000,2000] corresponding to [roll, pitch, throttle]
		#													self.min_values = [1000,1000,1000] corresponding to [pitch, roll, throttle]
		#																	You can change the upper limit and lower limit accordingly. 
		#----------------------------------------------------------------------------------------------------------

		# # This is the sample time in which you need to run pid. Choose any time which you seem fit. Remember the stimulation step time is 50 ms
		#self.sample_time = 0.03333 # in seconds





		# Publishing /drone_command, /alt_error, /pitch_error, /roll_error
		self.command_pub = rospy.Publisher('/drone_command', swift_msgs, queue_size=1)
		self.alt_error_pub = rospy.Publisher('/alt_error',Float64, queue_size=1)
		self.pitch_error_pub = rospy.Publisher('/pitch_error',Float64, queue_size=1)
		self.roll_error_pub = rospy.Publisher('/roll_error',Float64, queue_size=1)
		self.astrobiolocation = rospy.Publisher('/astrobiolocation' ,Biolocation, queue_size=1)
		#------------------------Add other ROS Publishers here-----------------------------------------------------






	#-----------------------------------------------------------------------------------------------------------


		# Subscribing to /whycon/poses, /pid_tuning_altitude, /pid_tuning_pitch, pid_tuning_roll
		rospy.Subscriber('whycon/poses', PoseArray, self.whycon_callback)
		rospy.Subscriber('/pid_tuning_altitude',PidTune,self.altitude_set_pid)
		rospy.Subscriber('/pid_tuning_pitch',PidTune,self.pitch_set_pid)
		rospy.Subscriber('/pid_tuning_roll',PidTune,self.roll_set_pid)
		rospy.Subscriber('/swift/camera_rgb/image_raw',Image,self.img_set)
		#-------------------------Add other ROS Subscribers here----------------------------------------------------




		#------------------------------------------------------------------------------------------------------------

		self.arm() # ARMING THE DRONE


	# Disarming condition of the drone
	def disarm(self):
		self.cmd.rcAUX4 = 1100
		self.command_pub.publish(self.cmd)
		rospy.sleep(1)

	def arm(self):

		self.disarm()

		self.cmd.rcRoll = 1500
		self.cmd.rcYaw = 1500
		self.cmd.rcPitch = 1500
		self.cmd.rcThrottle = 1000
		self.cmd.rcAUX4 = 1500
		self.command_pub.publish(self.cmd)	# Publishing /drone_command
		rospy.sleep(1)


	# Arming condition of the drone : Best practise is to disa*
	# Whycon callback function
	# The function gets executed each time when /whycon node publishes /whycon/poses 
	def whycon_callback(self,msg):
		self.drone_position[0] = msg.poses[0].position.x
		self.drone_position[1] = msg.poses[0].position.y
		self.drone_position[2] = msg.poses[0].position.z
		#--------------------Set the remaining co-ordinates of the drone from msg----------------------------------------------	#---------------------------------------------------------------------------------------------------------------



	# Callback function for /pid_tuning_altitude
	# This function gets executed each time when /tune_pid publishes /pid_tuning_altitude
	def altitude_set_pid(self,alt):
		self.Kp[2] = alt.Kp * 0.06 
		self.Ki[2] = alt.Ki * 0.0008
		self.Kd[2] = alt.Kd * 0.3
		
	#----------------------------Define callback function like altitide_set_pid to tune pitch, roll--------------

	def pitch_set_pid(self,pitch):
		self.Kp[1] = pitch.Kp * 0.06 
		self.Ki[1] = pitch.Ki * 0.0008
		self.Kd[1] = pitch.Kd * 0.3
		
	def roll_set_pid(self,roll):
		self.Kp[0] = roll.Kp * 0.06 
		self.Ki[0] = roll.Ki * 0.0008
		self.Kd[0] = roll.Kd * 0.3

	def img_set(self,img):
		br = CvBridge()
		self.led = br.imgmsg_to_cv2(img)

		

	#----------------------------------------------------------------------------------------------------------------------

	def pid(self):
		if self.l == len(self.setpoint) :
				self.setpoint[16][2] = 37
				self.cmd.rcThrottle = 0
				self.cmd.rcPitch = 0
				self.cmd.rcRoll = 0
				self.cmd.rcAUX4 = 1100
				self.command_pub.publish(self.cmd)
				rospy.sleep(1)
		else:
				for i in range(0,len(self.error)):
						self.error[i] = -(self.setpoint[self.l][i] - self.drone_position[i])
						if i == 0:
							self.cmd.rcRoll = int((1500 - (self.error[i] * self.Kp[i])) - ((self.error[i] - self.prev_error[i]) * self.Kd[i]) - (self.sum_error[i] * self.Ki[i]))
							if self.cmd.rcRoll > 2000:
								self.cmd.rcRoll = 2000
							if self.cmd.rcRoll < 1000:
								self.cmd.rcRoll = 1000
						if i == 1:
							self.cmd.rcPitch = int(1500 + self.error[i] * self.Kp[i] + (self.error[i] - self.prev_error[i]) * self.Kd[i] + self.sum_error[i] * self.Ki[i])
							if self.cmd.rcPitch > 2000:
								self.cmd.rcPitch = 2000
							if self.cmd.rcPitch < 1000:
								self.cmd.rcPitch = 1000
						if i == 2:
							self.cmd.rcThrottle = int((1580 + (self.error[i] * self.Kp[i])) + ((self.error[i] - self.prev_error[i]) * self.Kd[i]) + (self.sum_error[i] * self.Ki[i]))
							if self.cmd.rcThrottle > 2000:
								self.cmd.rcThrottle = 2000
							if self.cmd.rcThrottle < 1000:
								self.cmd.rcThrottle = 1000

								

						self.prev_error[i] = self.error[i]
						self.sum_error[i]  = self.sum_error[i] + self.error[i]
								
			#------------------------------------------------------------------------------------------------------------------------
						self.command_pub.publish(self.cmd)
						self.alt_error_pub.publish(self.error[2])
						self.pitch_error_pub.publish(self.error[1])
						self.roll_error_pub.publish(self.error[0])
						
						

				if -0.2 < self.error[0] < 0.2 and -0.2 < self.error[1] < 0.2 and -0.2 < self.error[2] < 0.2 and self.l < len(self.setpoint):
							print("reached next ",self.l,"location:",self.drone_position)
							

							self.l = self.l + 1

							blank = np.zeros(self.led.shape, dtype='uint8')

							gray = cv.cvtColor(self.led, cv.COLOR_BGR2GRAY,)

							blur = cv.GaussianBlur(gray,(7,7),cv.BORDER_DEFAULT)

							threshold, thresh = cv.threshold(blur,105,255,0)

							maskedimg = cv.bitwise_and(self.led,self.led,mask= thresh)

							contours , hierachy = cv.findContours(thresh,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
					
				
							if len(contours) > 0:

										cnt = contours[0]
										a = 1
										area = []
										cor_x = []
										cor_y = []
										for c in contours:
											M = cv.moments(c)
											cX = float(M["m10"] / M["m00"])
											cY = float(M["m01"] / M["m00"])
											cv.putText(self.led, '#' + str(a), (int(cX) - 25, int(cY) - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
											cv.drawContours(self.led,contours,-1,(0,0,255),thickness=2)
											area = cv.contourArea(cnt)
											cor_x.append(cX)
											cor_y.append(cY)
											a = a+1
										ax = np.average(cor_x)
										ay = np.average(cor_y)
										sx = (ax)/83.33
										sy = (ay)/83.33
										if self.l == 4 or self.l == 5 or self.l == 12 or self.l ==13:
											sd = (sx)/3 + self.drone_position[0] -6
											st = (sy)/3 + self.drone_position[1]
										else :
											sd = (sx)/3 + self.drone_position[0]
											st = (sy)/3 + self.drone_position[1]
										
								

										if len(contours) == 2:
											self.alien = "alien_a"
											print("Alien_A detected on location x:",sd,"y:",st)

										elif len(contours) == 3:
											self.alien = "alien_b"
											print("Alien_B detected on location x:",sd,"y:",st)

										elif len(contours) == 4:
											self.alien = "alien_c"
											print("Alien_C detected on location x:",sd,"y:",st)
										self.astrobiolocation.publish(self.alien,sd,st,37)
										cv.waitKey(0)



				

		




					
				



if __name__ == '__main__':
	
	swift_drone = swift()
	r = rospy.Rate(30) #specify rate in Hz based upon your desired PID sampling time, i.e. if desired sample time is 33ms specify rate as 30Hz
	while not rospy.is_shutdown():
		swift_drone.pid()
		r.sleep()
