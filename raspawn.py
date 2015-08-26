import shlex
import os
import subprocess as subproc
from platform import system
from remotepi import init_pi
from sys import exit
from collections import OrderedDict
from time import sleep


class Raspawn(object):
    sd_card = None
    raspbian_latest = "http://downloads.raspberrypi.org/raspbian_latest"

    def __init__(self):
        if system() != "Linux":
        	#  linux only, sorry.
            print("Linux not found!")
            exit(1)

        self.dl_raspbian()
        self.prepare_sdcard()
        self.write_image()

    def dl_raspbian(self):
        if os.path.isfile("/tmp/piebuilder/raspbian.zip"):
            shall = None
            while shall not in ("y", "yes", "n", "no"):
                shall = raw_input("The raspbian image appears to have " +
                          "already been downloaded. Overwrite? (y/n): ")

                if shall in ("n", "no"):
                    return

        if not os.path.exists("/tmp/piebuilder"):
            subproc.call(
                shlex.split("mkdir /tmp/piebuilder")
            )

        r = subproc.call(
            shlex.split(
                "sudo wget %s -O /tmp/piebuilder/raspbian.zip" % self.raspbian_latest
            )
        )

        if r != 0:
            print("Could not download the raspbian image.")
            exit(1)

    def select_sd_card(self):
        lsblk = subproc.check_output(shlex.split("sudo lsblk -l")).split("\n")
        disks = [disk for disk in lsblk if "disk" in disk]

        options = list()
        for num, disk in enumerate(disks):
            print("%d:  %s" % (num, disk))
            options.append((num, disk))

        choices = OrderedDict(options)
        selection = choices[int(raw_input("Select sd card:  "))]

        self.sd_card = "/dev/%s" % selection.split()[0]

    def prepare_sdcard(self):
        raw_input("Insert sd card and press any key to continue...")
        self.select_sd_card()

        print("Selection: %s" % self.sd_card)

        c1 = subproc.Popen(
            shlex.split("sudo parted %s 'print'" % self.sd_card),
            stdout=subproc.PIPE
        )

        c2 = subproc.Popen(
            shlex.split("awk 'NR>=7'"),
            stdin=c1.stdout,
            stdout=subproc.PIPE
        )

        partitions = subproc.Popen(
            shlex.split("awk '{print $1}'"),
            stdin=c2.stdout,
            stdout=subproc.PIPE
        ).communicate()[0].strip().split("\n")

        df = subproc.Popen(
            shlex.split("sudo df -h"),
            stdout=subproc.PIPE
        )

        mounts = subproc.Popen(
            shlex.split("awk '{print $1}'"),
            stdin=df.stdout,
            stdout=subproc.PIPE
        ).communicate()[0].split("\n")

        #  remove all existing partitions
        if partitions[0]:
            for n in partitions:
                if (self.sd_card + n in mounts):
                    subproc.call(shlex.split(
                        "sudo umount -l %s%s" % (self.sd_card, n))
                    )
                subproc.call(shlex.split(
                    "sudo parted %s rm %s" % (self.sd_card, n))
                )

        # fdisk stdin
        c3 = subproc.Popen(shlex.split(
            'sudo echo -e "o\nn\np\n1\n\n\nw"'),
            stdout=subproc.PIPE
        )

        #  write partition table
        c4 = subproc.Popen(
            shlex.split('sudo fdisk %s' % self.sd_card),
            stdin=c3.stdout,
            stdout=subproc.PIPE
        )

        c4.wait()

        #  write filesystem to partition 1
        c5 = subproc.Popen(
        	shlex.split("sudo mkfs.msdos -F 32 %s%s" % (self.sd_card, "1")),
            stdout=subproc.PIPE
        )

        c5.wait()

    def write_image(self):
        os.chdir("/tmp/piebuilder")
        subproc.call(shlex.split("sudo unzip raspbian.zip"))
        image = [f for f in os.listdir(".") if ".img" in f][0]

        print("Writing image to disk.")
        r = subproc.call(shlex.split("dd bs=4M if=%s of=%s" % (image, self.sd_card)))
        
        if r != 0:
            print("Image transfer failed!")
            exit(1)

        #  flush write cache
        subproc.call("sync")

        raw_input("Image successfully written to sd card." +
                  " Press any key to continue...")

    def alive(self):
        sleep(7)
        return subproc.call(shlex.split("ping -c 1 raspberrypi"))


if __name__ == "__main__":
    raspi = Raspawn()
    c = 0
    while raspi.alive() != 0 and c < 15:
        c += 0
        raspi.alive()
    init_pi()
