# Smart Watring System

A smart watering system is a type of irrigation system that uses advanced technology to efficiently water plants and lawns. These systems typically use sensors to measure soil moisture and weather conditions and adjust the watering schedule accordingly. This helps conserve water and prevent over-watering, leading to waste and unhealthy plants. Some smart watering systems also allow users to control and monitor the watering schedule from their smartphone or other devices, making it easier to manage watering needs remotely.

## Table of Contents
- [Overview](https://github.com/GP-712/Smart_watring_system#smart-watring-system)
- [How to install](https://github.com/GP-712/Smart_watring_system#how-to-install)
- [How to configure](https://github.com/GP-712/Smart_watring_system#how-to-configure)
- [How to use](https://github.com/GP-712/Smart_watring_system#how-to-use)
- [Prerequisites](https://github.com/GP-712/Smart_watring_system#prerequisites)

## How to install

Here is an explanation of the steps to install the project

### 1- Install MQTT Broker (Mosquitto) ###
Execute the following commands:
``` bash
sudo yum -y install epel-release
sudo yum -y install mosquitto
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```
After that, edit file `/etc/mosquitto/mosquitto.conf` and add the commands after `# General configuration` (replace `ip_server` with ip server used)
``` pan
listener 1883 ip_server
allow_anonymous true
```
After edit, we need to restart the service to implement the modifications:
``` bash
sudo systemctl restart mosquitto
```

### 2- Git files ###
install wget for download Project files:
```bash
sudo yum install wget -y
```
install unzip for extract files from zip:
```bash
sudo yum install unzip -y
```
unzip file:
```bash
sudo unzip Project.zip
```
edit "/Project/mqttListener.py" line 18 (change ip server): 
```bash
client.connect("ip_server", 1883)
```
install "systemd" for create service to start project every run server:
```bash
sudo yum install -y systemd
```
create file service in "/etc/systemd/system":
```bash
sudo touch /etc/systemd/system/Project.service
```
add the script in file created before:
```bash
[Unit]
Description=project service
After=multi-user.target
[Service]
Type=simple
Restart=always
WorkingDirectory=/Project
ExecStart=/usr/bin/python3 main.py
[Install]
WantedBy=multi-user.target
```
install pip to install python pakages:
```bash
sudo yum install python-pip
```
install needed package python using pip:
```bash
pip install paho-mqtt schedule numpy scikit-learn dash dash_daq dash-bootstrap-components dash_bootstrap_templates plotly_express pandas
```
run the command for reload services:
```bash
sudo systemctl daemon-reload
```
run the commands for start and enable service:
```bash
sudo systemctl enable Project.service
sudo systemctl start Project.service
```

### 3- Configure and start service ###

## How to configure sensors

Here is an explanation of the steps to configure the project
- First one 
- Second one

## How to use

Here is an explanation of use the project
- First one 
- Second one

## Prerequisites

- LilyGo T-Higrow (available from AliExpress).
- Windows 10 , VsCode and PlatformI0 extention.
- MQTT server.
- python V3 with DASH library installed.
