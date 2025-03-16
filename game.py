# Import tkinter for gui
import tkinter
from tkinter import ttk

# Import other relevant modules
import os
import math
import ast
import random
import time
import platform

# Return a number that is easily readable to display for the user
def pretty_num(num):
    # Safely convert the number to an integer
    num = safe_int(num)

    # If the number is not that long, just add commas
    if len(str(math.floor(num))) < 6:
        num = f'{num:,}'

    # If the number is too long, convert it to scientific notation
    else:
        magnitude = math.floor(math.log10(abs(num)))
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

# Handle a click event
def click(times = 1):
    # Make empty array to record all point increments from clicks and whether or not they were critical
    clicks = [[], []]

    # Calculate points increment from basic and critical clicks
    gain_from_click = save_data["ppc"] * save_data["pm"] * save_data["cm"] ** math.floor(save_data["cc"])
    gain_from_critical = gain_from_click * save_data["cm"]

    # Populate the clicks list with point increments
    for i in range(times):
        # Generate a basic click
        click = [gain_from_click, 0]
    
        # Attempt to make the click critical, multiplying by the critical multiplier and marking the click as critical if successful
        if random.random() < save_data["cc"] % 1:
            click[0] = gain_from_critical
            click[1] = 1
        
        # Append click and whether it was critical to clicks
        clicks[0].append(click[0])
        clicks[1].append(click[1])
    
    # Calculate the total increment to add to the amount of points
    increment = round(sum(clicks[0]))

    # Calculate how number of criticals and points increment from them
    num_criticals = sum([1 for item in clicks[1] if (item == 1)])
    gain_from_criticals = round(gain_from_critical * num_criticals)

    # If critical clicks were rolled, print a message to display information about them
    if gain_from_criticals > 0:
        if num_criticals == 1:
            print(f"Tier {pretty_num(math.ceil(save_data['cc']))} Critical Click! Got {pretty_num(gain_from_criticals)} points.")
        else:
            print(f"Got {pretty_num(gain_from_criticals)} Points from {pretty_num(num_criticals)} Tier {pretty_num(math.ceil(save_data['cc']))} Critical Clicks.")
    
    # Add increment to the amount of points the user has
    save_data["points"] += increment

    # Update the main window to display the new points value
    update_window()

# Calculate the cost of an upgrade
def calc_upgrade_cost(attribute, target_value):

    # Define functions to return the cost of upgrading an attribute to num level(s)
    formulas = {
        "acps" : lambda num: round(1000 * 1.5 ** num),
        "pm" : lambda num: math.ceil(100 * 1.25 ** ((num - 1) * 10)),
        "ppc" : lambda num: 10 * (num % 10) + 200 * min(1, math.floor(num / 10)) * 2 ** (math.floor(num / 10) - 1),
        "cc" : lambda num: math.ceil(10000 * 1.1 ** ((num - 0.01) * 100)),
        "cm" : lambda num: round(100000 + 10000 * (num - 10) * 1.025 ** (num - 10))
    }
    
    # Return the cost for upgrading the attribute to target_value
    return formulas[attribute](target_value)

# Construct the display message for upgrading something
def calc_upgrade_message(attribute, cost):
    # Define the messages for each attribute
    messages = {
        "acps" : "AutoClicks per Second",
        "pm" : "Points Multiplier",
        "ppc" : "Points per Click",
        "cc" : "Critical Click Chance",
        "cm" : "Critical Click Multiplier",
    }

    # Construct a string with the attribute upgraded, amount of times it was upgraded, and the cost of the upgrade
    if save_data["current_buy_amount"] == 1:
        message = f"Upgraded {messages[attribute]} for {pretty_num(cost)} points."
    else:
        message = f'Upgraded {messages[attribute]} {pretty_num(save_data["current_buy_amount"])} times for {pretty_num(cost)} points.'

    # Return the constructed message
    return message

