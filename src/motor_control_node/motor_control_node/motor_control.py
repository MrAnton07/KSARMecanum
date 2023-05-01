import serial
import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32MultiArray


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('motor_topic_subscriber')
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        self.subscription = self.create_subscription(
            Int32MultiArray,
            'distance_topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%d"' % msg.data[1])
        if (msg.data[1]>30):
                self.ser.write(b"3\n")
        elif (msg.data[1]<20):
                self.ser.write(b"0\n")
        elif (msg.data[1]>=20) or (msg.data[1]<=30):
                self.ser.write(b"0\n")
        self.ser.reset_input_buffer()

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
