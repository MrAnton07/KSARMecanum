import serial
import rclpy
from rclpy.node import Node
from time import sleep

from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32

class DistanceColorServo(Node):

    def __init__(self):
        super().__init__('DistanceColorServo')
        self.distance_publisher_ = self.create_publisher(Int32MultiArray, 'distance_topic', 10)
        self.color_publisher_ = self.create_publisher(String, 'color_topic', 10)
        self.servo_subscriber_ = self.create_subscription(Int32, 'servo_control_topic', self.servo_callback, 10)
        
        self.ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)
        self.ser.flush()
        self.str_mess = ""

        timer_period = 0.1  # seconds
        self.timer_distance_color = self.create_timer(timer_period, self.timer_distance_color_callback)

    def timer_distance_color_callback(self):
        distance_msg = Int32MultiArray()
        color_msg = String()
        self.ser.write(b"1\n")
        self.ser.flush()
        
        if self.ser.in_waiting > 0:
            self.str_mess = self.ser.readline().decode('utf-8').rstrip()
            VarList = [int(x) for x in self.str_mess.split(',')]

            distance_msg.data = VarList[:2]
            self.distance_publisher_.publish(distance_msg)
            if(VarList[-1] == 1):
                color_msg.data = "Red"
                self.color_publisher_.publish(color_msg)
            elif(VarList[-1] == 2):
                color_msg.data = "Green"
                self.color_publisher_.publish(color_msg)
            else:
                color_msg.data = "Blue"
                self.color_publisher_.publish(color_msg)
            print(distance_msg.data)
            self.get_logger().info('Publishing: "%s"' % color_msg.data)
    
    def servo_callback(self, msg):
        if (msg.data == 0):
            self.ser.write(b"2\n")
            self.ser.flush()
        elif (msg.data == 1):
            self.ser.write(b"3\n")
            self.ser.flush()


def main(args=None):
    rclpy.init(args=args)
    
    Distance_Color_Servo = DistanceColorServo()

    rclpy.spin(Distance_Color_Servo)

    Distance_Color_Servo.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
