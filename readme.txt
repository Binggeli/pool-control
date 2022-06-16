Headless setup of raspbian stretch:
- create emtpy file "ssh" in the volume "boot":
  	 touch /Volumes/boot/ssh
- create wpa config file "wpa_supplicant.conf" in the volume "boot":

country=CH
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="Abahachi"
    scan_ssid=1
    psk="your_real_password"
    key_mgmt=WPA-PSK
}

- add lines  to file "config.txt" in the volume "boot":

# Enable 1-wire (e.g. for temperature sensor)
dtoverlay=w1-gpio


Install RPi Relais Board:
- Download the WiringPi libraries: git clone git://git.drogon.net/wiringPi
  (please see: https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/)
  Run commands:
  - cd wiringPi
  - ./build
- Download and Install C Library bcm2835: curl -O http://www.airspayce.com/mikem/bcm2835/bcm2835-1.55.tar.gz
  (please see: http://www.airspayce.com/mikem/bcm2835/index.html)
  Run commands:
  - # download the latest version of the library, say bcm2835-1.xx.tar.gz, then:
  - tar zxvf bcm2835-1.xx.tar.gz
  - cd bcm2835-1.xx
  - ./configure
  - make
  - sudo make check
  - sudo make install
- Python Libraries for Raspbian:
  - sudo python3 -m pip install RPi.GPIO
  - sudo python3 -m pip install spidev
- Download demo code: curl -O https://www.waveshare.com/w/upload/2/24/RPi_Relay_Board.tar.gz

Install DS18B20 Temperature Sensors:
- Edit /boot/config.txt and add line: dtoverlay=w1-gpio
- Reboot (sudo reboot)
- Test with the following commands:
  - sudo modprobe w1-gpio
  - sudo modprobe w1-therm
  - pushd /sys/bus/w1/devices
  - ls
  This will show a directory for every sensor:
  - 28-000008aa92f7
  - 28-0416a5b761ff
- Rot ist 3-5 V Spannung
- Blau / Schwarz wird mit Masse verbunden
- Gelb / Weiß ist die 1-Wire Datenleitung

Install ADS1115 analog digital converter:
- Install adafruit libraries with pip: 
  - sudo python3 -m pip install adafruit-ads1x15
- Enable I2C interface with raspi-config
- Test connectivity: sudo i2cdetect -y 1
- Test ADS1115 with sample program: sudo python simpletest.py

Start flask app:
- add entry to crontab:
  - sudo crontab -e
  - add line: @reboot /bin/bash /home/pi/bin/start_pool_app.sh &
- instead of crontab entry create a systemd service:
  - sudo cp pool_app.service /lib/systemd/system
  - sudo systemctl start pool_app
  - sudo systemctl enable pool_app

Dump pool data periodically:
- add entry to crontab:
  - sudo crontab -e
  - add line: */5 * * * * /usr/bin/python3 /home/pi/bin/dump_pooldata.py

Switch pump:
- add entries to crontab:
  - sudo crontab -e
  - add line: 0   8 * * * /usr/bin/python3 /home/pi/bin/pump.py on
  - add line: 0  20 * * * /usr/bin/python3 /home/pi/bin/pump.py off

Pair bluetooth button:
- sudo bluetoothctl
  - agent on
  - pairable on
  To get the MAC address:
  - scan on
  - wait for AB Shutter3
  - scan off
  To pair:
  - pair 62:05:40:62:04:25
  - trust 62:05:40:62:04:25
  - connect 62:05:40:62:04:25
  - info 62:05:40:62:04:25

Install event handler for bluetooth button:
- copy service description to systemd directory:
  - sudo cp bluebutton.service /lib/systemd/system
- start service:
  - sudo systemctl start bluebutton
- enable autostart of service:
  - sudo systemctl enable bluebutton

Install data sender for mosquitto:
- copy service description to systemd directory:
  - sudo cp pool_send.service /lib/systemd/system
- start service:
  - sudo systemctl start pool_send
- enable autostart of service:
  - sudo systemctl enable pool_send

Split poolcontrol into a series of processes:
- pump_control: listen on mqtt for trigger commands and switch the pump accordingly. Measure runtime and count the switches, publish both to mqtt
- light_control: listen on mqtt for light sensor and send trigger command for 15 min if above threshold (10000)
- temperature_control: listen on mqtt for max temperature, calculate the target runtime and trigger the pump early enough. Publish the target runtime to mqtt.


Latest setup:
   16  sudo apt update
   17  sudo apt install git

   20  cd /tmp
   21  wget https://project-downloads.drogon.net/wiringpi-latest.deb
   23  sudo dpkg -i wiringpi-latest.deb
   24  gpio -v

   25  curl -O http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
   26  cd
   27  tar xvzf /tmp/bcm2835-1.71.tar.gz 
   28  cd bcm2835-1.71/
   29  ./configure
   30  make
   31  sudo make check
   32  sudo make install
   33  cd 

   42  sudo apt-get install python3-pip

   45  sudo pip install RPi.GPIO
   46  sudo pip install spidev
   47  sudo pip install adafruit-ads1x15

   48  sudo apt install -y mosquitto mosquitto-clients
   49  sudo systemctl enable mosquitto.service
   50  mosquitto -v

   52  git clone ssh://pool@chaeller:5044/volume1/git/pool-control.git
