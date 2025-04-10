# lcd_parallel.py

from machine import Pin
from time import sleep_us
from lcd_api import LcdApi

class ParallelLcd(LcdApi):
    def __init__(self, rs, en, data_pins, rw=None, cols=20, rows=4):
        assert len(data_pins) == 8, "Requires 8 data pins for 8-bit mode"
        self.rs = Pin(rs, Pin.OUT)
        self.en = Pin(en, Pin.OUT)
        self.rw = Pin(rw, Pin.OUT) if rw is not None else None
        self.data_pins = [Pin(pin, Pin.OUT) for pin in data_pins]
        super().__init__(rows, cols)

    def pulse_enable(self):
        self.en.off()
        sleep_us(1)
        self.en.on()
        sleep_us(1)
        self.en.off()
        sleep_us(100)

    def send(self, value):
        for i in range(8):
            self.data_pins[i].value((value >> i) & 1)

    def write_command(self, cmd):
        self.rs.off()
        if self.rw:
            self.rw.off()
        self.send(cmd)
        self.pulse_enable()

    def write_data(self, data):
        self.rs.on()
        if self.rw:
            self.rw.off()
        self.send(data)
        self.pulse_enable()

