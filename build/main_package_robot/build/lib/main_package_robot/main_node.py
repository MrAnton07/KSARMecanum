import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32
from std_msgs.msg import Int32MultiArray

class MainAlg(Node):
    __flag = 1

    def __init__(self):

        super().__init__('MainAlg')
        self.motor_pub = self.create_publisher(
            Int32MultiArray,
            'motor_control_topic',
            10)
        self.distance_sub = self.create_subscription(
            Int32MultiArray,
            'distance_topic',
            self.distance_callback,
            10)
        self.aruco_sub = self.create_subscription(
            Int32MultiArray,
            'aruco_topic',
            self.aruco_callback,
            10)



    def motor_publisher(self, speed, mode):
        msg = Int32MultiArray()
        msg.data = [speed, mode]
        self.motor_pub.publish(msg)
        self.get_logger().info('Publish: "%d"' % mode)
        
    def distance_callback(self, msg):
        if self.__flag == 1:
            if len(msg.data) != 0:
                self.get_logger().info('I heard: "%d"' % msg.data[0])
                if msg.data[0] < 50:
                    self.motor_publisher()
        if self.__flag == 2:
            pass
        if self.__flag == 3:
            pass

    def aruco_callback(self, msg):
        if self.__flag == 1:
            if len(msg.data) != 0:
                self.get_logger().info('I heard: "%d"' % msg.data[0])
                if msg.data[0] == 0  or msg.data[0] == 2:
                    dist_mark = msg.data[1]
                    if(abs(dist_mark)<150):
                        if dist_mark <-15:
                            self.motor_publisher(abs(int(dist_mark/10)),3)
                        elif dist_mark >15:
                            self.motor_publisher(abs(int(dist_mark/10)),4)
                        else:
                            self.motor_publisher(0,0)
                else:
                    self.motor_publisher(0,0) 
        if self.__flag == 2:
            pass
        if self.__flag == 3:
            pass



def main(args=None):
    rclpy.init(args=args)

    mainAlg = MainAlg()
    rclpy.spin(mainAlg)

    mainAlg.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



