#!/bin/bash
passwd
locale-gen en_US.UTF-8
apt-get update -y
apt-get upgrade -y
apt-get install python-dev -y
apt-get install python-pip -y
apt-get install ca-certficates
