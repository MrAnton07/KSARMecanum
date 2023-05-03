import rclpy
from rclpy.node import Node

from time import sleep
from std_msgs.msg import Int32
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import String

class MainAlg(Node):
    __flag = 1
    distance = [0,0]
    AruCo = [-1,-1]
    color = "None"

    def __init__(self):

        super().__init__('MainAlg')
        self.distance_color_pub = self.create_publisher(Int32, 'distance_color_topic', 10)
        self.motor_pub = self.create_publisher(Int32MultiArray, 'motor_control_topic', 10)
        self.servo_pub = self.create_publisher(Int32, 'servo_control_topic', 10)
        self.distance_sub = self.create_subscription(Int32MultiArray, 'distance_topic', self.distance_callback, 10)
        self.color_sub = self.create_subscription(String, 'color_topic', self.color_callback, 10)
        self.aruco_sub = self.create_subscription(Int32MultiArray, 'aruco_topic', self.aruco_callback, 10)

        timer_period = 0.1    # seconds
        self.algorithm_cycle = self.create_timer(timer_period, self.main_algorithm)

    def main_algorithm(self):
        ################################################################# 1 Flag #################################################################
        if (self.__flag == 1):
            self.get_logger().info('MISSION FLAG: "%d"' % self.__flag)
            self.CD_publisher(0)
            if(80 > self.distance[1] > 70):
                self.__flag = 2
                return
            self.motor_publisher(7, 4)

        ################################################################# 2 Flag #################################################################
        if (self.__flag == 2):
            self.get_logger().info('MISSION FLAG: "%d"' % self.__flag)
            if self.AruCo[0] == 0  or self.AruCo[0] == 2:
    
                if self.AruCo[1] <-15:
                    self.motor_publisher(abs(int(self.AruCo[1]/23)),3)
                elif self.AruCo[1] >15:
                    self.motor_publisher(abs(int(self.AruCo[1]/23)),4)
                else:
                    self.motor_publisher(0,0)
                    self.__flag = 3
                    return
            else:
                self.motor_publisher(0,0)
        
        ################################################################# 3 Flag #################################################################
        if (self.__flag == 3):
            self.get_logger().info('MISSION FLAG: "%d"' % self.__flag)
            self.motor_publisher(6, 5)
            if self.AruCo[0] == 0  or self.AruCo[0] == 2:
                if abs(self.AruCo[1]) > 20:
                    self.__flag = 2
                    return                                       #Вынести Этот Блок Кода В Функцию
            if self.distance[0] > 30:
                self.motor_publisher(0, 0)
                for i in range(10000):
                    self.CD_publisher(1)
                if self.distance[0] < 50:
                    self.CD_publisher(1)
                    self.motor_publisher(4, 5)
                    return
                else:
                    self.__flag = 4
            self.CD_publisher(0)

        ################################################################# 4 Flag #################################################################
        if (self.__flag == 4):
            self.get_logger().info('MISSION FLAG: "%d"' % self.__flag)
            self.motor_publisher(6, 6)
            self.CD_publisher(0)
            if(self.distance[0] < 17):
                self.motor_publisher(0, 0)
                self.__flag = 5

    def CD_publisher(self, servo_mess):
        msg = Int32()
        msg.data = servo_mess
        self.distance_color_pub.publish(msg)

    def motor_publisher(self, speed, mode):
        msg = Int32MultiArray()
        msg.data = [speed, mode]
        self.motor_pub.publish(msg)
        #self.get_logger().info('I HEARD: "%d"' % self.distance[0])

    def servo_publisher(self, mode):
        msg = Int32()
        msg.data = mode
        self.servo_pub.publish(msg)
        
    def distance_callback(self, msg):
        self.distance = msg.data

    def aruco_callback(self, msg):
        self.AruCo = msg.data

    def color_callback(self, msg):
        self.color = msg.data

def main(args=None):
    sleep(3)
    rclpy.init(args=args)

    mainAlg = MainAlg()
    rclpy.spin(mainAlg)

    mainAlg.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



