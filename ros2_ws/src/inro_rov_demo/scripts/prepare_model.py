#!/usr/bin/env python3
"""Fetch pinned upstream assets and adapt the model locally; meshes are not vendored."""
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

REV = '661264b719ffd2dcdd0d0990de80547d6029cc16'
BASE = f'https://raw.githubusercontent.com/clydemcqueen/bluerov2_gz/{REV}/'
root = Path(__file__).resolve().parents[1]
model_dir = root / 'models' / 'bluerov2'
files = ['model.sdf', 'model.config', 'BlueROV2.md', 'meshes/bluerov2.dae',
         'meshes/t200_cw_prop.dae', 'meshes/t200_ccw_prop.dae']
for name in files:
    target = model_dir / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(urllib.request.urlopen(BASE + 'models/bluerov2/' + name, timeout=90).read())
tree = ET.parse(model_dir / 'model.sdf')
model = tree.getroot().find('model')
for plugin in list(model.findall('plugin')):
    if plugin.get('name') == 'ArduPilotPlugin':
        model.remove(plugin)
sensor = model.find("link[@name='base_link']/sensor")
sensor.find('pose').text = '0 0 0 0 0 0'  # ROS FLU, not the original ArduPilot FRD
sensor.find('update_rate').text = '50'
ET.SubElement(sensor, 'topic').text = '/inro/imu'
odom = ET.SubElement(model, 'plugin', filename='gz-sim-odometry-publisher-system',
                     name='gz::sim::systems::OdometryPublisher')
for key, value in {'odom_frame':'world', 'robot_base_frame':'bluerov2/base_link',
                   'odom_publish_frequency':'20', 'dimensions':'3',
                   'odom_topic':'/model/bluerov2/odometry'}.items():
    ET.SubElement(odom, key).text = value
ET.indent(tree)
tree.write(model_dir / 'model.sdf', encoding='utf-8', xml_declaration=True)
print('Prepared standard six-thruster BlueROV2 at upstream revision ' + REV)
