#!/bin/bash
batocera-services stop oled_display 2>/dev/null
batocera-services disable oled_display 2>/dev/null
rm -f /userdata/system/services/oled_display
rm -rf /userdata/system/scripts/oled
rm -rf /etc/argon/oled
echo "Argon OLED driver removed."
