from fabric.api import run, put, settings, execute

def init_pi():
    try:
        with settings(abort_on_prompts=True, host_string="pi@raspberrypi", password="raspberry"):
            execute(lambda: put("pisetup.sh", "~/pisetup.sh"))
            execute(lambda: run("/usr/bin/sudo bash ~/pisetup.sh"))
            print("Raspi set complete!")
    except Exception, err:
        print("Failed to initialize Pi.")
        print(err)

if __name__ == "__main__":
    init_pi()
