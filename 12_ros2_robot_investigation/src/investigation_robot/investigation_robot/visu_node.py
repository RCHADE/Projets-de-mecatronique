import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import threading


WINDOW_SIZE = 50
SAFE_DISTANCE = 0.5


class VisuNode(Node):

    def __init__(self):
        super().__init__('visu_node')
        self.distances = deque([0.0] * WINDOW_SIZE, maxlen=WINDOW_SIZE)
        self.subscription = self.create_subscription(Float32, '/sensor_data', self.callback, 10)
        self.get_logger().info('Visu node started — real-time plot active')

    def callback(self, msg):
        self.distances.append(msg.data)


def ros_thread(node):
    rclpy.spin(node)


def main(args=None):
    rclpy.init(args=args)
    node = VisuNode()

    thread = threading.Thread(target=ros_thread, args=(node,), daemon=True)
    thread.start()

    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-', linewidth=2, label='Distance (m)')
    threshold = ax.axhline(y=SAFE_DISTANCE, color='r', linestyle='--', label=f'Seuil sécurité ({SAFE_DISTANCE} m)')

    ax.set_xlim(0, WINDOW_SIZE)
    ax.set_ylim(0, 3.5)
    ax.set_xlabel('Échantillons')
    ax.set_ylabel('Distance (m)')
    ax.set_title('Robot Investigation — Distance capteur temps réel')
    ax.legend()
    ax.grid(True, alpha=0.3)

    def update(frame):
        data = list(node.distances)
        line.set_data(range(len(data)), data)
        color = 'red' if data[-1] < SAFE_DISTANCE else 'blue'
        line.set_color(color)
        return line,

    ani = animation.FuncAnimation(fig, update, interval=200, blit=True)
    plt.tight_layout()
    plt.show()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()