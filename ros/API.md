# Yoke ROS 2 API

ROS 2 Jazzy nodes running on the Pi. Packages:

- `yoke_interfaces` — interface definitions (the `Notify` service)
- `yoke_location` — the three nodes and the launch file

There are no actions. The nodes talk through one topic and one service.

## Overview

```
                 /fix (sensor_msgs/NavSatFix)              /notify (yoke_interfaces/srv/Notify)
 NEO-6M ──UART──▶ [gps_node] ─────────────▶ [location_monitor] ─────────────▶ [notifier] ──HTTPS──▶ ntfy.sh ──▶ phone
 /dev/ttyAMA0      publisher               subscriber + client                server
```

| Name | Kind | Type | Provider | User |
|---|---|---|---|---|
| `/fix` | topic | `sensor_msgs/msg/NavSatFix` | `gps_node` (publisher) | `location_monitor` (subscriber) |
| `/notify` | service | `yoke_interfaces/srv/Notify` | `notifier` (server) | `location_monitor` (client), you from the CLI |

Everything runs in the default namespace with ROS domain ID 0 and the default RMW (Fast DDS).

## Interfaces

### `yoke_interfaces/srv/Notify`

```
# Request
string title      # notification title
string message    # notification body (may contain newlines and a URL)
---
# Response
bool success      # true once ntfy accepted the notification
string error      # reason for the failure, empty on success
```

The call is synchronous from the caller's point of view: the response comes back only after the
notification has been delivered to ntfy or all retries have failed (up to ~30 s).

## Nodes

### `gps_node`

Reads NMEA sentences from the GPS serial port and publishes the position.

- **Publishes** `/fix` (`sensor_msgs/msg/NavSatFix`, QoS depth 10, reliable) for every valid `GGA`
  sentence, i.e. at the receiver's output rate (1 Hz on a NEO-6M).
  - `status.status`: `STATUS_NO_FIX` (-1) without a fix, `STATUS_FIX` (0), or `STATUS_SBAS_FIX` (1) for DGPS/SBAS
  - `status.service`: `SERVICE_GPS`
  - `latitude`, `longitude` in degrees (south and west are negative), `altitude` in metres above sea level
  - `position_covariance`: approximated from HDOP × 5 m (`COVARIANCE_TYPE_APPROXIMATED`);
    `COVARIANCE_TYPE_UNKNOWN` without a fix
  - `header.frame_id`: from the `frame_id` parameter
- Sentences with a bad checksum are dropped. If the port disappears it is reopened automatically.
- Logs `GPS fix acquired` / `No GPS fix` when the fix state changes.

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `port` | string | `/dev/ttyAMA0` | serial device (GPIO14/15) |
| `baud` | int | `9600` | baud rate |
| `frame_id` | string | `gps` | `header.frame_id` of `/fix` |

### `location_monitor`

Decides when the position changed enough to notify.

- **Subscribes** to `/fix`. Messages with `status.status < STATUS_FIX` (no fix) are ignored.
- **Calls** `/notify`:
  1. On the **first fix**: title `GPS fix acquired`. That position becomes the reference point.
  2. When the position is farther than `threshold_m` from the reference point for `confirm_samples`
     fixes **in a row**: title `Moved <distance>` (`Moved 12.3 km`, or metres below 1 km).
     The new position becomes the reference point. A single fix back inside the radius resets the count,
     which filters out GPS jumps.
- Message body for both: `<lat>, <lon>` and a Google Maps link.
- Distance is the great-circle (haversine) distance.
- If `/notify` is not available yet (e.g. right after boot), notifications are queued and sent as
  soon as the service comes up. The result of every call is logged.

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `threshold_m` | double | `10000.0` | distance in metres that counts as a move |
| `confirm_samples` | int | `3` | consecutive fixes beyond the threshold needed to report a move |

### `notifier`

Delivers notifications to the phone through [ntfy](https://ntfy.sh).

- **Provides** `/notify` (`yoke_interfaces/srv/Notify`). Each request is sent with up to 3 attempts
  (waits of 2 s and 5 s between them, 10 s HTTP timeout). Requests are handled in parallel.
- **On startup** sends `Yoke online` with the hostname and IP. It retries every 15 s (up to 40 times)
  until it succeeds, because right after boot the network may be down or the clock not yet synced
  (TLS fails with a wrong clock).
- Publishes with a JSON POST to the ntfy server root: `{"topic", "title", "message"}`.

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `config_file` | string | `/etc/yoke/ntfy.conf` | `key=value` file with `topic=` and optionally `server=` |
| `ntfy_topic` | string | `""` | overrides `topic` from the config file |
| `ntfy_server` | string | `""` | overrides `server`; default `https://ntfy.sh` |

`/etc/yoke/ntfy.conf` is generated at build time from the `NTFY_TOPIC` CI secret (mode 600, owner `yoke`).
Without a topic every `/notify` call fails with `ntfy topic is not configured`.

## Launch

`ros2 launch yoke_location yoke.launch.py` starts all three nodes with `respawn=True`: a node that
crashes is restarted after 5 s.

| Argument | Default | Passed to |
|---|---|---|
| `gps_port` | `/dev/ttyAMA0` | `gps_node.port` |
| `gps_baud` | `9600` | `gps_node.baud` |
| `threshold_m` | `10000.0` | `location_monitor.threshold_m` |

On the Pi the launch runs on boot as user `yoke` from `/etc/init.d/yoke-ros`
(`sudo /etc/init.d/yoke-ros start|stop|restart|status`), with output in `/var/log/yoke-ros.log`.
The init script uses the defaults; to try other values, stop the service and run the launch by hand:

    sudo /etc/init.d/yoke-ros stop
    ros2 launch yoke_location yoke.launch.py threshold_m:=500.0

## Using it from the command line

ROS is sourced in every login shell (`/etc/profile.d/ros.sh`).

    ros2 node list                              # /gps_node /location_monitor /notifier
    ros2 topic echo /fix                        # live position
    ros2 topic hz /fix                          # ~1 Hz with a NEO-6M
    ros2 service call /notify yoke_interfaces/srv/Notify "{title: test, message: hello}"
    ros2 param get /location_monitor threshold_m

Parameters are read once at node start, so `ros2 param set` has no effect on a running node;
use launch arguments instead.

Fake a position (for example to test `location_monitor` without a GPS fix):

    ros2 topic pub --once /fix sensor_msgs/msg/NavSatFix "{status: {status: 0}, latitude: 50.45, longitude: 30.52}"

While `gps_node` is running it keeps publishing the real position too, so stop the service first for a clean test.
