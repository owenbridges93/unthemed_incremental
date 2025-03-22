# Import tkinter for gui
import tkinter
from tkinter import ttk

# Import other relevant modules
import os
import math
import numpy
from decimal import Decimal
import ast
import random
import time
import datetime
import platform

# Return a number that is easily readable to display for the user
def pretty_num(num):
    # Safely convert the number to an integer
    num = safe_int(num)
    num = Decimal(num)

    # If the number is not that long, just add commas
    if len(str(Decimal(math.floor(num)))) < 6:
        num = f'{num:,}'

    # If the number is too long, convert it to scientific notation
    else:
        str_num = str(num).split(".")[0]
        magnitude = len(str_num) - 1

        principle = safe_int(round(num / (10 ** magnitude), 3))

        if principle == 10:
            principle = 1
            magnitude += 1
        
        num = f'{principle}e{magnitude}'
    
    # Return the processed value
    return num

# (Not currently in use, is for future idea) Convert a prettified number string to a list with a significand and magnitude
def pretty_to_value_with_magnitude(num):
    # If the number was injected with commas, remove them
    if "," in num:
        num = [float("".join(num.split(","))), 1]

    # If the number is in scientific notation, find the significand and exponent
    elif "e" in num:
        num = [num.split("e")]
        num = [float(num[0]), int(num[1])]

    # If the number had neither, just change its data type
    else:
        num = [float(num), 1]

    # Safely convert the significand in the list to an integer
    num[0] = safe_int(num[0])

    # Return the number as a list
    return num

# Safely convert a number to an integer
def safe_int(num):
    # Only convert to an integer if no data is lost
    if int(num) == num:
        num = int(num)

    # Return the processed number
    return num

def newlines(num = 4):
    print("".join(["\n" for i in range(num)]))

# Handle a click event
def click(times = 1, manual = False):
    # Access clicked_in_last_second and player_is_idle for manipulation
    global clicked_in_last_second, player_is_idle, click_combo
    
    times = int(times)

    # Raise clicked_in_last_second flag if the player clicked manually
    if manual:
        clicked_in_last_second = True
        click_combo += times
        if player_is_idle:
            print("You are no longer idle.")
            player_is_idle = False
        update_attribute_labels()

    # Calculate points increment from basic and critical clicks
    gain_from_click = attributes["ppc"] * attributes["pm"] * attributes["cm"] ** math.floor(attributes["cc"])
    gain_from_critical = gain_from_click * attributes["cm"]

    if player_is_idle:
        gain_from_click *= prestige_data["im"]
    else:
        gain_from_click *= 1 + prestige_data["cpm"] * click_combo

    num_criticals = Decimal(numpy.random.binomial(n = times, p = attributes["cc"] % 1))

    num_normals = times - num_criticals

    # Calculate the total increment to add to the amount of points
    increment = num_normals * gain_from_click + num_criticals * gain_from_critical

    # Calculate how number of criticals and points increment from them
    gain_from_criticals = round(num_criticals * gain_from_critical)

    # If critical clicks were rolled, print a message to display information about them
    if gain_from_criticals > 0:
        if num_criticals == 1:
            print(f"Tier {pretty_num(math.ceil(attributes['cc']))} Critical Click! Got {pretty_num(gain_from_criticals)} points.")
        else:
            print(f"Got {pretty_num(gain_from_criticals)} Points from {pretty_num(num_criticals)} Tier {pretty_num(math.ceil(attributes['cc']))} Critical Clicks.")
    
    increment *= prestige_data["apm"]

    # Add increment to the amount of points the user has
    currency["points"] += round(increment)

    # Update attribute labels to show the new points value
    update_attribute_labels()

# Calculate the cost of an upgrade
def calc_upgrade_cost(attribute, target_value):

    target_value = Decimal(target_value)

    # Define functions to return the cost of upgrading an attribute to num level(s)
    formulas = {
        "acps" : lambda num: round(1000 * Decimal('1.5') ** num),
        "pm" : lambda num: math.ceil(100 * Decimal('1.25') ** ((num - 1) * 10)),
        "ppc" : lambda num: 10 * (num % 10) + 200 * min(1, math.floor(num / 10)) * 2 ** Decimal(math.floor(num / 10) - 1),
        "cc" : lambda num: math.ceil(10000 * Decimal('1.1') ** ((num - Decimal('0.01')) * 100)),
        "cm" : lambda num: round(100000 + 10000 * (num - 10) * Decimal('1.025') ** (num - 10)),

        "apm" : lambda num: math.floor(2 ** ((num - 1) * 10)),
        "ud" : lambda num: math.floor(2 ** (num * 100)),
        "mp10acps" : lambda num: math.floor(1 * 1000000 ** (num - 1)),
        "aum" : lambda num: math.floor(1 * 1000000 ** (num - 1)),
        "im" : lambda num: math.floor(2 ** ((num - 1) * 10)),
        "cpm" : lambda num: math.floor(10 ** (num * 100))
    }
    
    if attribute in attributes:
        cost_multi = 1 - prestige_data["ud"]
    else:
        cost_multi = 1

    # Return the cost for upgrading the attribute to target_value
    return round(formulas[attribute](target_value) * cost_multi)