# Handle an upgrade event 
def upgrade(attribute):
    # Access the save_data list for manipulation
    global save_data

    # Find the current level of the attribute and what to increment it by
    prev_amount = save_data[attribute]
    increment = save_data["current_buy_amount"] * increase_per_upgrade[attribute]

    # Find the cost to upgrade the attribute to the target value by taking a series of the upgrades leading up to it
    upgrade_cost = sum([calc_upgrade_cost(attribute, save_data[attribute] + i * increase_per_upgrade[attribute]) for i in range(save_data["current_buy_amount"])])

    # If the user can afford the upgrade, go through with it
    if upgrade_cost <= save_data["points"]:
        # Add the the attribute value
        save_data[attribute] += increment

        # Charge the user for the upgrade(s)
        save_data["points"] -= upgrade_cost

        # Print the transaction information in the console
        print(calc_upgrade_message(attribute, upgrade_cost))

        # Update the window and display costs for upgrades
        update_window()
        update_display_costs()
    else:
        print("You can't afford that upgrade.")

# Find the maximum amount of times an attribute can be upgraded
def find_max_upgrade(attribute):
    # Store the current value of current_buy_amount in save_data
    current_buy_amount = save_data["current_buy_amount"]

    # Find the maximum amount of upgrades that the user can afford for the attribute
    save_data["current_buy_amount"] = 0
    while determine_cost(attribute) <= save_data["points"]:
        save_data["current_buy_amount"] += 1
    max_upgrade_num = save_data["current_buy_amount"] - 1

    # Return current_buy_amount in save_data to its original value
    save_data["current_buy_amount"] = current_buy_amount

    return max_upgrade_num

# Change how many times an upgrade is purchased per button click
def cycle_buy_amount():
    # Access save_data list for manipulation
    global save_data

    # Define the list of options for buy amount per click
    amounts = [1, 10, 25, 100, 1000]

    # Update save_data with the next item in the list, wrapping around when needed
    save_data["current_buy_amount"] = amounts[(amounts.index(save_data["current_buy_amount"]) + 1) % len(amounts)]

    # Log the new current buy amount
    print(f"New buy amount per click: {save_data['current_buy_amount']}")

    # Update the window and upgrade costs
    update_window()
    update_display_costs()

# Toggle whether or not the autobuyer is on
def toggle_autobuyer():
    # Access save_data list for manipulation
    global save_data

    # Toggle the autobuyer on or off
    save_data["autobuyer_state"] = not (save_data["autobuyer_state"])

    # Log the new state of the autobuyer
    autobuyer_states = {True : "on", False : "off"}
    print(f"Autobuyer toggled {autobuyer_states[save_data['autobuyer_state']]}.")

    # Update the window to display current autobuyer state
    update_window()

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

    # Create labels explaining the game mechanics
    pm_info = ttk.Label(info_window, wraplength = window_width, text = f'When clicking, the the Extra Points% is added to the increment (e.g. If you get 10 points after crit and have 130% extra points you would get 23 points from that click).\n', font = info_font)
    ppc_info = ttk.Label(info_window, wraplength = window_width, text = f'Points per click is the base amount of points you get per click.\n', font = info_font)
    acps_info = ttk.Label(info_window, wraplength = window_width, text = f'Autoclicks per second is the amount of times the game automatically clicks for you every second.\n', font = info_font)
    cc_info = ttk.Label(info_window, wraplength = window_width, text = f'Critical chance is the chance of landing a critical click. For values higher than 1, every critical click is guaranteed to multiply the points by critical_multiplier ^ floor(critical_chance), and has a critical_chance % 1 probability of multiplying the points value by critical_multiplier again.\n', font = info_font)
    cm_info = ttk.Label(info_window, wraplength = window_width, text = f'Critical multiplier is how much the points per click is multiplied with upon landing a critical hit.\n', font = info_font)
    cba_info = ttk.Label(info_window, wraplength = window_width, text = f'Cycling the buy amount allows you to buy more than one of an upgrade at a time.\n', font = info_font)
    autobuyer_info = ttk.Label(info_window, wraplength = window_width, text = f'The autobuyer will automatically buy upgrades when you can afford them.\n', font = info_font)
    placeholder_info = ttk.Label(info_window, wraplength = window_width, text = f'Placeholder description.', font = info_font)

    # Pack the labels into the window
    objects = (pm_info, ppc_info, acps_info, cc_info, cm_info, cba_info, autobuyer_info, placeholder_info)
    for info in objects:
        info.pack()

    # Start the mainloop for the window
    info_window.mainloop()

