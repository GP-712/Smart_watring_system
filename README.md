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

install wget for download Project files:\
```bash
sudo yum install wget -y
```


### 2- Git files ###

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
