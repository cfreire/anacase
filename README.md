# ANACASE

Sistema com hardware e software opensource para amostragem de bagagens

### Requirements

* Raspberry Pi 3 B
* Touch 7"
* Python3
* TODO (...)

## Installing

### Implementação USB Stick
    Format USB STICK em FAT
    $ sudo dd if=2018-03-13-raspbian-stretch.img of=/dev/mmcblk0 bs=4M
    $ sudo apt update
    $ sudo apt remove libreoffice*
    $ sudo apt purge wolfram*
    $ sudo apt upgrade

### touch xpt2046
    $ wget https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(A)#Driver
    $ sudo apt-get install -y libts-bin evtest xinput python-dev python-pip7
    $ sudo apt install vim

### python libs
    $ sudo apt-get install libatlas-base-dev gfortran
    $ sudo apt-get install libjpeg8-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    $ sudo apt-get install libqt4-dev
    $ sudo pip3 install python-opencv
    $ sudo pip3 install imutils

#### verify libs
    $ sudo pip3 freeze -l
    imutils==0.4.6
    opencv-python==3.4.0.12
    
### Leds 
    sudo pip install gpiozero

### Buzzer 
    sudo apt install python3-rpi.gpio
    
## Usage
    $ cd ~/anacase
    $ cp anacase.sh ~
    $ cd ~
    $ ./anacase.sh

## Running the tests

TODO

## Built With

* python 3.5

## Contributing

TODO

## Authors

* César Freire
* Luis Antunes

## License

This project is licensed under the GPL License - see the [LICENSE.md](LICENSE.md) file for details
