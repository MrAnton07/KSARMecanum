#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32_multi_array.hpp"
#include <termios.h>
#include <stdio.h>

static struct termios oldt, newt;

int getch()
{
  static bool firstTime = true;

  if (firstTime)
    {
      firstTime = false;
      tcgetattr( STDIN_FILENO, &oldt);
      newt = oldt;
      newt.c_lflag &= ~(ICANON);
      tcsetattr( STDIN_FILENO, TCSANOW, &newt);
    }

  int c = getchar();

  return c;
}

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  auto node = rclcpp::Node::make_shared("keyboard_node");
  auto publisher = node->create_publisher<std_msgs::msg::Float32MultiArray>("motor_control_topic", 10);

  std_msgs::msg::Float32MultiArray message;

  rclcpp::WallRate loop_rate(100);
  while (rclcpp::ok())
  {
    int c = getch();
    switch(c)
    {
    case 119: // up arrow key
      message.data = {16.0, 0.0, 0.0};
      break;
    case 115: // down arrow key
      message.data = {-16.0, 0.0, 0.0};
      break;
    case 100: // right arrow key
      message.data = {0.0, -15.0, 0.0};
      break;
    case 97: // left arrow key
      message.data = {0.0, 15.0, 0.0};
      break;
    case 46: // left arrow key
      message.data = {14.0, 8.0, 3.0};
      break;
    case 44: // left arrow key
      message.data = {-8.0, -14.0, -5.0};
      break;
    default:
      message.data = {0.0, 0.0, 0.0};
      break;
    }

    RCLCPP_INFO(node->get_logger(), "Publishing: '%d'", c);
    publisher->publish(message);

    rclcpp::spin_some(node);
    loop_rate.sleep();
  }

  tcsetattr( STDIN_FILENO, TCSANOW, &oldt);

  rclcpp::shutdown();

  return 0;
}