# Placeholder function for placeholder button
def placeholder_function():
    # Indicate that the function has been called
    print("placeholder_function")

# Save the game state to a file for persistence through runs of the code
def save():
    # Open the save file in the assets folder
    save_file = open('assets/save', 'w', encoding = "utf-8")

    # Write the current save_data to the file
    save_file.write(str(save_data))
    
    # Close the file
    save_file.close()

    # Alert the user that the game was saved
    print("Game saved.")

# Handle the user closing the game
def quit_game():
    # Record when the game was closed
    save_data['last_play_time'] = time.time()

    # Save the game to a file
    save()

    # Stop all code
    exit()

# Create the game window and return it
def create_window():
    # Make labels, buttons, and font global so other functions can manipulate them
    global points_text, pm_text, ppc_text, acps_text, cc_text, cm_text, eppc_text, pps_text
    global cba_button, autobuyer_button
    global pm_upgrade_button, ppc_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button
    global text_style

    # Initialize the game window
    game_window = tkinter.Tk()

    # Set the initial dimensions for the game window
    window_width = 350
    window_height = 180

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
    text_style = ttk.Style()
    text_style.configure("TLabel", font=("TkDefaultFont", 12))
    text_style.configure("TButton", font=("TkDefaultFont", 12))

    # Define how many rows and columns the window should have
    # Note: these MUST multiply to a value equal to or greater than the number of widgets the window has
    game_window_rows = 10
    game_window_columns = 2

    # Set a weight for each row and column
    for i in range(game_window_rows):
        game_window.grid_rowconfigure(i, weight = 1)
    for i in range(game_window_columns):
        game_window.grid_columnconfigure(i, weight = 1)

    # Initialize labels for the window
    points_text = ttk.Label(game_window, text = f'')
    pm_text = ttk.Label(game_window, text = f'')
    ppc_text = ttk.Label(game_window, text = f'')
    acps_text = ttk.Label(game_window, text = f'')
    cc_text = ttk.Label(game_window, text = f'')
    cm_text = ttk.Label(game_window, text = f'')
    eppc_text = ttk.Label(game_window, text = f'')
    pps_text = ttk.Label(game_window, text = f'')
    
    # Initialize buttons for the window
    click_button = ttk.Button(game_window, text = "Click", command = click)
    pm_upgrade_button = ttk.Button(game_window, text = f'', command = lambda: upgrade("pm"))
    ppc_upgrade_button = ttk.Button(game_window, text = f'', command = lambda: upgrade("ppc"))
    acps_upgrade_button  = ttk.Button(game_window, text = f'', command = lambda: upgrade("acps"))
    cc_upgrade_button  = ttk.Button(game_window, text = f'', command = lambda: upgrade("cc"))
    cm_upgrade_button  = ttk.Button(game_window, text = f'', command = lambda: upgrade("cm"))
    cba_button  = ttk.Button(game_window, text = f'', command = cycle_buy_amount)
    autobuyer_button  = ttk.Button(game_window, text = f'', command = toggle_autobuyer)
    placeholder_button = ttk.Button(game_window, text = f'Placeholder', command = placeholder_function)
    info_button  = ttk.Button(game_window, text = 'Info', command = display_info)
    save_button  = ttk.Button(game_window, text = "Save", command = save)
    quit_button  = ttk.Button(game_window, text = "Quit", command = quit_game)
    
    # Define list of widgets and place them on the window grid
    widgets = [points_text, pm_text, ppc_text, acps_text, cc_text, cm_text, eppc_text, pps_text, 
               click_button, pm_upgrade_button, ppc_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button,
               cba_button, autobuyer_button, placeholder_button, info_button, save_button, quit_button]
    for widget in widgets:
        widget.grid(row = math.floor(widgets.index(widget) / game_window_columns), column = widgets.index(widget) % game_window_columns, sticky = 'nsew')

    # Bind running quit game to when the window manager closes the window
    game_window.protocol("WM_DELETE_WINDOW", quit_game)

    # Bind adjusting the font size to when the window is moved or resized
    game_window.bind('<Configure>', lambda event: adjust_font_size())

    # Return the constructed window
    return game_window

