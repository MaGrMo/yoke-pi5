"""Reads NMEA sentences from a serial GPS (u-blox NEO-6M) and publishes /fix."""

import rclpy
import serial
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, NavSatStatus

# Rough user range error of a consumer GPS, in metres; scaled by HDOP for the covariance
UERE_M = 5.0


def nmea_checksum_ok(sentence):
    """True if '$...*hh' has a valid XOR checksum."""
    if not sentence.startswith('$') or '*' not in sentence:
        return False
    body, _, checksum = sentence[1:].partition('*')
    calc = 0
    for ch in body:
        calc ^= ord(ch)
    try:
        return calc == int(checksum[:2], 16)
    except ValueError:
        return False


def nmea_to_degrees(value, hemisphere):
    """'4807.038', 'N' -> 48.1173. Format is (d)ddmm.mmmm."""
    dot = value.index('.')
    degrees = float(value[:dot - 2])
    minutes = float(value[dot - 2:])
    result = degrees + minutes / 60.0
    return -result if hemisphere in ('S', 'W') else result


def parse_gga(sentence):
    """Parse a $xxGGA sentence. Returns None when the receiver has no fix."""
    fields = sentence.split('*')[0].split(',')
    if len(fields) < 10:
        return None
    quality = int(fields[6] or 0)
    if quality == 0 or not fields[2] or not fields[4]:
        return None
    return {
        'lat': nmea_to_degrees(fields[2], fields[3]),
        'lon': nmea_to_degrees(fields[4], fields[5]),
        'quality': quality,
        'satellites': int(fields[7] or 0),
        'hdop': float(fields[8] or 99.0),
        'alt': float(fields[9] or 0.0),
    }


class GpsNode(Node):
    def __init__(self):
        super().__init__('gps_node')
        self.port = self.declare_parameter('port', '/dev/ttyAMA0').value
        self.baud = self.declare_parameter('baud', 9600).value
        self.frame_id = self.declare_parameter('frame_id', 'gps').value

        self.pub = self.create_publisher(NavSatFix, 'fix', 10)
        self.serial = None
        self.buffer = b''
        self.had_fix = None
        self.create_timer(0.05, self.poll)

    def open_serial(self):
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=0)
            self.get_logger().info(f'Opened {self.port} at {self.baud} baud')
        except serial.SerialException as e:
            self.serial = None
            self.get_logger().warn(f'Cannot open {self.port}: {e}', throttle_duration_sec=30.0)

    def poll(self):
        if self.serial is None:
            self.open_serial()
            if self.serial is None:
                return
        try:
            self.buffer += self.serial.read(4096)
        except serial.SerialException as e:
            self.get_logger().warn(f'Serial error, reopening: {e}')
            self.serial.close()
            self.serial = None
            return

        *lines, self.buffer = self.buffer.split(b'\n')
        for raw in lines:
            line = raw.decode('ascii', errors='ignore').strip()
            if line[3:6] == 'GGA' and nmea_checksum_ok(line):
                self.handle_gga(line)

    def handle_gga(self, line):
        try:
            gga = parse_gga(line)
        except ValueError:
            return

        msg = NavSatFix()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        msg.status.service = NavSatStatus.SERVICE_GPS

        if gga is None:
            msg.status.status = NavSatStatus.STATUS_NO_FIX
            msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_UNKNOWN
        else:
            # GGA quality 2 = DGPS/SBAS
            msg.status.status = (NavSatStatus.STATUS_SBAS_FIX if gga['quality'] == 2
                                 else NavSatStatus.STATUS_FIX)
            msg.latitude = gga['lat']
            msg.longitude = gga['lon']
            msg.altitude = gga['alt']
            horizontal = (gga['hdop'] * UERE_M) ** 2
            msg.position_covariance = [horizontal, 0.0, 0.0,
                                       0.0, horizontal, 0.0,
                                       0.0, 0.0, 4.0 * horizontal]
            msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_APPROXIMATED

        has_fix = gga is not None
        if has_fix != self.had_fix:
            self.get_logger().info('GPS fix acquired' if has_fix else 'No GPS fix')
            self.had_fix = has_fix
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = GpsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
