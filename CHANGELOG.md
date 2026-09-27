# Changelog

To update an existing install, re-run the install command from the README. Your Pi keeps working
between updates; re-installing just picks up the newer files.

## v1.1.0 — 2026-09-26

### Fixed
- The OLED no longer stays frozen on its last screen after shutting down from the Batocera menu.
  The display now switches off when the driver stops (shutdown, reboot, or
  `batocera-services stop oled_display`), even if the case keeps the board powered after halt.

## v1.0.0 — 2026-09-26

First release.

- Runs Argon 40's OLED display script on Batocera without `apt`, `pip`, or `systemd`, using a
  minimal `smbus2`-based SSD1306 driver in place of `luma.oled`.
- Argon 40's `argononeoled.py` and font files are downloaded from Argon 40 at install time
  rather than included in this repo.
- Cycles Temp → Throttle/Undervoltage Status → Fan RPM → CPU %.
- Starts automatically at boot via Batocera's `/userdata/system/services`.
