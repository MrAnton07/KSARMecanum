import serial
import rclpy
from rclpy.node import Node
from time import sleep

from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray


class DistancePublisher(Node):

    def __init__(self):
        super().__init__('distance_publisher')
        self.publisher_ = self.create_publisher(Int32MultiArray, 'distance_topic', 10)
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        self.str_mess = ""

        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Int32MultiArray()
        self.ser.write(b"1\n")
        self.ser.flush()
        
        if self.ser.in_waiting > 0:
            self.str_mess = self.ser.readline().decode('utf-8').rstrip()
            msg.data = [int(x) for x in self.str_mess.split(',')]
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: "%d"' % msg.data[0])


def main(args=None):
    rclpy.init(args=args)
    sleep(5)

    minimal_publisher = DistancePublisher()

    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