# Construct the display message for upgrading something
def calc_upgrade_message(attribute, cost):
    # Define the messages for each attribute
    attribute_messages = {
        "acps" : "AutoClicks per Second",
        "pm" : "Points Multiplier",
        "ppc" : "Points per Click",
        "cc" : "Critical Click Chance",
        "cm" : "Critical Click Multiplier"
    }
    prestige_messages = {
        'apm' : 'Additional Points Multiplier',
        'ud' : 'Upgrade Discount',
        'mp10acps' : 'Multiplier per 10 AutoClicks per Second',
        'aum' : 'Additional Upgrade Multiplier',
        'im' : 'Idle Multiplier',
        'cpm' : 'Combo Multiplier'
    }

    messages = {"attribute" : attribute_messages, "prestige" : prestige_messages}

    if attribute in attribute_messages:
        message_type = "attribute"
        points_type = "points"
    else:
        message_type = "prestige"
        points_type = "prestige points"

    # Construct a string with the attribute upgraded, amount of times it was upgraded, and the cost of the upgrade
    if buy_settings["current_buy_amount"] == 1:
        message = f"Upgraded {messages[message_type][attribute]} for {pretty_num(cost)} {points_type}."
    else:
        message = f'Upgraded {messages[message_type][attribute]} {pretty_num(buy_settings["current_buy_amount"])} times for {pretty_num(cost)} {points_type}.'

    # Return the constructed message
    return message

# Handle an upgrade event 
def upgrade(attribute):
    # Access the attributes and currency dictionaries for manipulation
    global attributes, prestige_data, currency
    
    if attribute == "ud" and round(prestige_data["ud"], 2) >= 0.99:
        print("That upgrade is already maxed out.")
        return None

    if attribute in attributes:
        upgrade_list = attributes
        upgrade_currency = "points"
    elif attribute in prestige_data:
        upgrade_list = prestige_data
        upgrade_currency = "prestige_points"
    
    # Find what to increment the upgrading quantity by
    increment = increase_per_upgrade[attribute] * buy_settings["current_buy_amount"]

    # Find the cost to upgrade the attribute to the target value by taking a series of the upgrades leading up to it
    upgrade_cost = sum([calc_upgrade_cost(attribute, upgrade_list[attribute] + i * increase_per_upgrade[attribute]) for i in range(buy_settings["current_buy_amount"])])

    # If the user can afford the upgrade, go through with it
    if upgrade_cost <= currency[upgrade_currency]:
        if upgrade_currency == "points":
            upgrade_multiplier = prestige_data["aum"]
        else:
            upgrade_multiplier = 1
        # Add the the attribute value
        upgrade_list[attribute] += increment * upgrade_multiplier

        # Charge the user for the upgrade(s)
        currency[upgrade_currency] -= upgrade_cost

        # Print the transaction information in the console
        print(calc_upgrade_message(attribute, upgrade_cost))

        # Update the window and display costs for upgrades
        update_attribute_labels()
        update_attribute_buttons()
        if upgrade_currency == 'prestige_points':
            update_prestige_labels()
            update_prestige_buttons()
    else:
        print("You can't afford that upgrade.")

# Find the maximum amount of times an attribute can be upgraded
def find_max_upgrade(attribute):
    # Store the current value of current_buy_amount in buy_settings
    current_buy_amount = buy_settings["current_buy_amount"]

    if attribute in attributes:
        upgrade_list = attributes
        upgrade_currency = "points"
    elif attribute in prestige_data:
        upgrade_list = prestige_data
        upgrade_currency = "prestige_points"


    # Find the maximum amount of upgrades that the user can afford for the attribute
    buy_settings["current_buy_amount"] = 0
    while determine_cost(attribute, upgrade_list) <= currency[upgrade_currency]:
        buy_settings["current_buy_amount"] += 1
    max_upgrade_num = buy_settings["current_buy_amount"] - 1

    # Return current_buy_amount in buy_settings to its original value
    buy_settings["current_buy_amount"] = current_buy_amount

    return max_upgrade_num

# Change how many times an upgrade is purchased per button click
def cycle_buy_amount():
    # Access buy settings dictionary for manipulation
    global buy_settings

    # Define the list of options for buy amount per click
    amounts = [1, 10, 25, 100, 250]

    # Update buy_settings with the next item in the list, wrapping around when needed
    buy_settings["current_buy_amount"] = amounts[(amounts.index(buy_settings["current_buy_amount"]) + 1) % len(amounts)]

    # Log the new current buy amount
    print(f"New buy amount per click: {buy_settings['current_buy_amount']}")

    # Update the window and upgrade costs
    update_attribute_buttons()
    update_buy_setting_buttons()
    update_prestige_buttons()

# Toggle whether or not the autobuyer is on
def toggle_autobuyer():
    # Access buy_settings dictionary for manipulation
    global buy_settings

    # Toggle the autobuyer on or off
    buy_settings["autobuyer_state"] = not (buy_settings["autobuyer_state"])

    # Log the new state of the autobuyer
    autobuyer_states = {True : "on", False : "off"}
    print(f"Autobuyer toggled {autobuyer_states[buy_settings['autobuyer_state']]}.")

    # Update the window to display current autobuyer state
    update_buy_setting_buttons()

