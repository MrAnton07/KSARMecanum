import lgpio
import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32

LED_R = 23
LED_G = 24
LED_Y = 25

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, LED_R)
lgpio.gpio_claim_output(h, LED_G)
lgpio.gpio_claim_output(h, LED_Y)

def light(data):
    if data == 11:
        lgpio.gpio_write(h, LED_R, 1)
        lgpio.gpio_write(h, LED_G, 0)
        lgpio.gpio_write(h, LED_Y, 0)
    elif data == 12:
        lgpio.gpio_write(h, LED_G, 1)
        lgpio.gpio_write(h, LED_R, 0)
        lgpio.gpio_write(h, LED_Y, 0)
    elif data == 13:
        lgpio.gpio_write(h, LED_Y, 1)
        lgpio.gpio_write(h, LED_G, 0)
        lgpio.gpio_write(h, LED_R, 0)
    else:
        lgpio.gpio_write(h, LED_R, 0)
        lgpio.gpio_write(h, LED_G, 0)
        lgpio.gpio_write(h, LED_Y, 0)

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            Int32,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%d"' % msg.data)
        light(msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    lgpio.gpio_write(h, LED_R, 0)
    lgpio.gpio_write(h, LED_G, 0)
    lgpio.gpio_write(h, LED_Y, 0)
    lgpio.gpiochip_close(h)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
