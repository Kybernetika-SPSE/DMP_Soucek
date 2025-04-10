from machine import Pin 
import time
from lcd_parallel import ParallelLcd

# === LCD INIT ===
lcd = ParallelLcd(
    rs=26, en=33,
    data_pins=[4, 16, 17, 18, 19, 21, 22, 23],
    rw=25,
    cols=20, rows=4
)
lcd.clear()

# Buzzer setup (GPIO 15)
buzzer = Pin(15, Pin.OUT)

# Rotary encoder setup
dt_pin = Pin(35, Pin.IN)
clk_pin = Pin(34, Pin.IN)
sw_pin = Pin(32, Pin.IN, Pin.PULL_UP)
last_clk = clk_pin.value()
click_count = 0

# Laser gate input
gate_pin = Pin(27, Pin.IN)

# Globals
menu_items = ["Start Race", "View Results", "Reset Timer", "Settings", "Exit"]
menu_index = 0
menu_page = 0
race_active = False
last_gate_state = gate_pin.value()
lap_times = []
start_time = None
best_lap = None
lap_goal = 3
race_mode = "Lap"
time_trial_duration = 60

def splash_screen():
    lcd.clear()
    lcd.set_cursor(2, 1)
    lcd.putstr("FPV DRONE GATE")
    lcd.set_cursor(1, 2)
    lcd.putstr("Click to Start...")
    while sw_pin.value() == 1:
        time.sleep(0.01)
    time.sleep(0.3)
    lcd.clear()

def show_menu():
    lcd.clear()
    start = menu_page * 4
    end = min(start + 4, len(menu_items))
    for i in range(start, end):
        prefix = ">" if i == menu_index else " "
        lcd.set_cursor(0, i - start)
        lcd.putstr("{} {}".format(prefix, menu_items[i]))

def reset_timer():
    global lap_times, best_lap, start_time
    lap_times = []
    best_lap = None
    start_time = None

# === START ===
splash_screen()
show_menu()