# Find how many prestige points the player would gain from prestiging
def find_prestige_gain():
    return round((2 * Decimal(currency["points"]) / 10 ** 10) ** Decimal('0.5'))

# Prestige the player
def prestige_player():
    # Access relevant save data for resetting during prestige
    global currency, attributes, buy_settings, player_data

    # If the user can afford to prestige, reset their attributes and add to their prestige points
    if currency["points"] >= (10 ** 10):
        print(f"Prestiged for {pretty_num(find_prestige_gain())} prestige points.")


        new_prestige_points = currency['prestige_points'] + find_prestige_gain()
        currency = {'points' : Decimal(0), 'prestige_points' : new_prestige_points}
        attributes = {'ppc': 1, 'pm': Decimal(1), 'acps': 0, 'cc': Decimal('0.01'), 'cm': 10}
        buy_settings = {'current_buy_amount': 1, 'autobuyer_state': False}

        current_time = datetime.datetime.now()
        player_data['last_prestige_date'] = f"{current_time.month}/{current_time.day}/{current_time.year}, {current_time.hour}:{current_time.minute}"
        
        update_prestige_labels()
        update_attribute_labels()
        update_attribute_buttons()
    # If the user can't afford to prestige, tell them
    else:
        print("You cannot yet afford to prestige.")

# Create a window to display information about the game mechanics
def display_info():
    # Initialize the information window
    info_window = tkinter.Tk()

    # Find the dimensions of the display
    screen_width = info_window.winfo_screenwidth()
    screen_height = info_window.winfo_screenheight()

    # Set the dimensions of the window based off of the display dimensions
    window_width = int(screen_width / 2)
    window_height = int(screen_height / 2)

    # Find the center of the screen
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    # Set the windows geometry based off of the calculated values
    info_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    # Prevent the user from resizing this window
    info_window.resizable(False, False)

    # Define a title for this window
    info_window.title("Information")

    # Access a window icon and set it for this window
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "assets/media/info.ico")
    info_window.iconbitmap(icon_path)

    # Set a font for this window
    font_size = math.ceil(min(window_width, window_height) / 34)
    info_font = ("TkDefaultFont", font_size)

    info_tabs = ttk.Notebook(info_window)

    attributes_tab = ttk.Frame(info_tabs)
    prestige_tab = ttk.Frame(info_tabs)

    tab_descriptions = {
        attributes_tab : "Attributes",
        prestige_tab : "Prestige Upgrades"
    }

    for tab in tab_descriptions:
        info_tabs.add(tab, text = tab_descriptions[tab])

    # Create labels explaining the attribute mechanics
    pm_info = ttk.Label(attributes_tab, wraplength = window_width, text = 'PM: When clicking, the the Extra Points% is added to the increment (e.g. If you get 10 points after crit and have 130% extra points you would get 23 points from that click).\n', font = info_font)
    ppc_info = ttk.Label(attributes_tab, wraplength = window_width, text = 'PpC: Points per click is the base amount of points you get per click.\n', font = info_font)
    acps_info = ttk.Label(attributes_tab, wraplength = window_width, text = 'aCpS: Autoclicks per second is the amount of times the game automatically clicks for you every second.\n', font = info_font)
    cc_info = ttk.Label(attributes_tab, wraplength = window_width, text = 'CC: Critical chance is the chance of landing a critical click. For values higher than 1, every critical click is guaranteed to multiply the points by critical_multiplier ^ floor(critical_chance), and has a critical_chance % 1 probability of multiplying the points value by critical_multiplier again.\n', font = info_font)
    cm_info = ttk.Label(attributes_tab, wraplength = window_width, text = 'CM: Critical multiplier is how much the points per click is multiplied with upon landing a critical hit.\n', font = info_font)
    cba_info = ttk.Label(attributes_tab, wraplength = window_width, text = 'CBA: Cycling the buy amount allows you to buy more than one of an upgrade at a time.\n', font = info_font)
    autobuyer_info = ttk.Label(attributes_tab, wraplength = window_width, text = 'AB: The autobuyer will automatically buy upgrades when you can afford them.\n', font = info_font)


    # Create labels explaining prestige attribute mechanics
    apm_info = ttk.Label(prestige_tab, wraplength = window_width, text = 'aPm: Additional points multiplier is an additional multiplier applied to the points you gain.\n', font = info_font)
    ud_info = ttk.Label(prestige_tab, wraplength = window_width, text = 'UD: Upgrade discounts are removed from prices of attribute upgrades.\n', font = info_font)
    mp10acps_info = ttk.Label(prestige_tab, wraplength = window_width, text = 'Mp10aCpS: Multiplier per 10 autoclicks per second is applied the clicks per second of each "autoclicker" for every 10 that you buy.\n', font = info_font)
    aum_info = ttk.Label(prestige_tab, wraplength = window_width, text = 'aUm: Additional upgrades multiplier gives you a "2 for the price of 1" deal for upgrades where the 2 is instead your AUM.\n', font = info_font)
    im_info = ttk.Label(prestige_tab, wraplength = window_width, text = 'IM: The points you earn are multiplied by this number while idle (no manual clicks in last 60 seconds).\n', font = info_font)
    cm_info = ttk.Label(prestige_tab, wraplength = window_width, text = 'CPM :The points you earn are multiplied by this number and and your current click combo, which resets when you go idle.\n', font = info_font)

    tabs = {
        attributes_tab : [pm_info, ppc_info, acps_info, cc_info, cm_info, cba_info, autobuyer_info],
        prestige_tab : [apm_info, ud_info, mp10acps_info, aum_info, im_info, cm_info]
    }

    # Pack the labels into tabs
    for tab in tabs:

        for info in tabs[tab]:
            info.pack()
    
    info_tabs.grid(row = 0, column = 0, sticky = 'nsew')

    info_window.grid_rowconfigure(0, weight = 1)
    info_window.grid_columnconfigure(0, weight = 1)

    # Start the mainloop for the window
    info_window.mainloop()

