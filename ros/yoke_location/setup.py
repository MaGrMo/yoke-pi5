from glob import glob

from setuptools import setup

package_name = 'yoke_location'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maksym Morozenko',
    maintainer_email='magrmo@gmail.com',
    description='GPS reader, location monitor and ntfy notifier',
    license='MIT',
    entry_points={
        'console_scripts': [
            'gps_node = yoke_location.gps_node:main',
            'location_monitor = yoke_location.location_monitor:main',
            'notifier = yoke_location.notifier:main',
        ],
    },
)
