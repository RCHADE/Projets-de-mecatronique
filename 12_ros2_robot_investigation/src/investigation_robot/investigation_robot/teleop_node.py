import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


SAFE_DISTANCE = 0.5
NORMAL_SPEED = 0.3
TURN_SPEED = 0.5


class TeleopNode(Node):

    def __init__(self):
        super().__init__('teleop_node')
        self.subscription = self.create_subscription(
            Float32,
            '/sensor_data',
            self.sensor_callback,
            10
        )
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Teleop node started — subscribing to /sensor_data, publishing on /cmd_vel')

    def sensor_callback(self, msg):
        distance = msg.data
        cmd = Twist()

        if distance < SAFE_DISTANCE:
            cmd.linear.x = 0.0
            cmd.angular.z = TURN_SPEED
            self.get_logger().warn(f'Obstacle at {distance:.3f} m — stopping and turning')
        else:
            cmd.linear.x = NORMAL_SPEED
            cmd.angular.z = 0.0
            self.get_logger().info(f'Clear at {distance:.3f} m — moving forward')

        self.publisher_.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()