def dark_mode(switch = False):
    global player_data

    if switch:
        player_data["dark_mode"] = not player_data["dark_mode"]

    mode_icons = {True : "_dark_mode", False : ""}

    # Access a window icon and set it for the window
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, f"assets/media/game{mode_icons[player_data['dark_mode']]}.ico")
    window.iconbitmap(icon_path)

    widget_types = ["TLabel", "TFrame", "TButton", "TNotebook"]
    bg_color, fg_color, active_color = ["#100000", "#c60000", "#400000"] if player_data["dark_mode"] else ["lightgrey", "#000000", "#cccccc"]

    for widget_type in widget_types:
        game_window_style.configure(widget_type, background = bg_color, foreground = fg_color)

    game_window_style.map("TButton", foreground = [('pressed', fg_color)], background = [('pressed', active_color)])

    game_window_style.configure("TNotebook.Tab", background = bg_color, foreground = fg_color)
    game_window_style.map("TNotebook.Tab", foreground = [('selected', fg_color)], background = [('selected', active_color)])

    window.configure(bg = bg_color)

    modes_display_values = {True : "Dark", False : "Light"}
    mode_display = modes_display_values[player_data['dark_mode']]
    
    dark_mode_button.config(text = f"Mode: {mode_display}", command = lambda : dark_mode(True))

    if switch:
        print(f"Switched to {mode_display.lower()} mode.")

    if player_data["easter_egg"]:
        icon_path = os.path.join(script_dir, f"assets/media/game_dark_mode_glowing.ico")
        window.iconbitmap(icon_path)
    
# Placeholder function for placeholder button
def update_all_visuals():
    update_attribute_buttons()
    update_attribute_labels()
    update_buy_setting_buttons()
    update_prestige_buttons()
    update_prestige_labels()
    dark_mode()

# Save the game state to a file for persistence through runs of the code
def save():
    print("Saving... ", end = "")
    # Open the save file in the assets folder
    save_file = open('assets/save', 'w', encoding = "utf-8")

    # Compile all save data categories back into one dictionary
    save_data = {
        "currency" : currency.copy(), 
        "attributes" : attributes.copy(), 
        "buy_settings" : buy_settings.copy(), 
        "prestige" : prestige_data.copy(), 
        "player_data" : player_data.copy()
    }

    

    for data_type in save_data:
        for data_point in save_data[data_type]:
            if data_point in ["last_prestige_date", "autobuyer_state", "current_buy_amount", "dark_mode", "easter_egg"]:
                continue
            save_data[data_type][data_point] = str(save_data[data_type][data_point])

    # Write the current attributes to the file
    save_file.write(str(save_data))
    
    # Close the file
    save_file.close()

    # Alert the user that the game was saved
    print("Game saved.")

def create_save():
    # Create new save data
    currency = {'points' : 0, 'prestige_points' : 0}
    # ppc = Points per click, pm = Points multiplier, acps = Autoclicks per second, cc = Critical chance, cm = Critical multiplier
    attributes = {'ppc': 1, 'pm': Decimal(1), 'acps': 0, 'cc': Decimal('0.01'), 'cm': 10}
    buy_settings = {'current_buy_amount': 1, 'autobuyer_state': False}
    # apm = Additional points multiplier, ud = Upgrade discount, mp10acps = Multiplier per 10 autoclicks per second, aum = Attribute upgrade multiplier, im = Idle multiplier, cm = Combo multiplier
    prestige_data = {'apm' : Decimal(1), 'ud' : Decimal(0), 'mp10acps' : 1, 'aum' : 1, 'im' : Decimal(1), 'cpm' : Decimal(0)}
    player_data = {'dark_mode' : False,'last_play_time' : Decimal(time.time()), 'last_prestige_date' : "N/A", 'easter_egg' : False}

    return currency, attributes, buy_settings, prestige_data, player_data

def load_save():
    try:
        print("Loading save data... ", end = "")
        
        # Access the save file and read save data from it
        with open('assets/save', 'r', encoding = "utf-8") as save_file:
            save_data = ast.literal_eval(save_file.read())

        for data_type in save_data:
            for data_point in save_data[data_type]:
                if data_point in ["last_prestige_date", "autobuyer_state", "current_buy_amount", "dark_mode", "easter_egg"]:
                    continue
                save_data[data_type][data_point] = Decimal(save_data[data_type][data_point])



        currency = save_data["currency"]
        attributes = save_data["attributes"]
        buy_settings = save_data["buy_settings"]
        prestige_data = save_data["prestige"]
        player_data = save_data["player_data"]

        print("Done.")

        return currency, attributes, buy_settings, prestige_data, player_data
    except SyntaxError:
        invalid_save()


