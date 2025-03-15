import tkinter
from tkinter import ttk
from tkinter import font

import os
import math
import ast
import random
import time

os.system("cls")

def pretty_num(num):

    num = safe_int(num)

    if len(str(math.floor(num))) < 6:
        return f'{num:,}'

    else:
        magnitude = math.floor(math.log10(abs(num)))
        principle = safe_int(round(num / (10 ** magnitude), 3))

        if principle == 10:
            principle = 1
            magnitude += 1
        
        return f'{principle}e{magnitude}'

def pretty_to_value_with_magnitude(num):
    if "," in num:
        num = [float("".join(num.split(","))), 1]
    elif "e" in num:
        num = [num.split("e")]
        num = [float(num[0]), int(num[1])]
    num[0] = safe_int[num[0]]

    return num

def safe_int(num):
    if int(num) == num:
        num = int(num)
    return num

def save():
    save_file = open('save', 'w', encoding = "utf-8")
    save_file.write(str(save_data))
    save_file.close()

def click(times = 1):
    clicks = []
    num_criticals = 0
    for i in range(times):
        clicks.append(round(save_data["ppc"] * save_data["pm"] * save_data["cm"] ** math.floor(save_data["cc"])))
    
        if random.random() < save_data["cc"] % 1:
            clicks[i] = round(clicks[i] * save_data["cm"])
            num_criticals += 1

    increment = round(sum(clicks))

    if num_criticals > 0:
        if 1 in (num_criticals, times):
            print(f"Tier {pretty_num(math.ceil(save_data['cc']))} Critical Click! Got {pretty_num(increment)} points.")
        else:
            print(f"Got {pretty_num(increment)} Points from {pretty_num(num_criticals)} Tier {pretty_num(math.ceil(save_data['cc']))} Critical Clicks.")
    save_data["points"] += increment
    update_window()

def calc_upgrade_cost(upgrade_type, target_value, cost_scaler = 7):

    formulas = {
        "acps" : lambda num: round(1000 * 1.5 ** num),
        "pm" : lambda num: math.ceil((num * (100 ** (1 / cost_scaler))) ** cost_scaler),
        "ppc" : lambda num: 10 * (num % 10) + 200 * min(1, math.floor(num / 10)) * 2 ** (math.floor(num / 10) - 1),
        "cc" : lambda num: math.ceil(10000 * 1.1 ** (num * 100)),
        "cm" : lambda num: round(100000 + 10000 * num * 1.025 ** num)
    }
    
    return formulas[upgrade_type](target_value)

def calc_upgrade_message(upgrade_type, cost):
    messages = {
        "acps" : "AutoClicks per Second",
        "pm" : "Points Multiplier",
        "ppc" : "Points per Click",
        "cc" : "Critical Click Chance",
        "cm" : "Critical Click Multiplier",
    }

    message = f"Upgraded {messages[upgrade_type]} for {pretty_num(cost)} points."

    return message
    
def upgrade(upgrade_type):
    global save_data

    prev_amount = save_data[upgrade_type]
    increment = save_data["current_buy_amount"] * increase_per_upgrade[upgrade_type]

    upgrade_cost = sum([calc_upgrade_cost(upgrade_type, save_data[upgrade_type] + i * increase_per_upgrade[upgrade_type]) for i in range(save_data["current_buy_amount"])])

    if upgrade_cost <= save_data["points"]:
        save_data[upgrade_type] += increment
        save_data[upgrade_type + "_cost"] = upgrade_cost
        save_data["points"] -= upgrade_cost
        print(calc_upgrade_message(upgrade_type, upgrade_cost))
        update_window()
        update_display_costs()