# Update text labels and some buttons
def update_window():
    # Recalculate point gain expected per click
    expected_points_per_click = round(save_data["ppc"] * save_data["pm"] * save_data["cm"] ** math.floor(save_data["cc"]) * ((1 - save_data["cc"] % 1) + save_data["cm"] * (save_data["cc"] % 1)))

    # Configure all labels to show current values from save_data
    points_text.config(text = f'Points: {pretty_num(round(save_data["points"]))}')
    pm_text.config(text = f'Extra Points: {pretty_num(round((save_data["pm"] - 1) * 100))}%')
    ppc_text.config(text = f'Points Per Click: {pretty_num(save_data["ppc"])}')
    acps_text.config(text = f'AutoClicks Per Second: {pretty_num(save_data["acps"])}')
    cc_text.config(text = f'Critical Chance: {pretty_num(round(save_data["cc"] * 100))}%')
    cm_text.config(text = f'Critical Multiplier: {pretty_num(save_data["cm"])}x')
    eppc_text.config(text = f'Expected Points Per Click: {pretty_num(expected_points_per_click)}')
    pps_text.config(text = f'Points Per Second: {pretty_num(round(points_per_second))}')

    # Configure cycle buy amount button text to display current value from save_data
    cba_button.config(text = f'Cycle Buy Amount (Current: {save_data["current_buy_amount"]})', command = cycle_buy_amount)

    # Configure autobuyer button to display current state from save_data
    autobuyer_states = {False: "Off", True: "On"}
    autobuyer_button.config(text = f'Toggle Autobuyer (State: {autobuyer_states[save_data["autobuyer_state"]]})', command = toggle_autobuyer)

# Update upgrade buttons to display current costs
def update_display_costs():
    # Access and update next_upgrade_costs 
    global next_upgrade_costs
    next_upgrade_costs = {attribute: determine_cost(attribute) for attribute in attributes}


    # Define list of buttons used for upgrades
    upgrade_buttons = [ppc_upgrade_button, pm_upgrade_button, acps_upgrade_button, cc_upgrade_button, cm_upgrade_button]

    # Define list of abbreviations for each attribute to put on upgrade buttons
    upgrade_names = ["PpC", "EP", "aCpS", "CC", "CM"]

    # Update each upgrade button with names and costs
    for i in range(len(upgrade_buttons)):
        upgrade_buttons[i].config(text = f'Upgrade {upgrade_names[i]} (Cost: {pretty_num(next_upgrade_costs[attributes[i]])})', command = lambda to_upgrade = attributes[i]: upgrade(to_upgrade))

# Adjust the font size for the game window
def adjust_font_size():
    # Find the dimensions of the game window
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Define the new font based off of window dimensions
    font_size = max(math.ceil(min(window_width, window_height) / 25), 8)
    new_font = ("TkDefaultFont", font_size)

    # Update labels and buttons with this new font
    text_style.configure("TLabel", font = new_font)
    text_style.configure("TButton", font = new_font)

