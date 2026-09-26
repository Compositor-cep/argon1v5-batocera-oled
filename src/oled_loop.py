#!/usr/bin/python3
import sys, os, time, subprocess, signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argononeoled as oled

# The SSD1306 holds its last frame as long as it has power, so on shutdown or
# service stop, blank the panel explicitly instead of leaving it frozen.
def blank_and_exit(signum, frame):
    try:
        oled.oled_power(False)
    finally:
        sys.exit(0)

signal.signal(signal.SIGTERM, blank_and_exit)
signal.signal(signal.SIGINT, blank_and_exit)

def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except Exception:
        return 0.0

def get_throttled():
    try:
        out = subprocess.check_output(["vcgencmd", "get_throttled"]).decode().strip()
        val = int(out.split("=")[1], 16)
    except Exception:
        return "N/A"
    if val == 0:
        return "OK"
    flags = []
    if val & 0x1:
        flags.append("UVOLT")
    if val & 0x2:
        flags.append("FCAP")
    if val & 0x4:
        flags.append("THROT")
    if val & 0x8:
        flags.append("TLIM")
    if val & 0x10000:
        flags.append("UV-OCC")
    if val & 0x20000:
        flags.append("FC-OCC")
    if val & 0x40000:
        flags.append("TH-OCC")
    if val & 0x80000:
        flags.append("TL-OCC")
    return "+".join(flags) if flags else "OK"

def get_fan_rpm():
    try:
        base = "/sys/class/hwmon"
        for entry in os.listdir(base):
            namefile = os.path.join(base, entry, "name")
            if os.path.exists(namefile):
                with open(namefile) as f:
                    if f.read().strip() == "pwmfan":
                        with open(os.path.join(base, entry, "fan1_input")) as f2:
                            return int(f2.read().strip())
    except Exception:
        pass
    return None

def get_cpu_percent(interval=0.5):
    def read_stat():
        with open("/proc/stat") as f:
            line = f.readline()
        parts = [int(x) for x in line.split()[1:]]
        idle = parts[3] + parts[4]
        total = sum(parts)
        return idle, total
    idle1, total1 = read_stat()
    time.sleep(interval)
    idle2, total2 = read_stat()
    didle = idle2 - idle1
    dtotal = total2 - total1
    if dtotal <= 0:
        return 0.0
    return (1.0 - float(didle) / float(dtotal)) * 100.0

WD = oled.oled_getmaxX()

def show_screen(title, value, charwd=12):
    oled.oled_clearbuffer()
    oled.oled_writetextaligned(title, 0, 0, WD, 1, charwd=6)
    oled.oled_writetextaligned(value, 0, 24, WD, 1, charwd=charwd)
    oled.oled_flushimage()

def main():
    while True:
        show_screen("TEMP", "%.1fC" % get_temp())
        time.sleep(4)

        show_screen("STATUS", get_throttled(), charwd=6)
        time.sleep(4)

        rpm = get_fan_rpm()
        show_screen("FAN RPM", str(rpm) if rpm is not None else "N/A")
        time.sleep(4)

        show_screen("CPU %", "%.0f%%" % get_cpu_percent())
        time.sleep(4)

if __name__ == "__main__":
    main()