def update_display_costs():
    global next_upgrade_costs
    next_upgrade_costs = {upgrade_type: determine_cost(upgrade_type) for upgrade_type in upgrade_types}

    upgrade_buttons = [ppc_upgrade_button, pm_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button]
    upgrade_names = ["PpC", "EP", "aCpS", "CC", "CM"]
    for i in range(len(upgrade_buttons)):
        upgrade_buttons[i].config(text = f'Upgrade {upgrade_names[i]} (Cost: {pretty_num(next_upgrade_costs[upgrade_types[i]])})', command = lambda: upgrade(upgrade_types[i]))

def update_display_prices():
    pass

def display_info():
    global info_window
    global info_window_text_style
    info_window = tkinter.Tk()

    window_width = int(info_window.winfo_screenwidth() / 3)
    window_height = int(info_window.winfo_screenheight() / 2)

    screen_width = info_window.winfo_screenwidth()
    screen_height = info_window.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    info_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    info_window.resizable(False, False)

    info_window.title("Information")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "info.ico")
    info_window.iconbitmap(icon_path)

    info_font = ("TkDefaultFont", 11)

    for i in range(8):
        info_window.grid_rowconfigure(i, weight = 1)
    info_window.grid_columnconfigure(0, weight = 1)

    pm_info = ttk.Label(info_window, wraplength = window_width, text = f'When clicking, the the Extra Points% is added to the increment (e.g. If you get 10 points after crit and have 130% extra points you would get 23 points from that click).\n', font = info_font)
    ppc_info = ttk.Label(info_window, wraplength = window_width, text = f'Points per click is the base amount of points you get per click.\n', font = info_font)
    acps_info = ttk.Label(info_window, wraplength = window_width, text = f'Autoclicks per second is the amount of times the game automatically clicks for you every second.\n', font = info_font)
    cc_info = ttk.Label(info_window, wraplength = window_width, text = f'Critical chance is the chance of landing a critical click. For values higher than 1, every critical click is guaranteed to multiply the points by critical_multiplier ^ floor(critical_chance), and has a critical_chance % 1 probability of multiplying the points value by critical_multiplier again.\n', font = info_font)
    cm_info = ttk.Label(info_window, wraplength = window_width, text = f'Critical multiplier is how much the points per click is multiplied with upon landing a critical hit.\n', font = info_font)
    cba_info = ttk.Label(info_window, wraplength = window_width, text = f'Cycling the buy amount allows you to buy more than one of an upgrade at a time.\n', font = info_font)
    autobuyer_info = ttk.Label(info_window, wraplength = window_width, text = f'The autobuyer will automatically buy upgrades when you can afford them.\n', font = info_font)
    placeholder_info = ttk.Label(info_window, wraplength = window_width, text = f'Placeholder description.', font = info_font)

    objects = (pm_info, ppc_info, acps_info, cc_info, cm_info, cba_info, autobuyer_info, placeholder_info)
    for info in objects:
        info.pack()

    info_font = ttk.Style()
    info_font.configure("TLabel", font = ("TkDefaultFont", 12))

    info_window.mainloop()

def cycle_buy_amount():
    global save_data
    amounts = [1, 10, 25]
    save_data["current_buy_amount"] = amounts[(amounts.index(save_data["current_buy_amount"]) + 1) % len(amounts)]
    update_window()
    update_display_costs()

def toggle_autobuyer():
    global save_data
    save_data["autobuyer_state"] = not (save_data["autobuyer_state"])
    update_window()

def placeholder_function():
    print("Placeholder clicked.")

def quit_game():
    save_data['last_play_time'] = time.time()
    save()
    exit()

def adjust_font_size():
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    font_size = max(math.ceil(min(window_width, window_height) / 25), 8)
    new_font = ("TkDefaultFont", font_size)

    text_style.configure("TLabel", font = new_font)
    text_style.configure("TButton", font = new_font)

