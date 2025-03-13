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


def safe_int(num):
    if int(num) == num:
        num = int(num)
    return num

def save():
    save_file = open('save', 'w', encoding = "utf-8")
    save_file.write(str(save_data))
    save_file.close()

def click():
    if random.random() < save_data["critical_chance"]:
        increment = save_data["critical_multiplier"] * save_data["points_per_click"]
        print(f"Critical Click! Got {pretty_num(increment)} points.")
    else:
        increment = save_data["points_per_click"]
    save_data["points"] += save_data["points_multiplier"] * increment
    update_window()

def acps_upgrade():
    if save_data["points"] >= save_data["acps_cost"]:
        print(f"Upgraded AutoClicks per Second for {pretty_num(save_data['acps_cost'])} points.")
        save_data["points"] -= save_data["acps_cost"]
        save_data["autoclicks_per_second"] += 1
        save_data["acps_cost"] = math.floor(save_data["acps_cost"] * 1.5)
        update_window()

def pm_upgrade():
    if save_data["points"] >= save_data["pm_cost"]:
        print(f"Upgraded Points per Second for {pretty_num(save_data['pm_cost'])} points.")
        save_data["points"] -= save_data["pm_cost"]
        save_data["points_multiplier"] += 0.1
        save_data["pm_cost"] *= 2
        update_window()

def ppc_upgrade():
    if save_data["points"] >= save_data["ppc_cost"]:
        print(f"Upgraded Points per Click for {pretty_num(save_data['ppc_cost'])} points.")
        save_data["points"] -= save_data["ppc_cost"]
        save_data["points_per_click"] += 1
        save_data["ppc_cost"] += 10
        if save_data["points_per_click"] % 10 == 0:
            save_data["ppc_cost"] = 2 * round(save_data["ppc_cost"], -2)
        update_window()

def cc_upgrade():
    if save_data["points"] >= save_data["cc_cost"]:
        print(f"Upgraded Critical Click Chance for {pretty_num(save_data['cc_cost'])} points.")
        save_data["points"] -= save_data["cc_cost"]
        save_data["critical_chance"] = round(save_data["critical_chance"] + 0.01, 2)
        save_data["cc_cost"] = math.ceil(save_data["cc_cost"] * 1.1)
        update_window()

def cm_upgrade():
    if save_data["points"] >= save_data["cm_cost"]:
        print(f"Upgraded Critical Click Multiplier for {pretty_num(save_data['cm_cost'])} points.")
        save_data["points"] -= save_data["cm_cost"]
        save_data["critical_multiplier"] += 2
        save_data["cm_cost"] += 20000
        update_window()

def quit_game():
    global close_game
    window.quit()
    save_data['last_play_time'] = time.time()
    save()
    close_game = True

def adjust_font_size():
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    font_size = max(math.ceil(min(window_width, window_height) / 25), 8)
    new_font = ("TkDefaultFont", font_size)

    text_style.configure("TLabel", font = new_font)
    text_style.configure("TButton", font = new_font)

def create_window():
    global points_text, pm_text, ppc_text, acps_text, cc_text, cm_text, eppc_text, pps_text
    global click_button, save_button, quit_button, pm_upgrade_button, ppc_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button
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

    points_text = ttk.Label(root, text = f'Points: {pretty_num(round(save_data["points"]))}')
    pm_text = ttk.Label(root, text = f'Extra Points: {pretty_num(round((save_data["points_multiplier"] - 1) * 100))}%')
    ppc_text = ttk.Label(root, text = f'Points Per Click: {pretty_num(save_data["points_per_click"])}')
    acps_text = ttk.Label(root, text = f'AutoClicks Per Second: {pretty_num(save_data["autoclicks_per_second"])}')
    cc_text = ttk.Label(root, text = f'Critical Chance: {save_data["critical_chance"]}')
    cm_text = ttk.Label(root, text = f'Critical Multiplier: {pretty_num(save_data["critical_multiplier"])}x')
    eppc_text = ttk.Label(root, text = f'Expected Points Per Click: {pretty_num(round(save_data["points_per_click"] * save_data["points_multiplier"] * (1 - save_data["critical_chance"]) + save_data["points_per_click"] * save_data["critical_chance"] * save_data["critical_multiplier"]))}')
    pps_text = ttk.Label(root, text = f'Points Per Second: {pretty_num(round(points_per_second))}')

    points_text.grid(row = 0, column = 0, sticky = 'nsew')
    pm_text.grid(row = 0, column = 1, sticky = 'nsew')
    ppc_text.grid(row = 1, column = 0, sticky = 'nsew')
    acps_text.grid(row = 1, column = 1, sticky = 'nsew')
    cc_text.grid(row = 2, column = 0, sticky = 'nsew')
    cm_text.grid(row = 2, column = 1, sticky = 'nsew')
    eppc_text.grid(row = 3, column = 0, sticky = 'nsew')
    pps_text.grid(row = 3, column = 1, sticky = 'nsew')

    click_button = ttk.Button(root, text = "Click", command = click)
    pm_upgrade_button = ttk.Button(root, text = f'Upgrade EP (Cost: {pretty_num(save_data["pm_cost"])})', command = pm_upgrade)
    ppc_upgrade_button = ttk.Button(root, text = f'Upgrade PpC (Cost: {pretty_num(save_data["ppc_cost"])})', command = ppc_upgrade)
    acps_upgrade_button  = ttk.Button(root, text = f'Upgrade aCpS (Cost: {pretty_num(save_data["acps_cost"])})', command = acps_upgrade)
    cc_upgrade_button  = ttk.Button(root, text = f'Upgrade CC (Cost: {pretty_num(save_data["cc_cost"])})', command = cc_upgrade)
    cm_upgrade_button  = ttk.Button(root, text = f'Upgrade CM (Cost: {pretty_num(save_data["cm_cost"])})', command = cm_upgrade)
    save_button  = ttk.Button(root, text = "Save", command = save)
    quit_button  = ttk.Button(root, text = "Quit", command = quit_game)
    
    click_button.grid(row = 4, column = 0, sticky = 'nsew')
    pm_upgrade_button.grid(row = 4, column = 1, sticky = 'nsew')
    ppc_upgrade_button.grid(row = 5, column = 0, sticky = 'nsew')
    acps_upgrade_button.grid(row = 5, column = 1, sticky = 'nsew')
    cc_upgrade_button.grid(row = 6, column = 0, sticky = 'nsew')
    cm_upgrade_button.grid(row = 6, column = 1, sticky = 'nsew')
    save_button.grid(row = 7, column = 0, sticky = 'nsew')
    quit_button.grid(row = 7, column = 1, sticky = 'nsew')

    root.protocol("WM_DELETE_WINDOW", quit_game)
    root.bind('<Configure>', lambda event: adjust_font_size())

    return root

