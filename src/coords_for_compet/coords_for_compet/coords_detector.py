import numpy as np
import matplotlib.pyplot as plt
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Point

class NoiseFilter:
        def __init__(self, window_size=5):
            self.window_size = window_size
            self.values = []

        def filter(self, value):
            self.values.append(value)

            while len(self.values) > self.window_size:
                self.values.pop(0)
            values = np.array(self.values)
            
            if not any(len(lst) > 0 for lst in values):
                return [0.0, 0.0]

            values = [sublist for sublist in values if len(sublist) > 0]
            distances = np.linalg.norm(values, axis=1)
            values = np.array(values)
            sorted_points = values[np.argsort(distances)]
            
            return sorted_points[0]
        

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('laser_scan_listener')
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.listener_callback,
            10)
        self.publisher_ = self.create_publisher(Point, "Coord_xy", 10)
        self.Filt = NoiseFilter()
        self.subscription  
        

    def listener_callback(self, msg):
        num_of_measur = len(msg.ranges)
        max_measurement_distance = msg.range_max
        angle = 360/num_of_measur

        measurement_list = list(range(num_of_measur))
        y = [max_measurement_distance if dist > float('inf') else dist for dist in msg.ranges]                                                                        

        points_of_difference = []
        dx = 1
        for x in range(-1, num_of_measur-1):                                                                     
            dy = (y[x+dx] - y[x])/dx
            points_of_difference.append(dy)
        points_of_difference = [abs(point) if point<0 else 0 for point in (points_of_difference)]


        threshold = 0.0 #Задаём Пороговое Значение Для Обработки (Величина Производной)
        decart_xy = [] #Список Точек, Переведённых В Декартову СК (Правая Тройка Векторов, y Сонаправлена С Передом Робота)
        for measurement in measurement_list: 
            if(points_of_difference[measurement] > threshold): #and (points_of_difference[measurement] < 0.2)
                decart_xy.append([y[measurement]*np.sin(angle*measurement*np.pi/180), y[measurement]*np.cos(angle*measurement*np.pi/180)]) 
                
        # self.is_table(sorted(decart_xy, key=lambda row: row[0]))
        for i in decart_xy:
            dist = i[0]**2+i[1]**2
            if(dist<0.04) and (dist >0):
                print(i)
        plt.plot(range(num_of_measur), points_of_difference, 'k') 
        plt.show(block = False) #Задаём True Для Отладки (Для Построения Графика Производных)

    
    def is_table(self, decart_xy):
        table_side_len = 1.62 #Сторона Стола
        table_diagonal_len = table_side_len * np.sqrt(2)
        cluster_treshold = 0.05 
        
        points = np.array(decart_xy)
        arr_length = len(decart_xy)
        threshold = table_diagonal_len*0.07 #Пороговое Значение (В Данном Случае 7% От Длины Диагонали)
        probable_center_coords = []
        vectors_list = []   
        center_coords = []  #Список Наиболее Вероятных Центров Столов
        sorted_points = [[]]

        for i in range(arr_length):
            for j in range(i+1, arr_length):
                    vec = points[i] - points[j]
                    vec_len = self.length(vec)
                    vectors_list.append(vec)
                    if(table_diagonal_len + threshold > vec_len > table_diagonal_len - threshold):        
                        probable_center_coords.append([(decart_xy[i][0]+decart_xy[j][0])/2, (decart_xy[i][1]+decart_xy[j][1])/2])
                        
        arr_coords = np.array(probable_center_coords)
        for i in range(len(arr_coords)):
            tmp_point = [0, 0]
            count_neighbours = 0
            for j in range(len(points)):
                if (((table_diagonal_len + threshold)/2 > self.length(arr_coords[i]-points[j]) > (table_diagonal_len - threshold)/2) and (self.length(points[j]-tmp_point) > cluster_treshold)):   
                    count_neighbours+=1
                    if count_neighbours == 3:
                        center_coords.append(arr_coords[i]) 
                tmp_point = points[j]
        center_coords = np.array(center_coords)
        
        msg = Point()
        if(center_coords != []):
            distances = np.linalg.norm(center_coords, axis=1)
            sorted_points = center_coords[np.argsort(distances)]

        point = self.Filt.filter(sorted_points[0])
        msg.x = point[0]
        msg.y = point[1]
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: x={msg.x}, y={msg.y}")


    def length(self, vec):
        return np.linalg.norm(vec)

    
    

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main() 