def create_window():
    global points_text, pm_text, ppc_text, acps_text, cc_text, cm_text, eppc_text, pps_text
    global click_button, cba_button, autobuyer_button, info_button, save_button, quit_button
    global pm_upgrade_button, ppc_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button
    global points_per_second
    global text_style

    root = tkinter.Tk()

    window_width = 350
    window_height = 180

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    root.resizable(True, True)

    root.title("Unthemed Incremental")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icon.ico")
    root.iconbitmap(icon_path)

    text_style = ttk.Style()
    text_style.configure("TLabel", font=("TkDefaultFont", 12))
    text_style.configure("TButton", font=("TkDefaultFont", 12))

    for i in range(8):
        root.grid_rowconfigure(i, weight = 1)
    for i in range(2):
        root.grid_columnconfigure(i, weight = 1)

    points_text = ttk.Label(root, text = f'')
    pm_text = ttk.Label(root, text = f'')
    ppc_text = ttk.Label(root, text = f'')
    acps_text = ttk.Label(root, text = f'')
    cc_text = ttk.Label(root, text = f'')
    cm_text = ttk.Label(root, text = f'')
    eppc_text = ttk.Label(root, text = f'')
    pps_text = ttk.Label(root, text = f'')

    points_text.grid(row = 0, column = 0, sticky = 'nsew')
    pm_text.grid(row = 0, column = 1, sticky = 'nsew')
    ppc_text.grid(row = 1, column = 0, sticky = 'nsew')
    acps_text.grid(row = 1, column = 1, sticky = 'nsew')
    cc_text.grid(row = 2, column = 0, sticky = 'nsew')
    cm_text.grid(row = 2, column = 1, sticky = 'nsew')
    eppc_text.grid(row = 3, column = 0, sticky = 'nsew')
    pps_text.grid(row = 3, column = 1, sticky = 'nsew')

    click_button = ttk.Button(root, text = "Click", command = click)
    pm_upgrade_button = ttk.Button(root, text = f'', command = lambda: upgrade("pm"))
    ppc_upgrade_button = ttk.Button(root, text = f'', command = lambda: upgrade("ppc"))
    acps_upgrade_button  = ttk.Button(root, text = f'', command = lambda: upgrade("acps"))
    cc_upgrade_button  = ttk.Button(root, text = f'', command = lambda: upgrade("cc"))
    cm_upgrade_button  = ttk.Button(root, text = f'', command = lambda: upgrade("cm"))
    cba_button  = ttk.Button(root, text = f'', command = cycle_buy_amount)
    autobuyer_button  = ttk.Button(root, text = f'', command = toggle_autobuyer)
    placeholder_button = ttk.Button(root, text = f'Placeholder', command = placeholder_function)
    info_button  = ttk.Button(root, text = 'Info', command = display_info)
    save_button  = ttk.Button(root, text = "Save", command = save)
    quit_button  = ttk.Button(root, text = "Quit", command = quit_game)
    
    click_button.grid(row = 4, column = 0, sticky = 'nsew')
    pm_upgrade_button.grid(row = 4, column = 1, sticky = 'nsew')
    ppc_upgrade_button.grid(row = 5, column = 0, sticky = 'nsew')
    acps_upgrade_button.grid(row = 5, column = 1, sticky = 'nsew')
    cc_upgrade_button.grid(row = 6, column = 0, sticky = 'nsew')
    cm_upgrade_button.grid(row = 6, column = 1, sticky = 'nsew')
    cba_button.grid(row = 7, column = 0, sticky = 'nsew')
    autobuyer_button.grid(row = 7, column = 1, sticky = 'nsew')
    placeholder_button.grid(row = 8, column = 0, sticky = 'nsew')
    info_button.grid(row = 8, column = 1, sticky = 'nsew')
    save_button.grid(row = 9, column = 0, sticky = 'nsew')
    quit_button.grid(row = 9, column = 1, sticky = 'nsew')

    root.protocol("WM_DELETE_WINDOW", quit_game)
    root.bind('<Configure>', lambda event: adjust_font_size())

    return root