def update_window():
    points_text.config(text = f'Points: {pretty_num(round(save_data["points"]))}')
    pm_text.config(text = f'Extra Points: {pretty_num(round((save_data["points_multiplier"] - 1) * 100))}%')
    ppc_text.config(text = f'Points Per Click: {pretty_num(save_data["points_per_click"])}')
    acps_text.config(text = f'AutoClicks Per Second: {pretty_num(save_data["autoclicks_per_second"])}')
    cc_text.config(text = f'Critical Chance: {save_data["critical_chance"]}')
    cm_text.config(text = f'Critical Multiplier: {pretty_num(save_data["critical_multiplier"])}x')
    eppc_text.config(text = f'Expected Points Per Click: {pretty_num(round(save_data["points_per_click"] * save_data["points_multiplier"] * (1 - save_data["critical_chance"]) + save_data["points_per_click"] * save_data["critical_chance"] * save_data["critical_multiplier"]))}')
    pps_text.config(text = f'Points Per Second: {pretty_num(round(points_per_second))}')


    pm_upgrade_button.config(text = f'Upgrade EP (Cost: {pretty_num(save_data["pm_cost"])})', command = pm_upgrade)
    ppc_upgrade_button.config(text = f'Upgrade PpC (Cost: {pretty_num(save_data["ppc_cost"])})', command = ppc_upgrade)
    acps_upgrade_button.config(text = f'Upgrade aCpS (Cost: {pretty_num(save_data["acps_cost"])})', command = acps_upgrade)
    cc_upgrade_button.config(text = f'Upgrade CC (Cost: {pretty_num(save_data["cc_cost"])})', command = cc_upgrade)
    cm_upgrade_button.config(text = f'Upgrade CM (Cost: {pretty_num(save_data["cm_cost"])})', command = cm_upgrade)



if os.path.exists('save'):
    save_file = open('save', 'r', encoding = "utf-8")
    save_data = ast.literal_eval(save_file.read())
    save_file.close()
    offline_points = round((time.time() - save_data["last_play_time"]) * save_data["points_multiplier"] * (save_data["autoclicks_per_second"] * save_data["points_per_click"] * ((1 - save_data["critical_chance"]) + save_data["critical_chance"] * save_data["critical_multiplier"])))
    print(f"Gained {pretty_num(offline_points)} points while offline.")
    save_data["points"] += offline_points
else:
    save_file = open('save', 'x', encoding = "utf-8")
    save_file.close()
    save_data = {'points_per_click': 1, 'points_multiplier': 1, 'autoclicks_per_second': 0, 'points': 0, 'pm_cost' : 100, 'ppc_cost' : 10, 'acps_cost' : 1000, 'critical_chance': 0.01, 'critical_multiplier': 10, 'cc_cost': 10000, 'cm_cost': 100000, 'last_play_time': time.time()}

close_game = False

def game_loop():
    global prev_points, points_per_second
    for i in range(save_data["autoclicks_per_second"]):
        click()
    points_per_second = save_data["points"] - prev_points
    prev_points = save_data["points"]

    update_window()

    if not close_game:
        window.after(1000, game_loop)

prev_points = save_data["points"]
points_per_second = 0

window = create_window()

game_loop()

window.mainloop()
