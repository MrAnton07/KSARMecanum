import cv2
import cv2.aruco as aruco
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class DetectorPublisher(Node):
    def __init__(self):
        super().__init__("detector_publisher")
        self.publisher_ = self.create_publisher(Int32, "topic", 10)

    def detector(self):
        cap = cv2.VideoCapture(0)
        msg = Int32()

        while True:
            iSee = 0
            ret, frame = cap.read()

            # определение словаря маркеров ArUco
            aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)

            # параметры детектирования маркеров
            parameters = aruco.DetectorParameters_create()

            # детектирование маркеров во входном кадре
            corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

            # если маркеры обнаружены
            if ids is not None:
                # рисуем границы маркеров и выводим их идентификаторы
                frame = aruco.drawDetectedMarkers(frame, corners, ids)
                for i in range(len(ids)):
                    c = corners[i][0]
                    center = (int((c[0][0] + c[2][0])/2), int((c[0][1] + c[2][1])/2))
                    cv2.putText(frame, str(ids[i][0]), center, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                iSee = ids
            msg.data = int(iSee)
            if msg.data == 11:
                self.get_logger().info('Publish: "%d" - Red' % msg.data)
            elif msg.data == 12:
                self.get_logger().info('Publish: "%d" - Green' % msg.data)
            elif msg.data == 13:
                self.get_logger().info('Publish: "%d" - Blue' % msg.data)
            else:
                self.get_logger().info('Publish: "%d" - No Color' % msg.data)
            self.publisher_.publish(msg)

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
