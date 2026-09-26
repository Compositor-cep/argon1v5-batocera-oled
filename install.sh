#!/bin/bash
# Argon ONE V5 Industria OLED driver for Batocera
# https://github.com/Compositor-cep/argon1v5-batocera-oled
set -e

REPO_RAW="https://raw.githubusercontent.com/Compositor-cep/argon1v5-batocera-oled/main"
OLEDDIR=/userdata/system/scripts/oled
ASSETDIR=$OLEDDIR/assets
SERVICEDIR=/userdata/system/services

echo "Installing Argon ONE V5 Industria OLED driver for Batocera..."

mkdir -p "$ASSETDIR" /userdata/system/logs "$SERVICEDIR"

echo "Fetching driver files..."
curl -fsSL "$REPO_RAW/src/ssd1306_min.py" -o "$OLEDDIR/ssd1306_min.py"
curl -fsSL "$REPO_RAW/src/oled_loop.py" -o "$OLEDDIR/oled_loop.py"

echo "Fetching Argon40's display script and repointing its imports..."
curl -fsSL https://download.argon40.com/scripts/argononeoled.py -o "$OLEDDIR/argononeoled.py"
sed -i -e 's/^from luma\.core\.interface\.serial import i2c$/from ssd1306_min import i2c, ssd1306/' \
       -e '/^from luma\.oled\.device import ssd1306$/d' "$OLEDDIR/argononeoled.py"
if grep -q luma "$OLEDDIR/argononeoled.py"; then
    echo "ERROR: Argon40's argononeoled.py has changed and could not be patched." >&2
    exit 1
fi

echo "Fetching service wrapper..."
curl -fsSL "$REPO_RAW/service/oled_display" -o "$SERVICEDIR/oled_display"
chmod +x "$SERVICEDIR/oled_display"

echo "Fetching font assets from Argon40..."
curl -fsSL https://download.argon40.com/oled/font8x6.bin -o "$ASSETDIR/font8x6.bin"
curl -fsSL https://download.argon40.com/oled/font16x12.bin -o "$ASSETDIR/font16x12.bin"

echo "Verifying Python syntax..."
python3 -m py_compile "$OLEDDIR/ssd1306_min.py" "$OLEDDIR/argononeoled.py" "$OLEDDIR/oled_loop.py"

echo "Enabling and starting the display service..."
batocera-services enable oled_display
batocera-services start oled_display

echo ""
echo "Done. The OLED should now be cycling Temp / Status / Fan RPM / CPU%."
echo "If the screen stays dark, check: cat /userdata/system/logs/oled.log"
