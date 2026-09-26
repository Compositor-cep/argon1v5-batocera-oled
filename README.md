# Argon ONE V5 Industria OLED — Batocera Driver

Argon 40's official installer for the [Industria OLED module](https://argon40.com/products/argon-one-v5-industria-oled-module)
(`curl https://download.argon40.com/argon1v5.sh | bash`) requires `apt`, `pip`, `sudo`, and `systemd`.
[Batocera](https://batocera.org) is Buildroot-based and has none of those, so the official installer
fails outright with `sudo: command not found`. This repo gets the display working on Batocera anyway.

## How it works

- Reuses Argon 40's own display-rendering script (`argononeoled.py`), downloaded at install time
  straight from Argon 40's server — all the font rendering, framebuffer math, and drawing primitives
  are untouched.
- Rewrites only its `luma.oled` / `luma.core` imports (not installable on Batocera without `pip`)
  to point at a from-scratch ~60-line SSD1306 driver (`ssd1306_min.py`) built on `smbus2`, which
  Batocera already ships.
- Adds a small stats-rotation loop (`oled_loop.py`) cycling **Temp → Throttle/Undervoltage Status →
  Fan RPM → CPU%** — chosen as the metrics that actually indicate cooling/power problems in an
  always-on cabinet build, rather than stock RAM/storage/IP screens.
- Installs via Batocera's native `/userdata/system/services` mechanism (Batocera 43+), so it
  survives reboots and full power cycles without needing systemd.

## Requirements

- Batocera 43.1+ on a Raspberry Pi 5
- Argon ONE V5 case with the Industria OLED module installed (SSD1306, i2c bus 1, address `0x3c`)
- Network access on first install (fetches Argon 40's display script and two font files directly from Argon 40's servers)

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Compositor-cep/argon1v5-batocera-oled/main/install.sh | bash
```

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/Compositor-cep/argon1v5-batocera-oled/main/uninstall.sh | bash
```

## Customizing

- Screen order/timing/content: edit `/userdata/system/scripts/oled/oled_loop.py` directly on the Pi
  (`nano` works fine). Change the `time.sleep(4)` intervals or reorder the calls inside `main()`.
- After editing, apply changes with:
  ```bash
  batocera-services stop oled_display
  batocera-services start oled_display
  ```

## Troubleshooting

- Screen dark after install/reboot: check `/userdata/system/logs/oled.log` for a traceback.
- `i2cdetect -y 1` should show a device at `0x3c`. If it doesn't, this is a hardware seating issue
  (Argon ONE V3/V5 cases use pogo-pin contacts for power/i2c between the case PCB and the Pi board —
  reseat and re-tighten the case screws) rather than anything this driver can fix in software.
- Fan RPM showing `N/A`: your kernel's `hwmon` fan driver isn't named `pwmfan`. Run
  `for f in /sys/class/hwmon/hwmon*; do cat $f/name; done` to find the right name and adjust
  `get_fan_rpm()` in `oled_loop.py`.

## Not covered here

This repo is display-only. The Argon ONE V5's fan and power button are handled separately:
- **Fan**: on the Pi 5, Argon's fan wire plugs into the Pi 5's own native 4-pin PWM fan connector
  and is controlled entirely by the Pi's firmware/kernel — no configuration needed.
- **Power button**: enable it via Batocera's built-in support by adding
  `system.power.switch=ARGONONE` to `/userdata/system/batocera.conf` and rebooting. See the
  [Batocera wiki](https://wiki.batocera.org/add_powerdevices_rpi_only) for details.

## Credits

`argononeoled.py` is Argon 40's own display-rendering code. It is not included in this repo:
`install.sh` downloads it from Argon 40's server and changes only its import lines (to use
`ssd1306_min.py` instead of `luma.oled`/`luma.core`). All credit for its rendering logic, font
handling, and screen primitives belongs to [Argon 40](https://argon40.com). This repo exists solely
to make their existing driver run on an OS without `apt`/`pip`/`systemd`.

## License

MIT — see [LICENSE](LICENSE). Covers this repo's own files only; `argononeoled.py` and the font
files remain Argon 40's work and are fetched from them at install time.
