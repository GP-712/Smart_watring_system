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

### 2- Configure and start service ###
Download and decompress the `Project.zip` file first, then edit  `/Project/mqttListener.py` line 18 (change `ip_server` only): 
```bash
client.connect("ip_server", 1883)
```
install `systemd` for create service to start project every run server:
```bash
sudo yum install -y systemd
```
create file service in `/etc/systemd/system`:
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

## How to configure sensors
1. Open Smart_watring_system/Resources/Sensor_frameware/Frimware/ directory in VS code.
2. Connect the sensor to the computer using the type-c port on the sensor.
3. Open "user-variables.sh" file. 
4. Then edit the folowing lines : 
```
String ssidArr[] = {"Enterprise-pro", "Enterprise_EXT", "Enterprise_EXTN", "Enterprise" };
int ssidArrNo = 4;

const char* ssid = ""; // no need to fill in
const char* password = "password";
const char* ntpServer = "pool.ntp.org";
``` 
Add your ssid to the ssid array and insert your ssid password if required.


5. You can change the device name if desired.
```
const String device_name = "HIGrow"; 
```
6. Adjust time to sleep. 
```
#define TIME_TO_SLEEP  300       //Time ESP32 will go to sleep (in seconds)
```
7. Add your MQTT server credentials.
```
const char broker[] = "146.190.117.90";
int        port     = 1883;
const char mqttuser[] = ""; //add eventual mqtt username
const char mqttpass[] = ""; //add eventual mqtt password
```
8. press the check mark (✓) on the tool bar to build the project.

<p align="center">
<img src="./Screenshots/1.png"><br>
</p>
9. Then press the arrow (→) on the tool bar to upload the code to the sensor board.
<br /> 10. Place the sensor in the desired area.


## How to use

Here is an explanation of use the project
- First one 
- Second one

## Prerequisites

- LilyGo T-Higrow (available from AliExpress).
- Windows 10 , VsCode and PlatformI0 extention.
- MQTT server.
- python V3 with DASH library installed.