# Handle the user closing the game
def quit_game():
    # Record when the game was closed
    player_data['last_play_time'] = Decimal(time.time())

    # Save the game to a file
    save()

    # Stop all code
    exit()

def invalid_save():
    try:
        window.destroy()
    except NameError:
        pass
    newlines()
    print("The save data is invalid. Either delete assets/save or revert it to the default format, then reload the game.")
    input("Press enter to continue...\n\n\n")
    exit()

# Create the game window and return it
def create_window():
    # Make labels, buttons, and font global so other functions can manipulate them
    global points_text, pm_text, ppc_text, acps_text, cc_text, cm_text, eppc_text, pps_text
    global click_button, pm_upgrade_button, ppc_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button
    global cba_button, autobuyer_button
    global prestige_text, prestige_button
    global ppoints_text, lp_text, apm_text, ud_text, mp10acps_text, aum_text, im_text, cpm_text
    global apm_upgrade_button, ud_upgrade_button, mp10acps_upgrade_button, aum_upgrade_button, im_upgrade_button, cpm_upgrade_button
    global dark_mode_button
    global game_window_style

    # Initialize the game window
    game_window = tkinter.Tk()

    # Set the initial dimensions for the game window
    window_width = 480
    window_height = 260

    # Calculate the coordinates of the center of the screen
    screen_width = game_window.winfo_screenwidth()
    screen_height = game_window.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    # Use the calculated values to set the geometry for the window
    game_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    # Make the window resizable
    game_window.resizable(True, True)

    # Set a title for the window
    game_window.title("Unthemed Incremental")

    # Access a window icon and set it for the window
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "assets/media/game.ico")
    game_window.iconbitmap(icon_path)

    # Create the font style for buttons and labels
    game_window_style = ttk.Style()

    game_window_style.theme_use("alt")

    game_window_style.configure("TLabel", font=("TkDefaultFont", 12))
    game_window_style.configure("TButton", font=("TkDefaultFont", 12))

    # Define how many rows and columns the window should have
    game_window_rows = 10
    game_window_columns = 2
        
    # Set a weight for each row and column
    for i in range(game_window_rows):
        game_window.grid_rowconfigure(i, weight = 1)
    for i in range(game_window_columns):
        game_window.grid_columnconfigure(i, weight = 1)

    # Initialize notebook to store buttons in tabs
    game_tabs = ttk.Notebook(game_window)

    # Initialize the tabs in the notebook
    attributes_tab = ttk.Frame(game_tabs)
    buy_settings_tab = ttk.Frame(game_tabs)
    prestige_tab = ttk.Frame(game_tabs)
    prestige_shop_tab = ttk.Frame(game_tabs)
    menu_tab = ttk.Frame(game_tabs)

    # Define display text for the tabs
    tabs_display_text = {
        attributes_tab : "Attributes",
        buy_settings_tab : "Attribute Purchase Settings",
        prestige_tab : "Prestige",
        prestige_shop_tab : "Prestige Shop",
        menu_tab : "Menu"
    }

    # Add the tabs to the notebook with their display text
    for tab in tabs_display_text:
        game_tabs.add(tab, text = tabs_display_text[tab])

    # Initialize labels for the window
    points_text = ttk.Label(attributes_tab)
    pm_text = ttk.Label(attributes_tab)
    ppc_text = ttk.Label(attributes_tab)
    acps_text = ttk.Label(attributes_tab)
    cc_text = ttk.Label(attributes_tab)
    cm_text = ttk.Label(attributes_tab)
    eppc_text = ttk.Label(attributes_tab)
    pps_text = ttk.Label(attributes_tab)    
    
    prestige_text = ttk.Label(prestige_tab, wraplength = game_window.winfo_width(), text = 'Prestige will reset your points and attributes, but will give prestige points, which can be spent for persistent upgrades in the prestige shop. Prestiging requires 1e10 points, but the more points you have when you prestige, the more prestige points you gain from doing so.')
    
    ppoints_text = ttk.Label(prestige_shop_tab)
    lp_text = ttk.Label(prestige_shop_tab)
    apm_text = ttk.Label(prestige_shop_tab)
    ud_text = ttk.Label(prestige_shop_tab)
    mp10acps_text = ttk.Label(prestige_shop_tab)
    aum_text = ttk.Label(prestige_shop_tab)
    im_text = ttk.Label(prestige_shop_tab)
    cpm_text = ttk.Label(prestige_shop_tab)
    

    # Initialize buttons for the window
    click_button = ttk.Button(attributes_tab, text = '', command = lambda : click(times = 1, manual = True))
    pm_upgrade_button = ttk.Button(attributes_tab)
    ppc_upgrade_button = ttk.Button(attributes_tab)
    acps_upgrade_button  = ttk.Button(attributes_tab)
    cc_upgrade_button  = ttk.Button(attributes_tab)
    cm_upgrade_button  = ttk.Button(attributes_tab)
    
    cba_button  = ttk.Button(buy_settings_tab)
    autobuyer_button  = ttk.Button(buy_settings_tab)
    
    prestige_button = ttk.Button(prestige_tab)
    
    apm_upgrade_button = ttk.Button(prestige_shop_tab)
    ud_upgrade_button = ttk.Button(prestige_shop_tab)
    mp10acps_upgrade_button = ttk.Button(prestige_shop_tab)
    aum_upgrade_button = ttk.Button(prestige_shop_tab)
    im_upgrade_button = ttk.Button(prestige_shop_tab)
    cpm_upgrade_button = ttk.Button(prestige_shop_tab)
    
    dark_mode_button = ttk.Button(menu_tab)
    info_button  = ttk.Button(menu_tab, text = 'Info', command = display_info)
    save_button  = ttk.Button(menu_tab, text = "Save", command = save)
    quit_button  = ttk.Button(menu_tab, text = "Quit", command = quit_game)

    # Categorize the buttons into their respective tabs
    widgets = {
        attributes_tab : [points_text, pm_text, ppc_text, acps_text, cc_text, cm_text, eppc_text, pps_text, click_button, pm_upgrade_button, ppc_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button], 
        buy_settings_tab : [autobuyer_button, cba_button], # put autobuyer buttons here
        prestige_tab : [prestige_text, prestige_button], # put prestige buttons here
        prestige_shop_tab : [ppoints_text, lp_text, apm_text, ud_text, mp10acps_text, aum_text, im_text, cpm_text, apm_upgrade_button, ud_upgrade_button, mp10acps_upgrade_button, aum_upgrade_button, im_upgrade_button, cpm_upgrade_button], # put prestige shop buttons here
        menu_tab : [dark_mode_button, info_button, save_button, quit_button]
    }
    
    # Use the categories of buttons to put them in their respective tabs and weight each row/column in each tab
    for tab in widgets:
        if tab == prestige_tab:
            for widget in widgets[tab]: 
                widget.grid(row = widgets[tab].index(widget), column = 0, sticky = 'nsew')

                for i in range(2):
                    tab.grid_rowconfigure(i, weight = 1)
                for i in range(1):
                    tab.grid_columnconfigure(i, weight = 1)

        else:
            for widget in widgets[tab]:
                widget.grid(row = math.floor(widgets[tab].index(widget) / game_window_columns), column = widgets[tab].index(widget) % game_window_columns, sticky = 'nsew')

            for i in range(math.ceil(len(widgets[tab]) / game_window_columns)):
                tab.grid_rowconfigure(i, weight = 1)
            for i in range(game_window_columns):
                tab.grid_columnconfigure(i, weight = 1)

    # Put the notebook of tabs into the window
    game_tabs.grid(row = 0, column = 0, rowspan = game_window_rows, columnspan = game_window_columns, sticky = "nsew")

    # Bind running quit game to when the window manager closes the window
    game_window.protocol("WM_DELETE_WINDOW", quit_game)

    # Bind adjusting the font size to when the window is moved or resized
    game_window.bind('<Configure>', lambda event: adjust_font_size())

    # Return the constructed window
    return game_window

