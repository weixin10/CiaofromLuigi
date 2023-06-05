# CiaofromLuigi-Smart-Garden-

CircuitPython script for monitoring Luigi the plant’s health using an Adafruit dashboard. 
<br><br>
<img src="Images/Adafruit dashboard.png" class = "center">
<br><br>
Grove temperature and humidity sensor(https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/) as well as Grove moisture sensor(https://wiki.seeedstudio.com/Grove-Moisture_Sensor/) are used to monitor environment temperature, air humidity and soil moisture levels respectively. The sensors are connected to WiFi-enabled Arduino Nano RP2040(https://docs.arduino.cc/hardware/nano-rp2040-connect) to allow for the readings taken every hour to be published and displated on an Adafruit dashboard.
<br><br>
<img src="Images/circuit.png" class = "center">
<br><br>
The script also publishes preset messages on the message feed on Adafruit when the plant is under sub-optimal conditions defined by moisture, temperature and humidity thresholds. The messages remind the owner to water the plant or to perform other necessary actions such as move the plant into a shader area. If the plant is not watered, the script will continue sending reminders to water the plant every 10 min until the owner waters the plant. The plant is watered with using a 12 V DC peristaltic pump that is configured to be turned on/off using the Adafruit dashboard. The script also sends the owner a random preset motivational quote every 24 hours. 
<br><br><img src="Images/messages.png"><br><br>
The code for connecting to WiFi, callback functions and initialising the MQTT Client is adapted from here [1] (https://learn.adafruit.com/quickstart-rp2040-pico-with-wifi-and-circuitpython/usage-with-adafruit-io)