# Manage recurring timed events
def game_loop():
    # Access prev_points and points_per_second for manipulation
    global prev_points, points_per_second

    # Click autoclicks per second times
    click(save_data["acps"])


    # Calculate how many points were gained/lossed in the last second
    points_per_second = save_data["points"] - prev_points

    # Update prev_points for next points_per_second calculation
    prev_points = save_data["points"]


    # If the autobuyer is active, upgrade each attribute as many times as possible
    if save_data["autobuyer_state"]:
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
            # Store the current state of current_buy_amount in save_data
            current_buy_amount = save_data["current_buy_amount"]

            # Indicate that the following purchases are products of the autobuyer
            print("\nAutobuyer: ")
            
            # Upgrade each attribute in order of auto_upgrade_priority
            for attribute in auto_upgrade_priority:
                # Find the maximum amount of times the attribute can be upgraded
                max_upgrade = find_max_upgrade(attribute)

                # If the attribute can be upgraded, do so
                if max_upgrade > 0:
                    save_data["current_buy_amount"] = max_upgrade
                    upgrade(attribute)
            
            # Visually seperate autobuyer purchases from everything else
            print()

            # Revert current_buy_amount in save_data to the previous quantity
            save_data["current_buy_amount"] = current_buy_amount

            # Update the game window
            update_display_costs()
            update_window()

    # Call game_loop again after 1 second
    window.after(1000, game_loop)

# Define clear commands native to the big three operating systems
clear_commands = {
    "Windows" : "cls",
    "Darwin" : "clear",
    "Linux" : "clear"
}

# Fetch the user's operating system
user_os = platform.system()

# If the clear command for it is known, clear the console
if user_os in clear_commands:
    os.system(clear_commands[user_os])

# If a save file exists, access it, else make one
if os.path.exists('assets/save'):
    # Access the save file and read save data from it
    with open('assets/save', 'r', encoding = "utf-8") as save_file:
        save_data = ast.literal_eval(save_file.read())

    # Calculate how many points the user gained while offline, notify the user, and give them the points
    expected_points_per_click = save_data["ppc"] * save_data["pm"] * save_data["cm"] ** math.floor(save_data["cc"]) * ((1 - save_data["cc"] % 1) + save_data["cm"] * (save_data["cc"] % 1))
    offline_points = round((time.time() - save_data["last_play_time"]) * save_data["acps"] * expected_points_per_click)
    print(f"Gained {pretty_num(offline_points)} points while offline.")
    save_data["points"] += offline_points
else:
    # Create a save file
    save_file = open('assets/save', 'x', encoding = "utf-8")
    save_file.close()

    # Create new save data
    # ppc = Points per click, pm = Points multiplier, acps = Autoclicks per second, cc = Critical chance, cm = Critical multiplier
    save_data = {'points': 0, 'ppc': 1, 'pm': 1, 'acps': 0, 'cc': 0.01, 'cm': 10, 'current_buy_amount': 1, 'autobuyer_state': False, 'last_play_time': time.time()}

# Define attributes that can be upgraded and prioritize them for the autobuyer
attributes = ['ppc', 'pm', 'acps', 'cc', 'cm']
auto_upgrade_priority = ['acps', 'cc', 'ppc', 'pm', 'cm']

# Define how much each attribute should be incremented by per upgrade
increase_per_upgrade = {
    "acps" : 1,
    "pm" : 0.1,
    "ppc" : 1,
    "cc" : 0.01,
    "cm" : 2,
}

# Define function to more consisely find the cost of upgrading a specific attribute a certain amount of times and use it to calculate costs for every attribute
determine_cost = lambda cost_type : sum([calc_upgrade_cost(cost_type, save_data[cost_type] + i * increase_per_upgrade[cost_type]) for i in range(save_data["current_buy_amount"])])
next_upgrade_costs = {attribute: determine_cost(attribute) for attribute in attributes}

# Initialize values used in the game_loop function
prev_points = save_data["points"]
points_per_second = 0

# Create the window and initialize display costs for upgrades
window = create_window()
update_display_costs()

# Start the game loop
game_loop()

# Create the game window
window.mainloop()

