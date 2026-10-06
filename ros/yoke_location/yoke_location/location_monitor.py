"""Watches /fix and calls /notify on the first fix and when the position moves."""

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, NavSatStatus
from yoke_interfaces.srv import Notify

EARTH_RADIUS_M = 6371000.0


def distance_m(lat1, lon1, lat2, lon2):
    """Great-circle (haversine) distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def describe(lat, lon):
    return f'{lat:.6f}, {lon:.6f}\nhttps://maps.google.com/?q={lat:.6f},{lon:.6f}'


class LocationMonitor(Node):
    def __init__(self):
        super().__init__('location_monitor')
        self.threshold_m = self.declare_parameter('threshold_m', 100.0).value
        # Consecutive fixes beyond the threshold needed to report a move (filters GPS jumps)
        self.confirm_samples = self.declare_parameter('confirm_samples', 3).value

        self.reference = None   # (lat, lon) of the last notified position
        self.beyond_count = 0
        # Notifications waiting for /notify to come up (e.g. right after boot)
        self.pending = []
        self.client = self.create_client(Notify, 'notify')
        self.create_subscription(NavSatFix, 'fix', self.on_fix, 10)
        self.create_timer(2.0, self.flush_pending)

    def on_fix(self, msg):
        if msg.status.status < NavSatStatus.STATUS_FIX:
            return
        lat, lon = msg.latitude, msg.longitude

        if self.reference is None:
            self.reference = (lat, lon)
            self.get_logger().info(f'First fix: {lat:.6f}, {lon:.6f}')
            self.notify('GPS fix acquired', describe(lat, lon))
            return

        dist = distance_m(*self.reference, lat, lon)
        if dist <= self.threshold_m:
            self.beyond_count = 0
            return

        self.beyond_count += 1
        if self.beyond_count < self.confirm_samples:
            return

        self.get_logger().info(f'Moved {dist:.0f} m to {lat:.6f}, {lon:.6f}')
        self.reference = (lat, lon)
        self.beyond_count = 0
        self.notify(f'Moved {dist:.0f} m', describe(lat, lon))

    def notify(self, title, message):
        self.pending.append((title, message))
        self.flush_pending()

    def flush_pending(self):
        if not self.pending:
            return
        if not self.client.service_is_ready():
            self.get_logger().warn('Waiting for /notify', throttle_duration_sec=60.0)
            return
        for title, message in self.pending:
            future = self.client.call_async(Notify.Request(title=title, message=message))
            future.add_done_callback(lambda f, t=title: self.on_notify_done(t, f))
        self.pending.clear()

    def on_notify_done(self, title, future):
        result = future.result()
        if result is not None and result.success:
            self.get_logger().info(f'Notification sent: {title}')
        else:
            error = result.error if result is not None else 'no response'
            self.get_logger().error(f'Notification failed: {title}: {error}')


def main():
    rclpy.init()
    node = LocationMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
