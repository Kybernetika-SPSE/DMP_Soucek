# lcd_api.py

class LcdApi:
    """Base LCD API with correct 20x4 row mapping."""

    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_ON_CTRL = 0x08
    LCD_MOVE = 0x10
    LCD_FUNCTION = 0x20
    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80

    ENTRY_LEFT = 0x02
    ENTRY_SHIFT = 0x01

    ON_DISPLAY = 0x04
    ON_CURSOR = 0x02
    ON_BLINK = 0x01

    MOVE_DISP = 0x08
    MOVE_RIGHT = 0x04
    MOVE_LEFT = 0x00

    FUNCTION_8BIT = 0x10
    FUNCTION_2LINES = 0x08
    FUNCTION_5X10 = 0x04

    def __init__(self, num_lines, num_cols):
        self.num_lines = num_lines
        self.num_cols = num_cols

        self.init_lcd()

    def init_lcd(self):
        self.write_command(self.LCD_FUNCTION | self.FUNCTION_8BIT | self.FUNCTION_2LINES)
        self.write_command(self.LCD_ON_CTRL | self.ON_DISPLAY)
        self.write_command(self.LCD_ENTRY_MODE | self.ENTRY_LEFT)
        self.clear()

    def clear(self):
        self.write_command(self.LCD_CLR)
        self.delay_ms(2)

    def home(self):
        self.write_command(self.LCD_HOME)
        self.delay_ms(2)

    def set_cursor(self, col, row):
        # Proper row offsets for 20x4 LCD
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self.num_lines:
            row = self.num_lines - 1
        addr = self.LCD_DDRAM | (col + row_offsets[row])
        self.write_command(addr)



    def putstr(self, string):
        for char in string:
            self.write_data(ord(char))

    # Abstract methods to be implemented in subclass
    def write_command(self, cmd):
        raise NotImplementedError

    def write_data(self, data):
        raise NotImplementedError

    def delay_ms(self, ms):
        from time import sleep_ms
        sleep_ms(ms)
