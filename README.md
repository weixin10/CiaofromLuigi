# CiaofromLuigi-Smart-Garden-

## Introduction to the project
Ciao from Luigi is a smart garden as the soil moisture level, humidity and surrounding temperature is continously measured using sensors and displayed on an Adafruit dashboard to allow monitoring by the owner. 
<br><br>
<img src="Images/Adafruit dashboard.png" class = "center">
<br><br>
Reminders to water Luigi the plant will be emailed to the owner when soil moisture level drops below the set threshold. A 12V DC peristaltic pump that pumps water from the reservoir into the soil is also configured so that it can be switched on and off on the Adafruit dashboard to allow for remote watering. The aim of a manual watering function is such that the owner still maintains a relationship with the plant and does not rely only on automatic watering to keep the plant alive.
<br><br>
A 3 min Youtube video explaining the details of the project can be accessed [here](https://www.youtube.com/watch?v=AcPJYAaz1nI).

## Details of CircuitPython script

[Grove temperature and humidity sensor](https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/) and [Grove moisture sensor](https://wiki.seeedstudio.com/Grove-Moisture_Sensor/) are used to monitor environment temperature, humidity and soil moisture levels respectively. The sensors are connected to WiFi-enabled [Arduino Nano RP2040](https://docs.arduino.cc/hardware/nano-rp2040-connect) to allow for the readings taken every hour to be published to Adafruit IO and displayed on a dashboard. The circuit design is as shown in the picture below.
<br><br>
<img src="Images/circuit.png" class = "center">
<br><br>
The script also publishes specific preset messages to the "message" feed on Adafruit when the plant is under sub-optimal conditions defined by moisture, temperature and humidity thresholds set in the script. The messages remind the owner to water the plant or to perform other necessary actions such as to move the plant into the shade. Additionally, the red LED light turns on when the plant needs water, and conversely, the green LED light turns on when the plant is sufficiently watered. If the plant is not watered, the script will continue sending reminders to water the plant every 10 min until the owner waters the plant, after which a thank you message will be sent. The script also sends the owner a random preset motivational quote every 24 hours. Examples of messages sent are shown below.
<br><br><img src="Images/messages.png"><br><br> Image of plant taken from [here](https://www.vecteezy.com/vector-art/3226944-cute-ornamental-plant-icon-cartoon-illustration).<br><br>
When a new message is published to the "message" feed on Adafruit (trigger), an applet created using IFTTT emails the message to the owner (output). The published applet can be accessed [here](https://ifttt.com/applets/CUZQrvq2-message-channel-for-ciao-from-luigi). This can be when the plant requires additional actions such as watering or when it has been 24 hrs since the last motivational message.

The code for connecting to WiFi, callback functions and initialising the MQTT Client is adapted from [here](https://learn.adafruit.com/quickstart-rp2040-pico-with-wifi-and-circuitpython/usage-with-adafruit-io).
