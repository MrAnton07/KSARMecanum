import serial
import io
import time
import os

from math import *
import numpy as np

############################################################################################################################################
class RoboticArm:
    def __init__(self):
        #Объявляем длины звеньев манипулятора и разность между осями в порядке "От земли до захвата"
        self.__l1 = 70
        self.__l2 = 0
        self.__l3 = 141.4
        self.__l4 = 140.58
        self.__l5 = 43.45
        self.__l6 = 75.0
        self.__l7 = 10.0
        
    

    def InversProblem(self,X,Y,Z,pitch = 0):
        #Присваивание соответствующих величин для удобства работы с ними
        l1 = self.__l1
        l2 = self.__l2
        l3 = self.__l3
        l4 = self.__l4
        l5 = self.__l5
        l6 = self.__l6
        l7 = self.__l7
        try:
            #Вычисление всех углов и длин, а также преобразование координат в соответствии с методом решения ОЗК
            alpha_temp = atan2(Y,X)
            tetta = asin(l7/sqrt(X**2+Y**2))
            alpha1 = alpha_temp+tetta
            l = sqrt(X**2+Y**2-l7**2)

            X = l*cos(alpha1)
            Y = l*sin(alpha1)

            z = Z+l6-l1

            x = X/cos(alpha1)
            x = x - l2 - l5 
            
            d = sqrt(x*x+z*z)
            gamma = acos((l3*l3+d*d-l4*l4)/(2*l3*d))
            beta = gamma + atan(z/x)
            alpha2 = pi/2 - beta

            gamma1 = acos((l3*l3+l4*l4-d*d)/(2*l3*l4))
            
            alpha3 = gamma1 - alpha2
            
            s1 = alpha2
            s2 = alpha3
            
            #Приведение полученных значений к соответсвующим управляющим сигналам
            tick1 = alpha1*(180/pi)*2.844+512
            tick2 = 512+alpha2*(180/pi)*2.844
            tick3 = 512+(pi/2 - alpha3)*(180/pi)*2.844
            tick4 = pitch*(180/pi)*2.844

            q = (tick1 ,tick2 ,tick3 ,512)

            return q
        except Exception as e:
            #В случае ошибки при вычислении ОЗК выведет сообщение об ошибке
            print (e)
            return
############################################################################################################################################

#########################################################Установка параметров порта#########################################################
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    

# создаём объект класса RobotArm из OZK и объявляем переменные адресов регистров соответственно состояния, позиции, предыдущей позиции и скорости движения
robot = RoboticArm()
ADDR_MX_TORQUE_ENABLE      = 24               
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36
ADDR_MX_GOAL_SPEED = 32

# Задаём версию протокола 
PROTOCOL_VERSION            = 1.0               

# Устанавливаем ID, скорость обмена данными и имя DXL устройства в сети
DXL_ID                      = [1, 2, 3, 4]                 
BAUDRATE                    = 1000000
DEVICENAME                  = '/dev/ttyACM0'    
                                                
# Устанавливаем "макросы" на вкл/выкл питания на моторе
TORQUE_ENABLE               = 1                
TORQUE_DISABLE              = 0                

# Создаём список предыдущих позиций, темповый списко текущих позиций и желаемую скорость движения
dxl_goal_position_tmp = []
dxl_goal_speed = 100
dxl_present_position = [-1, -1, -1, -1]

# Получаем дескриптор порта, устанавливаем скорость обмена данными, создаём portHandler и packetHandler для управления портом, приём-передачи данных
#ocm = serial.Serial(port='/dev/ttyS1', baudrate=9600)

portHandler = PortHandler(DEVICENAME)

packetHandler = PacketHandler(PROTOCOL_VERSION)
#########################################################Установка параметров порта#########################################################

#########################################################Установка параметров###############################################################
#Открываем порт для обмена-передачи данных
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()


# Устанавливаем скорость обмена данными
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

#Устанавливаем скорость движения звеньев в соответствии с dxl_goal_speed
if ([packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_GOAL_SPEED, dxl_goal_speed) for dxl_id in DXL_ID]):
    print("Speed change successful")
else:
    print("Speed changing is faled!")


# Переводим двигатели в активное состояние
if not ([packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE) for dxl_id in DXL_ID]):
    print("ERROR")
else:
    print("Dynamixel has been successfully connected")

#########################################################Установка параметров###############################################################


#########################################################Рабочий режим######################################################################
while 1:
    #Вводим координаты целевой точки по XYZ в миллиметрах, и также задаём режим работы помпы
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break
    dxl_goal_position = []
    print("Write Goal X Position:\n")
    X  = int(input())
    print("Write Goal Y Position:\n")
    Y  = int(input())
    print("Write Goal Z Position:\n")
    Z  = int(input())
    #print("Write pump state (1 - ON, 0 - OFF):\n")
    #pump_state  = input()
    #ocm.write(pump_state.encode())

    #Решаем обратную задачу, заполняем список соответствующими переменными
    dxl_goal_position_tmp = robot.InversProblem(X, Y, Z)
    for i in dxl_goal_position_tmp:
        dxl_goal_position.append(int(i))
    print(dxl_goal_position)

    #Отправляем команды на моторы
    for i in range(len(DXL_ID)):
       packetHandler.write2ByteTxRx(portHandler, DXL_ID[i], ADDR_MX_GOAL_POSITION, dxl_goal_position[i])

    while 1:
        for i in range(len(DXL_ID)):
            dxl_present_position[i] = packetHandler.read2ByteTxRx(portHandler, DXL_ID[i], ADDR_MX_PRESENT_POSITION)
            print(dxl_present_position)
            print("[ID:%03d] GoalPos:%03d PresPos:%03d" % (DXL_ID[i], dxl_goal_position[i], dxl_present_position[i][0]))
        if i == len(DXL_ID)-1:
                    break
#########################################################Рабочий режим######################################################################

#########################################################Отключение#########################################################################
#Отключаем питание моторов
[packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE) for dxl_id in DXL_ID]
#ocm.write(b"0")

#Закрываем порт
portHandler.closePort()
#########################################################Отключение#########################################################################