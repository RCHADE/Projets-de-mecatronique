import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
import csv
import os
from datetime import datetime


CRITICAL_DISTANCE = 0.3


class LoggerNode(Node):

    def __init__(self):
        super().__init__('logger_node')

        self.log_file = f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        self.csv_file = open(self.log_file, 'w', newline='')
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(['timestamp', 'distance_m', 'linear_x', 'angular_z', 'anomaly'])

        self.last_distance = None
        self.last_cmd = Twist()

        self.sub_sensor = self.create_subscription(Float32, '/sensor_data', self.sensor_cb, 10)
        self.sub_cmd = self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.timer = self.create_timer(0.5, self.log)

        self.get_logger().info(f'Logger node started — writing to {self.log_file}')

    def sensor_cb(self, msg):
        self.last_distance = msg.data

    def cmd_cb(self, msg):
        self.last_cmd = msg

    def log(self):
        if self.last_distance is None:
            return

        anomaly = self.last_distance < CRITICAL_DISTANCE
        ts = self.get_clock().now().nanoseconds / 1e9

        self.writer.writerow([
            f'{ts:.3f}',
            f'{self.last_distance:.4f}',
            f'{self.last_cmd.linear.x:.3f}',
            f'{self.last_cmd.angular.z:.3f}',
            'CRITICAL' if anomaly else 'OK'
        ])
        self.csv_file.flush()

        if anomaly:
            self.get_logger().error(f'ANOMALY — distance critique: {self.last_distance:.3f} m')

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = LoggerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()