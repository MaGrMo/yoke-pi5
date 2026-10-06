"""Provides the /notify service and delivers notifications through ntfy (https://ntfy.sh)."""

import json
import socket
import time
import urllib.error
import urllib.request

import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from yoke_interfaces.srv import Notify

RETRY_DELAYS_S = (2.0, 5.0)        # waits between the 3 attempts of one notification
STARTUP_RETRY_PERIOD_S = 15.0      # the "online" message is retried until the network is up
STARTUP_MAX_ATTEMPTS = 40


def read_config(path):
    """Reads 'key=value' lines; a missing file gives an empty config."""
    config = {}
    try:
        with open(path) as f:
            for line in f:
                key, sep, value = line.strip().partition('=')
                if sep and not key.startswith('#'):
                    config[key.strip()] = value.strip()
    except OSError:
        pass
    return config


def local_ip():
    """IP of the interface with the default route (no packets are sent)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('1.1.1.1', 80))
            return s.getsockname()[0]
    except OSError:
        return 'unknown'


class Notifier(Node):
    def __init__(self):
        super().__init__('notifier')
        config_file = self.declare_parameter('config_file', '/etc/yoke/ntfy.conf').value
        config = read_config(config_file)
        self.topic = self.declare_parameter('ntfy_topic', '').value or config.get('topic', '')
        self.server = (self.declare_parameter('ntfy_server', '').value
                       or config.get('server', 'https://ntfy.sh')).rstrip('/')
        if not self.topic:
            self.get_logger().error(f'No ntfy topic: set "topic=" in {config_file}')

        # Service calls may run in parallel; the startup timer never overlaps itself
        self.create_service(Notify, 'notify', self.on_notify,
                            callback_group=ReentrantCallbackGroup())
        self.startup_attempts = 0
        self.startup_last_try = float('-inf')
        self.startup_timer = self.create_timer(1.0, self.send_startup,
                                              callback_group=MutuallyExclusiveCallbackGroup())

    def on_notify(self, request, response):
        response.success, response.error = self.send(request.title, request.message)
        return response

    def send_startup(self):
        # First try after 1 s, then every STARTUP_RETRY_PERIOD_S until delivered
        if time.monotonic() - self.startup_last_try < STARTUP_RETRY_PERIOD_S:
            return
        self.startup_last_try = time.monotonic()
        self.startup_attempts += 1
        ok, error = self.send_once('Yoke online', f'{socket.gethostname()} is up, IP {local_ip()}')
        if ok or self.startup_attempts >= STARTUP_MAX_ATTEMPTS:
            self.startup_timer.cancel()
            if not ok:
                self.get_logger().error(f'Giving up on the startup notification: {error}')
        else:
            self.get_logger().warn(f'Startup notification failed, will retry: {error}',
                                   throttle_duration_sec=60.0)

    def send(self, title, message):
        """Sends with retries. Returns (success, error)."""
        error = ''
        for attempt in range(len(RETRY_DELAYS_S) + 1):
            if attempt:
                time.sleep(RETRY_DELAYS_S[attempt - 1])
            ok, error = self.send_once(title, message)
            if ok:
                return True, ''
            self.get_logger().warn(f'Attempt {attempt + 1} failed: {error}')
        return False, error

    def send_once(self, title, message):
        if not self.topic:
            return False, 'ntfy topic is not configured'
        # JSON publishing keeps non-ASCII text intact (HTTP headers would not)
        body = json.dumps({'topic': self.topic, 'title': title, 'message': message}).encode()
        request = urllib.request.Request(self.server, data=body, method='POST',
                                         headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=10) as reply:
                reply.read()
            self.get_logger().info(f'Sent: {title}')
            return True, ''
        except (urllib.error.URLError, OSError) as e:
            return False, str(e)


def main():
    rclpy.init()
    node = Notifier()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