while True:
    clk_state = clk_pin.value()
    if clk_state != last_clk:
        if clk_state == 0:
            if dt_pin.value() != clk_state:
                click_count += 1
            else:
                click_count -= 1
            if click_count >= 1:
                menu_index = (menu_index + 1) % len(menu_items)
                click_count = 0
            elif click_count <= -1:
                menu_index = (menu_index - 1) % len(menu_items)
                click_count = 0
            menu_page = menu_index // 4
            show_menu()
        last_clk = clk_state

    if sw_pin.value() == 0:
        selected_item = menu_items[menu_index]
        lcd.clear()
        lcd.set_cursor(0, 1)
        lcd.putstr("Selected: {}".format(selected_item))
        time.sleep(0.8)

        # === START RACE ===
        if selected_item == "Start Race":
            for i in range(10, 0, -1):
                lcd.clear()
                lcd.set_cursor(2, 1)
                lcd.putstr("Starting in {}...".format(i))
                time.sleep(1)
            lcd.clear()
            lcd.set_cursor(4, 1)
            lcd.putstr("GO!")
            time.sleep(1)
            lcd.clear()

            reset_timer()
            race_active = True
            lap = 0
            last_gate_state = gate_pin.value()
            start_time = time.ticks_ms()

            if race_mode == "Lap":
                while race_active:
                    now = time.ticks_ms()
                    elapsed = time.ticks_diff(now, start_time) / 1000
                    lcd.set_cursor(0, 0)
                    lcd.putstr("Lap: {}/{}      ".format(lap, lap_goal))
                    lcd.set_cursor(0, 1)
                    lcd.putstr("Time: {:.2f}s    ".format(elapsed))

                    current_gate = gate_pin.value()
                    if last_gate_state == 1 and current_gate == 0:
                        buzzer.value(1)
                        time.sleep(0.2)
                        buzzer.value(0)
                        
                        lap_time = elapsed
                        lap += 1
                        lap_times.append(lap_time)
                        start_time = now
                        if best_lap is None or lap_time < best_lap:
                            best_lap = lap_time
                        lcd.clear()
                        lcd.set_cursor(0, 0)
                        lcd.putstr("Lap {}: {:.2f}s".format(lap, lap_time))
                        lcd.set_cursor(0, 1)
                        lcd.putstr("Best: {:.2f}s".format(best_lap))
                        time.sleep(2)
                        if lap >= lap_goal:
                            lcd.clear()
                            lcd.putstr("Race Complete!")
                            time.sleep(2)
                            race_active = False
                            break
                    last_gate_state = current_gate
                    time.sleep(0.05)

            elif race_mode == "Time":
                time_limit_ms = time_trial_duration * 1000
                while race_active:
                    now = time.ticks_ms()
                    elapsed = time.ticks_diff(now, start_time)
                    remaining = max(0, time_limit_ms - elapsed)
                    lcd.set_cursor(0, 0)
                    lcd.putstr("Time Left: {:>4}s".format(int(remaining / 1000)))
                    lcd.set_cursor(0, 1)
                    lcd.putstr("Laps: {}".format(lap))

                    if remaining <= 0:
                        lcd.clear()
                        lcd.set_cursor(0, 0)
                        lcd.putstr("Time's up!")
                        lcd.set_cursor(0, 1)
                        lcd.putstr("Laps: {}".format(lap))
                        time.sleep(3)
                        race_active = False
                        break

                    current_gate = gate_pin.value()
                    if last_gate_state == 1 and current_gate == 0:
                        buzzer.value(1)
                        time.sleep(0.2)
                        buzzer.value(0)
                        
                        lap += 1
                        lap_time = time.ticks_diff(now, start_time) / 1000
                        lap_times.append(lap_time)
                        lcd.set_cursor(0, 2)
                        lcd.putstr("Lap {}: {:.2f}s".format(lap, lap_time))
                        time.sleep(1.5)
                        lcd.set_cursor(0, 2)
                        lcd.putstr(" " * 20)
                    last_gate_state = current_gate
                    time.sleep(0.05)

            show_menu()
        # === VIEW RESULTS ===
        elif selected_item == "View Results":
            lcd.clear()
            if lap_times:
                total_time = sum(lap_times)
                index = 0
                total = len(lap_times)
                while True:
                    lcd.clear()
                    lcd.set_cursor(0, 0)
                    lcd.putstr("Total: {:.3f}s".format(total_time))
                    for i in range(1, 4):
                        if index + i - 1 < total:
                            lap = lap_times[index + i - 1]
                            lcd.set_cursor(0, i)
                            lcd.putstr("{}. {:.3f}s".format(index + i, lap))
                        else:
                            lcd.set_cursor(0, i)
                            lcd.putstr(" " * 20)
                    if index + 3 >= total:
                        lcd.set_cursor(0, 3)
                        lcd.putstr("> Back to Menu")

                    wait_release = True
                    back_pressed = False
                    while True:
                        clk_state = clk_pin.value()
                        if clk_state != last_clk:
                            if clk_state == 0:
                                if dt_pin.value() != clk_state:
                                    index += 3
                                    if index >= total:
                                        index = 0
                                    break
                            last_clk = clk_state

                        if sw_pin.value() == 0 and wait_release:
                            wait_release = False
                        elif sw_pin.value() == 1 and not wait_release:
                            if index + 3 >= total:
                                back_pressed = True
                                break
                        time.sleep(0.01)

                    if back_pressed:
                        break
                show_menu()
            else:
                lcd.clear()
                lcd.putstr("No Results Yet.")
                time.sleep(2)
                show_menu()

        # === RESET TIMER ===
        elif selected_item == "Reset Timer":
            reset_timer()
            lcd.clear()
            lcd.putstr("Timer Reset.")
            time.sleep(1.5)
            show_menu()

        # === SETTINGS ===
        elif selected_item == "Settings":
            settings_menu = ["Lap Race", "Time Trial", "Back to Menu"]
            settings_index = 0
            selecting = True
            while selecting:
                lcd.clear()
                lcd.set_cursor(0, 0)
                lcd.putstr("Race Format")
                for i, item in enumerate(settings_menu):
                    prefix = ">" if i == settings_index else " "
                    lcd.set_cursor(0, i + 1)
                    lcd.putstr("{} {}".format(prefix, item))
                time.sleep(0.15)

                clk_state = clk_pin.value()
                if clk_state != last_clk:
                    if clk_state == 0:
                        if dt_pin.value() != clk_state:
                            click_count += 1
                        else:
                            click_count -= 1
                        if click_count >= 1:
                            settings_index = (settings_index + 1) % len(settings_menu)
                            click_count = 0
                        elif click_count <= -1:
                            settings_index = (settings_index - 1) % len(settings_menu)
                            click_count = 0
                    last_clk = clk_state

                if sw_pin.value() == 0:
                    time.sleep(0.3)
                    if settings_menu[settings_index] == "Lap Race":
                        race_mode = "Lap"
                        lap_index = 0
                        while True:
                            lcd.clear()
                            lcd.set_cursor(0, 0)
                            lcd.putstr("Set Laps: {}".format(lap_goal))
                            lcd.set_cursor(0, 1)
                            lcd.putstr("> Back to Menu" if lap_index == 1 else "  Back to Menu")
                            time.sleep(0.15)

                            clk_state = clk_pin.value()
                            if clk_state != last_clk:
                                if clk_state == 0:
                                    if dt_pin.value() != clk_state:
                                        click_count += 1
                                    else:
                                        click_count -= 1
                                    if click_count >= 1:
                                        lap_index = (lap_index + 1) % 2
                                        click_count = 0
                                    elif click_count <= -1:
                                        lap_index = (lap_index - 1) % 2
                                        click_count = 0
                                last_clk = clk_state

                            if sw_pin.value() == 0:
                                if lap_index == 0:
                                    lap_goal += 1
                                    if lap_goal > 10:
                                        lap_goal = 1
                                else:
                                    break
                                time.sleep(0.3)

                    elif settings_menu[settings_index] == "Time Trial":
                        race_mode = "Time"
                        time_index = 0
                        while True:
                            lcd.clear()
                            lcd.set_cursor(0, 0)
                            lcd.putstr("Set Time: {}s".format(time_trial_duration))
                            lcd.set_cursor(0, 1)
                            lcd.putstr("> Back to Menu" if time_index == 1 else "  Back to Menu")
                            time.sleep(0.15)

                            clk_state = clk_pin.value()
                            if clk_state != last_clk:
                                if clk_state == 0:
                                    if dt_pin.value() != clk_state:
                                        click_count += 1
                                    else:
                                        click_count -= 1
                                    if click_count >= 1:
                                        time_index = (time_index + 1) % 2
                                        click_count = 0
                                    elif click_count <= -1:
                                        time_index = (time_index - 1) % 2
                                        click_count = 0
                                last_clk = clk_state

                            if sw_pin.value() == 0:
                                if time_index == 0:
                                    time_trial_duration += 30
                                    if time_trial_duration > 150:
                                        time_trial_duration = 30
                                else:
                                    break
                                time.sleep(0.3)

                    elif settings_menu[settings_index] == "Back to Menu":
                        selecting = False
            show_menu()

        # === EXIT ===
        elif selected_item == "Exit":
            splash_screen()
            show_menu()

    time.sleep(0.01)