def update_window():
    expected_points_per_click = round(save_data["pm"] * save_data["ppc"] * (((1 - save_data["cc"] % 1) * save_data["cm"] ** math.floor(save_data["cc"])) + (save_data["cc"] % 1) * save_data["cm"] ** math.ceil(save_data["cc"])))

    points_text.config(text = f'Points: {pretty_num(round(save_data["points"]))}')
    pm_text.config(text = f'Extra Points: {pretty_num(round((save_data["pm"] - 1) * 100))}%')
    ppc_text.config(text = f'Points Per Click: {pretty_num(save_data["ppc"])}')
    acps_text.config(text = f'AutoClicks Per Second: {pretty_num(save_data["acps"])}')
    cc_text.config(text = f'Critical Chance: {pretty_num(round(save_data["cc"] * 100))}%')
    cm_text.config(text = f'Critical Multiplier: {pretty_num(save_data["cm"])}x')
    eppc_text.config(text = f'Expected Points Per Click: {pretty_num(expected_points_per_click)}')
    pps_text.config(text = f'Points Per Second: {pretty_num(round(points_per_second))}')

    cba_button.config(text = f'Cycle Buy Amount (Current: {save_data["current_buy_amount"]})', command = cycle_buy_amount)

    autobuyer_states = {False: "Off", True: "On"}
    autobuyer_button.config(text = f'Toggle Autobuyer (Is: {autobuyer_states[save_data["autobuyer_state"]]})', command = toggle_autobuyer)

if os.path.exists('save'):
    save_file = open('save', 'r', encoding = "utf-8")
    save_data = ast.literal_eval(save_file.read())
    save_file.close()
    expected_points_per_click = round(save_data["pm"] * save_data["ppc"] * (((1 - save_data["cc"] % 1) * save_data["cm"] ** math.floor(save_data["cc"])) + (save_data["cc"] % 1) * save_data["cm"] ** math.ceil(save_data["cc"])))
    offline_points = round((time.time() - save_data["last_play_time"]) * save_data["acps"] * expected_points_per_click)
    print(f"Gained {pretty_num(offline_points)} points while offline.")
    save_data["points"] += offline_points
else:
    save_file = open('save', 'x', encoding = "utf-8")
    save_file.close()
    # ppc = Points per click, pm = Points multiplier, acps = Autoclicks per second, cc = Critical chance, cm = Critical multiplier
    save_data = {'points': 0, 'ppc': 1, 'pm': 1, 'acps': 0, 'cc': 0.01, 'cm': 10, 'ppc_cost' : 10, 'pm_cost' : 100, 'acps_cost' : 1000, 'cc_cost': 10000, 'cm_cost': 100000, 'current_buy_amount': 1, 'autobuyer_state': False, 'last_play_time': time.time()}

def game_loop():
    global prev_points, points_per_second, expected_points_per_click

    click(save_data["acps"])
    points_per_second = save_data["points"] - prev_points
    prev_points = save_data["points"]

    if save_data["autobuyer_state"]:
        for cost_key in auto_upgrade_priority:
            while next_upgrade_costs[cost_key] <= save_data["points"]:
                upgrade(cost_key)

    update_window()

    window.after(1000, game_loop)

upgrade_types = ['ppc', 'pm', 'acps', 'cc', 'cm']
auto_upgrade_priority = ['acps', 'cc', 'ppc', 'pm', 'cm']

increase_per_upgrade = {
    "acps" : 1,
    "pm" : 0.1,
    "ppc" : 1,
    "cc" : 0.01,
    "cm" : 2,
}

determine_cost = lambda cost_type : sum([calc_upgrade_cost(cost_type, save_data[cost_type] + i * increase_per_upgrade[cost_type]) for i in range(save_data["current_buy_amount"])])
next_upgrade_costs = {upgrade_type: determine_cost(upgrade_type) for upgrade_type in upgrade_types}

prev_points = save_data["points"]
points_per_second = 0
window = create_window()
update_display_costs()

game_loop()

window.mainloop()

