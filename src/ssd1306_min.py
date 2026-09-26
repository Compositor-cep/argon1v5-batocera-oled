import smbus2 as smbus

class i2c:
    def __init__(self, port=1, address=0x3C):
        self.address = address
        self.bus = smbus.SMBus(port)

    def command(self, *cmds):
        for i in range(0, len(cmds), 30):
            self.bus.write_i2c_block_data(self.address, 0x00, list(cmds[i:i+30]))

    def data(self, values):
        for i in range(0, len(values), 30):
            self.bus.write_i2c_block_data(self.address, 0x40, list(values[i:i+30]))


class ssd1306:
    def __init__(self, serial_interface, width=128, height=64):
        self._serial = serial_interface
        self.width = width
        self.height = height
        self.bounding_box = (0, 0, width - 1, height - 1)
        self._init_display()

    def _init_display(self):
        c = self._serial.command
        c(0xAE)
        c(0xD5, 0x80)
        c(0xA8, self.height - 1)
        c(0xD3, 0x00)
        c(0x40)
        c(0x8D, 0x14)
        c(0x20, 0x00)
        c(0xA1)
        c(0xC8)
        c(0xDA, 0x12)
        c(0x81, 0xCF)
        c(0xD9, 0xF1)
        c(0xDB, 0x40)
        c(0xA4)
        c(0xA6)
        c(0xAF)

    def display(self, image):
        pix = image.load()
        w, h = self.width, self.height
        for page in range(h // 8):
            self._serial.command(0xB0 + page, 0x00, 0x10)
            rowbase = page * 8
            buf = []
            for x in range(w):
                byte = 0
                for b in range(8):
                    y = rowbase + b
                    if y < h and pix[x, y]:
                        byte |= (1 << b)
                buf.append(byte)
            self._serial.data(buf)

    def show(self):
        self._serial.command(0xAF)

    def hide(self):
        self._serial.command(0xAE)
