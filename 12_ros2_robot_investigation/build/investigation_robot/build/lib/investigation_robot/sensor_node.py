import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random
import math


class SensorNode(Node):

    def __init__(self):
        super().__init__('sensor_node')
        self.publisher_ = self.create_publisher(Float32, '/sensor_data', 10)
        self.timer = self.create_timer(0.5, self.publish_sensor_data)
        self.angle = 0.0
        self.get_logger().info('Sensor node started — publishing on /sensor_data')

    def publish_sensor_data(self):
        msg = Float32()

        # simule une distance capteur (en metres) avec bruit gaussien
        base_distance = 1.5 + math.sin(self.angle) * 0.8
        noise = random.gauss(0, 0.05)
        msg.data = max(0.0, base_distance + noise)

        self.publisher_.publish(msg)
        self.get_logger().info(f'Distance: {msg.data:.3f} m')
        self.angle += 0.2


def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()