# Update text labels for attributes
def update_attribute_labels():
    # Recalculate point gain expected per click
    if player_is_idle:
        ci_multiplier = prestige_data["im"]
    else:
        ci_multiplier = 1 + prestige_data["cpm"] * click_combo
    expected_points_per_click = round(ci_multiplier * prestige_data["apm"] * attributes["ppc"] * attributes["pm"] * attributes["cm"] ** math.floor(attributes["cc"]) * ((1 - attributes["cc"] % 1) + attributes["cm"] * (attributes["cc"] % 1)))

    # Configure all labels to show current values from attributes
    points_text.config(text = f'Points: {pretty_num(currency["points"])}')
    pm_text.config(text = f'Extra Points: {pretty_num((attributes["pm"] - 1) * 100)}%')
    ppc_text.config(text = f'Points Per Click: {pretty_num(attributes["ppc"])}')
    acps_text.config(text = f'AutoClicks Per Second: {pretty_num(attributes["acps"])}')
    cc_text.config(text = f'Critical Chance: {pretty_num(attributes["cc"] * 100)}%')
    cm_text.config(text = f'Critical Multiplier: {pretty_num(attributes["cm"])}x')
    eppc_text.config(text = f'Expected Points Per Click: {pretty_num(expected_points_per_click)}')
    pps_text.config(text = f'Points Per Second: {pretty_num(points_per_second)}')

    # Update prestige button
    prestige_button.config(text = f"Prestige (Will Gain {pretty_num(find_prestige_gain())} Prestige Points)", command = prestige_player)

    # Update click button to display combo
    if player_is_idle:
        combo_state = "Idle"
    else:
        combo_state = f"Combo: {click_combo}"

    click_button.config(text = f'Click ({combo_state})', command = lambda : click(times = 1, manual = True))

# Update button text for attributes
def update_attribute_buttons():
    # Access and update next_upgrade_costs 
    global next_upgrade_costs
    next_upgrade_costs = {attribute : determine_cost(attribute, attributes) for attribute in attributes}


    # Associate upgrade buttons with their respective attributes
    upgrade_buttons = {
        ppc_upgrade_button : "ppc", 
        pm_upgrade_button : "pm", 
        acps_upgrade_button : "acps", 
        cc_upgrade_button : "cc", 
        cm_upgrade_button : "cm"
    }

    # Define list of abbreviations for each attribute to put on upgrade buttons
    upgrade_names = {
        ppc_upgrade_button : "PpC", 
        pm_upgrade_button : "EP", 
        acps_upgrade_button : "aCpS", 
        cc_upgrade_button : "CC", 
        cm_upgrade_button : "CM"
    }

    # Update each upgrade button with names and costs
    for button in upgrade_buttons:
        button.config(text = f'Upgrade {upgrade_names[button]} (Cost: {pretty_num(next_upgrade_costs[upgrade_buttons[button]])})', command = lambda to_upgrade = upgrade_buttons[button] : upgrade(to_upgrade))

