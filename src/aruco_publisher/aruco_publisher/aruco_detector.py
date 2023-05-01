import cv2
import cv2.aruco as aruco
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray

class DetectorPublisher(Node):
    def __init__(self):
        super().__init__("detector_publisher")
        self.publisher_ = self.create_publisher(Int32MultiArray, "aruco_topic", 10)

    def detector(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        msg = Int32MultiArray()
        ret, frame = cap.read()
        frame_width = frame.shape[1] #w:image-width and h:image-height
        while True:
            iSee = []
            ret, frame = cap.read()

            # определение словаря маркеров ArUco
            aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)

            # параметры детектирования маркеров
            parameters = aruco.DetectorParameters_create()

            # детектирование маркеров во входном кадре
            corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
            x_centerDiff = 1000
            # если маркеры обнаружены
            if ids is not None:
                # рисуем границы маркеров и выводим их идентификаторы
                frame = aruco.drawDetectedMarkers(frame, corners, ids)
                #maxc = max(frame, key=cv2.contourArea)
                #moments = cv2.moments(maxc)
                for i in range(len(ids)):
                    c = corners[i][0]
                    iSee.append(int(ids[i]))
                msg.data = iSee
                if 0 in ids:
                    centerX = corners[0][0][0][0]+ corners[0][0][1][0]
                    x_centerDiff = int(centerX/2 - frame_width/2)
                    msg.data.insert(1, x_centerDiff)
                    msg.data.insert(2, 0)
                    self.publisher_.publish(msg)
                    self.get_logger().info('Publish:  - No Color "%d"' % x_centerDiff)
                elif 2 in ids:
                    centerX = corners[0][0][0][0]+ corners[0][0][1][0]
                    x_centerDiff = int(centerX/2 - frame_width/2)
                    msg.data.insert(1, x_centerDiff)
                    msg.data.insert(2, 0)
                    self.publisher_.publish(msg)
                    self.get_logger().info('Publish:  - No Color "%d"' % x_centerDiff)
                if 11 in  ids:
                    self.get_logger().info('Publish:  - Red')
                    self.publisher_.publish(msg)
                elif 12 in  ids:
                    self.get_logger().info('Publish:  - Green')
                    self.publisher_.publish(msg)

                elif 13 in  ids:
                    self.get_logger().info('Publish:  - Blue')
                    self.publisher_.publish(msg)

            #cv2.imshow('frame', frame)

            # остановка при нажатии на клавишу 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # освобождение ресурсов и закрытие окон
        cap.release()
        cv2.destroyAllWindows()


def main(args = None):
    rclpy.init(args = args)
    ArUco = DetectorPublisher()
    ArUco.detector()
    ArUco.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()    
