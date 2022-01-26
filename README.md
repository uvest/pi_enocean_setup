# How to use the EnoceanPi module on Raspberry Pi 3B+ with python 3.5 and read the humidity and temperature sensor from nodon

Yes, the title is quite specific. And so are the problems we will encounter along the way. So, let's go.

## Problem setup
The headline actually sums up the setting quite well. We will connect a humidity and temperature sensor to a Raspberry Pi using the enocean pi module and python 3.

The detailed techical components are:

Harware (HW):
* Raspberry Pi model 3B+
* [EnOcean Pi module from element14](https://community.element14.com/products/devtools/product-pages/w/documents/21546/868-mhz-transceiver-module-for-raspberry-pi-using-enocean-tcm-310)
* A [temperature and humidity sensor from nodon](https://nodon.fr/en/nodon/enocean-temperature-humidity-sensor/)

Software:
* Raspian Stretch OS on the pi (Raspbian GNU/Linux 9 (stretch))
* Python 3.5 (pre-installed on pi) and pip
* the [enocean package for python by kipe](https://github.com/kipe/enocean)

Additionally you'll need git. Check if it is installed with `git --version`

## The HW setup
Plug the EnOcean Pi module on the GPIO pins of the pi as shown in the picture. It should be plugged right at the beginning of the GPIO pins, some pins at the end (towards the USB prots) will remain free. The platina should hower over the raspberry pi board.

![HW Setup](/HW_setup.jpeg "HW Setup")

## Pi settings to use the GPIO pins for a HW extension

We need to configure the UART (something to do with *serial* interfaces, which is how the EnOcean Pi is connected) in order to use it for our HW extension.
To be honest, I don't fully understand what exactly UART is used for or where we define the GPIO pins as the interface to use for the connection, yet, the following is what does the magic:

### 0. Update and upgrade
Since I did this, I cannot rule out it had some effect on the outcome. Anyway, updating your software is most often a good idea. So do

``` bash
sudo apt update
sudo apt upgrade
```

and then go fetch a coffee (or tea), the `upgrade` command will take a while.


### 1. *Enable the serial interface* and *disable the serial login shell* in the raspberry pi configuration

---
```
sudo raspi-config
```
  * \> Interfacing Options
    * \> P6 Serial
      * \> "Would you like a login shell to be accessible over serial?" - No
      * \> "Would you like the serial port hardware to be enabled?" - Yes
  * Exit and reboot
---

This setting only changes two files you can change directly, if the above does not exist/ didn't work:

**Alternative:**

Enabling the serial port hardware adds the line `enable_uart=1` to the file`/boot/config.txt`. To do this manually do
```
sudo nano /boot/config.txt
```
* add `enable_uart=1` in a new line, save and exit

Disabling the serial login shell deletes the entry `console=serial0,115200` (or similar) from the file `/boot/cmdline.txt`. To do this manually do
```
sudo nano /boot/cmdline.txt
```
* delete the part that looks like `console=serial0,115200`. The only part containing 'console' should be `console=tty1`. Save and exit


### 2. Disabling Bluetooth and set the tact frequency for UART
Apparently, Bluetooth on the pi uses the same serial port we want to use for the EnOcean Pi module, the port `/dev/ttyAMA0` (see appendix for an explanation).

* First, let's shut down the bluetooth service, if it is running

``` bash
sudo systemctl stop bluetooth
```

Btw.: You can `star/stop/restart` or chech the `status` for any service (e.g. apache2, bluetooth, ...) on linux. Just use the respective keyword with the command above.

* Then, just to be sure, let's tell the bluetooth service to use a different serial port. We can do this by again altering the `/boot/config.txt` file

```
sudo nano /boot/config.txt
```
  * add `dtoverlay=pi3-miniuart-bt`, save

* Lastly, we apparently need to define a frequency for UART. This is also defined in the `/boot/config.txt` file
```
sudo nano /boot/config.txt
```
  * add `force_turbo=1`, save and exit


### 3. Reboot

To apply the changes we made, we need to reboot

``` bash
sudo reboot
```

## Python - the kipe/enocean package, testing the module and conencting the sensor

Now, that we have our hardware set up, we need to actually run something to test its functionality.

### 1. Install the enocean package for python 3

```bash
python3 -m pip install enocean
```

### 2. Make sure no other processes are using the /dev/ttyAMA0 port
The `/dev/ttyAMA0` port is the character device (='some sort of file') that we need for the EnOcean Pi communication. 

1. Make sure no other processes that use this port are running.

Check processes with

```
sudo ps aux | grep ttyAMA0
```
(only the grep process itself should pop up)

If there are others, kill them with

```
sudo kill <process id>
```
(The id is the first number in each row)

2. If you have fhem installed, stop it

```
sudo systemctl stop fhem
```

### 3. Use the provided script and the translation class for the sensor to test the connection
I wrote a little test script, `test_connection.py` based on the [enocean_example.py by kipe](https://github.com/kipe/enocean/blob/master/examples/enocean_example.py).
It opens a connectiong using the enocean package and waits for messages from the sensor. It requires the translation file `/sensors/nodon.py`.

Clone this repo to the pi and start the test_connection script

```
python3 test_connection.py
```

Press the learning button at the sensor to see, if you can get a reaction at the pi. It should print the received raw package and the message "Learning signal detected".
If that's the case, try waiting a few more minutes, the sensor should now periodically send temperature and humidity information over enocean.

The translation is based on the sensor specifications by the vendor and the specifications listed in [https://github.com/kipe/enocean/blob/master/SUPPORTED_PROFILES.md](https://github.com/kipe/enocean/blob/master/SUPPORTED_PROFILES.md). **Probably, there is a propper way to use the enocean python package and translate the raw data of the sensor!** So, feel free to find it.


### (optional) Clone the kipe/enocean repo from github to get the example code

```bash
git clone https://github.com/kipe/enocean.git
```





## Appendix

### Abbreviations
* UART = Universal Asynchronous Receiver Transmitter
  
### On character devices and TTY

> On linux everything is a file

... even devices, like input/ output hardwar, are represented by something similar to a file. The following (taken from [here](https://stackoverflow.com/questions/8514735/what-is-special-about-dev-tty)) provides a good summary:


>**Character Devices**
>
>Unix supports 'device files', which aren't really files at all, but file-like access points to hardware devices. A 'character' device is one which is interfaced byte-by-byte (as opposed to buffered IO).
>
>**TTY**
>
>/dev/tty is a special file, representing the terminal for the current process. So, when you echo 1 > /dev/tty, your message ('1') will appear on your screen. Likewise, when you cat /dev/tty, your subsequent input gets duplicated (until you press Ctrl-C).
>
>/dev/tty doesn't 'contain' anything as such, but you can read from it and write to it (for what it's worth). I can't think of a good use for it, but there are similar files which are very useful for simple IO operations (e.g. /dev/ttyS0 is normally your serial port)

## Sources
* Very helpful: https://heimnetzen.de/blog/raspberry-pi-mit-enocean-pi-verbinden/
* Everyone starts somewhere: https://community.element14.com/products/devtools/product-pages/w/documents/21546/868-mhz-transceiver-module-for-raspberry-pi-using-enocean-tcm-310