#  Update button text for buy settings
def update_buy_setting_buttons():
    # Configure cycle buy amount button text to display current value from attributes
    cba_button.config(text = f'Cycle Buy Amount (Current: {buy_settings["current_buy_amount"]})', command = cycle_buy_amount)

    # Configure autobuyer button to display current state from attributes
    autobuyer_states = {False: "Off", True: "On"}
    autobuyer_button.config(text = f'Toggle Autobuyer (State: {autobuyer_states[buy_settings["autobuyer_state"]]})', command = toggle_autobuyer)

def update_prestige_labels():
    ppoints_text.config(text = f'Prestige Points: {pretty_num(currency["prestige_points"])}')
    lp_text.config(text = f'Last prestige: {player_data["last_prestige_date"]}')
    apm_text.config(text = f'Additional Points Multiplier: +{pretty_num((prestige_data["apm"] - 1) * 100)}%')
    ud_text.config(text = f'Upgrade Discount: {pretty_num(prestige_data["ud"] * 100)}%')
    mp10acps_text.config(text = f'Multiplier per 10 aCpS: {pretty_num(prestige_data["mp10acps"])}')
    aum_text.config(text = f'Additional Upgrades per Upgrade: {pretty_num(prestige_data["aum"] - 1)}')
    im_text.config(text = f'Idle Multiplier: +{pretty_num((prestige_data["im"] - 1) * 100)}%')
    cpm_text.config(text = f'Combo Points Multiplier: +{pretty_num(prestige_data["cpm"] * 100)}%')

def update_prestige_buttons():
    prestige_upgrade_costs = {prestige_attribute : determine_cost(prestige_attribute, prestige_data) for prestige_attribute in prestige_data}

    prestige_upgrade_buttons = {
        apm_upgrade_button : 'apm',
        ud_upgrade_button : 'ud',
        mp10acps_upgrade_button : 'mp10acps',
        aum_upgrade_button : 'aum',
        im_upgrade_button : 'im',
        cpm_upgrade_button : 'cpm'
    }

    prestige_upgrade_names = {
        apm_upgrade_button : 'aPm',
        ud_upgrade_button : 'UD',
        mp10acps_upgrade_button : 'Mp10aCpS',
        aum_upgrade_button : 'aUm',
        im_upgrade_button : 'IM',
        cpm_upgrade_button : 'CPM'
    }

    for button in prestige_upgrade_buttons:
        button.config(text = f'Upgrade {prestige_upgrade_names[button]} (Cost: {pretty_num(prestige_upgrade_costs[prestige_upgrade_buttons[button]])})', command = lambda to_upgrade = prestige_upgrade_buttons[button] : upgrade(to_upgrade))

# Adjust the font size for the game window
def adjust_font_size():
    # Find the dimensions of the game window
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Define the new font based off of window dimensions
    font_size = max(math.ceil(min(window_width, window_height) / 25), 8)
    new_font = ("TkDefaultFont", font_size)

    # Update labels and buttons with this new font
    game_window_style.configure("TLabel", font = new_font)
    game_window_style.configure("TButton", font = new_font)

    # Update text wrap of prestige text
    prestige_text.config(wraplength = window.winfo_width(), text = 'Prestige will reset your points and attributes, but will give prestige points, which can be spent for persistent upgrades in the prestige shop. Prestiging requires 1e10 points, but the more points you have when you prestige, the more prestige points you gain from doing so.')

def beat_game():
    global window, currency, attributes, buy_settings, prestige_data, player_data
    
    try:
        window.destroy()
    except NameError:
        pass

    save()

    if user_os in clear_commands:
        os.system(clear_commands[user_os])

    while True:
        newlines()
        print("You have somehow created an OverFlow error and in doing so, beaten the game.")

        create_new_save = input("Would you like to create a new save (y/n): ").strip().lower()
        if create_new_save in ["y", "n"]:
            break
        if user_os in clear_commands:
            os.system(clear_commands[user_os])
    
    if create_new_save == "y":
        currency, attributes, buy_settings, prestige_data, player_data = create_save()
        save()
        update_all_visuals()
        print("New save created.")
    else:
        print("In that case, goodbye.")
        if user_os == "Windows":
            os.system("pause")
        exit()

