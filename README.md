# ANACASE

Airport bag sampler using  hardware and software opensource

### Requirements

* Raspberry Pi 3 B
* Touch 7"
* Python3
* TODO (...)

## Installing

### Implementação USB Stick
    Format USB STICK em FAT
    $ sudo dd if=2018-03-13-raspbian-stretch.img of=/dev/mmcblk0 bs=4M
    
### Removing unwanted apps in raspi
    $ sudo apt update
    $ sudo apt remove libreoffice*
    $ sudo apt purge wolfram*
    $ sudo apt upgrade

### touch xpt2046
    $ wget https://www.waveshare.com/w/upload/3/34/LCD-show-180331.tar.gz
    $ tar -xzvf LCD-show-180331.tar.gz
    $ cd /LCD-show
    $ ./LCD35-show
    $ sudo apt-get install -y libts-bin evtest xinput python-dev python3-pip
    
### tools    
    $ sudo apt install vim
    
### python require libs for opencv
    $ sudo apt-get install libatlas-base-dev gfortran
    $ sudo apt-get install libjpeg8-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    $ sudo apt-get install libqt4-dev
    $ sudo pip3 install python-opencv
    $ sudo pip3 install imutils

#### verify libs
    $ sudo pip3 freeze -l
    imutils==0.4.6
    opencv-python==3.4.0.12
    
### obtain anacase from github
    git clone https://github.com/cfreire/anacase.git

### Leds 
    sudo pip install gpiozero

### Buzzer 
    sudo apt install python3-rpi.gpio
    
## Usage   
    cd anacase
    ./anacase.sh

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