# Manage recurring timed events
def game_loop():
    try:
        # Access variables for manipulation
        global prev_points, points_per_second, clicks_in_last_minute, clicked_in_last_second, player_is_idle, click_combo

        # Click autoclicks per second times
        click(attributes["acps"] * max(1, prestige_data["mp10acps"] * math.floor(attributes["acps"] / 10)))


        # Calculate how many points were gained/lossed in the last second
        points_per_second = currency["points"] - prev_points

        # Update prev_points for next points_per_second calculation
        prev_points = currency["points"]

        # If the autobuyer is active, upgrade each attribute as many times as possible
        if buy_settings["autobuyer_state"]:
            # Initialize if any attributes can be upgraded
            can_upgrade = False
            
            # Find amount of times each attribute could be upgraded with current points
            upgrade_nums = [find_max_upgrade(attribute) for attribute in attributes]
            
            # If anything can be upgraded, set can_upgrade to true
            for item in upgrade_nums:
                if item > 0:
                    can_upgrade = True
                    break
            
            # If anything can be upgraded, activate the autobuyer
            if can_upgrade:
                # Store the current state of current_buy_amount in attributes
                current_buy_amount = buy_settings["current_buy_amount"]

                # Indicate that the following purchases are products of the autobuyer
                print("\nAutobuyer: ")
                
                # Upgrade each attribute in order of auto_upgrade_priority
                for attribute in auto_upgrade_priority:
                    # Find the maximum amount of times the attribute can be upgraded
                    max_upgrade = find_max_upgrade(attribute)

                    # If the attribute can be upgraded, do so
                    if max_upgrade > 0:
                        buy_settings["current_buy_amount"] = max_upgrade
                        upgrade(attribute)
                
                # Visually seperate autobuyer purchases from everything else
                print()

                # Revert current_buy_amount in buy_settings to the previous quantity
                buy_settings["current_buy_amount"] = current_buy_amount

                # Update the game window
                update_attribute_labels()
                update_attribute_buttons()

        # Record whether or not the user clicked in the last second
        if clicked_in_last_second:
            clicks_in_last_minute.append(1)
            clicked_in_last_second = False
        else:
            clicks_in_last_minute.append(0)

        # If the list details more than 60 seconds, remove the first second
        if len(clicks_in_last_minute) > 60:
                    clicks_in_last_minute.pop(0)

        # If the player has not clicked manually in the last 60 seconds, mark them as idle
        if not (player_is_idle or 1 in clicks_in_last_minute):
            print("You are now idle.")
            player_is_idle = True
            click_combo = 0
            update_attribute_labels()

        # Call game_loop again after 1 second
        window.after(1000, game_loop)

    except OverflowError:
        beat_game()
    except KeyError:
        invalid_save()

try:

    # Define clear commands native to the big three operating systems
    clear_commands = {
        "Windows" : "cls",
        "Darwin" : "clear",
        "Linux" : "clear"
    }

    # Fetch the user's operating system
    user_os = platform.system()

    if user_os in clear_commands:
        os.system(clear_commands[user_os])

    # If a save file exists, access it, else make one
    if os.path.exists('assets/save'):
        save_get = load_save
    else:
        # Create a save file
        save_file = open('assets/save', 'x', encoding = "utf-8")
        save_file.close()

        # Create new save data
        save_get = create_save

    currency, attributes, buy_settings, prestige_data, player_data = save_get()

    print("Starting game... ", end = "", flush = True)

    # Prioritize attributes for the autobuyer
    auto_upgrade_priority = ['acps', 'cc', 'cm', 'ppc', 'pm']

    # Define how much each attribute should be incremented by per upgrade
    increase_per_upgrade = {
        "acps" : 1,
        "pm" : Decimal('0.1'),
        "ppc" : 1,
        "cc" : Decimal('0.01'),
        "cm" : 2,

        "apm" : Decimal('0.1'),
        "ud" : Decimal('0.01'),
        "mp10acps" : Decimal('0.5'),
        "aum" : 1,
        "im" : Decimal('0.1'),
        "cpm" : Decimal('0.01')
    }


    # Define function to more consisely find the cost of upgrading a specific attribute a certain amount of times and use it to calculate costs for every attribute
    determine_cost = lambda cost_type, attribute_list : sum([calc_upgrade_cost(cost_type, attribute_list[cost_type] + i * increase_per_upgrade[cost_type]) for i in range(buy_settings["current_buy_amount"])])
    next_upgrade_costs = {attribute: determine_cost(attribute, attributes) for attribute in attributes}

    # Initialize values used in the game_loop function
    prev_points = currency["points"]
    points_per_second = 0

    # Initialize information about if the player is idle
    clicks_in_last_minute = []
    clicked_in_last_second = False
    player_is_idle = True
    click_combo = 0

    # Create the window and initialize display values
    window = create_window()
    update_all_visuals()
    
    print("Done.")

    # Calculate how many points the user gained while offline, notify the user, and give them the points
    expected_points_per_click = prestige_data["im"] * prestige_data["apm"] * attributes["ppc"] * attributes["pm"] * attributes["cm"] ** math.floor(attributes["cc"]) * ((1 - attributes["cc"] % 1) + attributes["cm"] * (attributes["cc"] % 1))
    offline_points = round((Decimal(time.time()) - player_data["last_play_time"]) * attributes["acps"] * max(1, prestige_data["mp10acps"] * math.floor(attributes["acps"] / 10)) * expected_points_per_click)
    if offline_points > 0:
        print(f"Gained {pretty_num(offline_points)} points while offline.")
        currency["points"] += offline_points


    # Start the game loop
    game_loop()

    # Create the game window
    window.mainloop()

except OverflowError:
    beat_game()
except KeyError:
    invalid_save()