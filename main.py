from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import csv
import threading
import time
import os

# Global listener objects
mouse_listener = None
keyboard_listener = None

# Lists to store positions and keyboard inputs
pos = []
posx = []
posy = []
keys = []
timestamps = []

# the filepath for the location you put the program
# e.g. "C:\\python\\"
program_location = os.path.dirname(os.path.realpath(__file__))

# Initialize mouse and keyboard controllers
mouse_controller = MouseController()
keyboard_controller = KeyboardController()

#global time variable
last_event_time = None

def on_click(x, y, button, pressed):
    global last_event_time
    if pressed:
        current_time = time.time()
        if last_event_time is not None:
            time_diff = (current_time - last_event_time) * 1000  # Convert to milliseconds
        else:
            time_diff = 0  # No previous event, so time difference is 0
        last_event_time = current_time
        pos.append((x, y))
        posx.append(x)
        posy.append(y)
        keys.append('clicked')
        timestamps.append(time_diff)
        print(f"Mouse position recorded: ({x}, {y}) with delay {time_diff} ms")

def on_press(key):
    global last_event_time
    current_time = time.time()
    if last_event_time is not None:
        time_diff = (current_time - last_event_time) * 1000  # Convert to milliseconds
    else:
        time_diff = 0  # No previous event, so time difference is 0
    last_event_time = current_time
    try:
        if key == Key.space:
            keys.append('space')
        elif key == Key.backspace:
            keys.append('backspace')
        else:
            keys.append(key.char)
        posx.append('')  # Add placeholder for posx
        posy.append('')  # Add placeholder for posy
        timestamps.append(time_diff)
        print(f"Key pressed: {key} with delay {time_diff} ms")
    except AttributeError:
        keys.append(str(key))
        posx.append('')  # Add placeholder for posx
        posy.append('')  # Add placeholder for posy
        timestamps.append(time_diff)
        print(f"Special key pressed: {key} with delay {time_diff} ms")
        
def start_mouse_listener():
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    mouse_listener.join()

def start_keyboard_listener():
    global keyboard_listener
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    keyboard_listener.join()

def read_csv(file_path):
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            rows = [row for row in reader]
        return rows
    except FileNotFoundError:
        return f"Error: The file at {file_path} was not found."
    except PermissionError:
        return f"Error: Permission denied for file at {file_path}."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def save_to_csv(output_file_path, posx, posy, keys):
    try:
        with open(output_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['posx', 'posy', 'keys','timestamps'])
            for i in range(len(keys)):
                writer.writerow([posx[i], posy[i], keys[i], timestamps[i]])
    except Exception as e:
        print(f"An error occurred while saving to CSV: {e}")

def move_mouse_and_click():
    print("Starting mouse movement and click/key press operations")
    for idx in range(len(keys)):
        # Sleep for the recorded time before performing the next action
        time.sleep(timestamps[idx] / 1000.0)  # Convert milliseconds to seconds

        if keys[idx] == 'clicked':
            x = int(posx[idx]) * 2 / 3
            y = int(posy[idx]) * 2 / 3
            print(f"Moving to ({x}, {y}) and clicking")
            mouse_controller.position = (x, y)
            time.sleep(0.1)  # Pause to observe the movement
            mouse_controller.click(Button.left, 1)
            print(f"Clicked at ({x}, {y})")
        else:
            key_action = keys[idx]
            print(f"Pressing key '{key_action}'")
            try:
                if key_action == 'space':
                    keyboard_controller.press(Key.space)
                    keyboard_controller.release(Key.space)
                elif key_action == 'backspace':
                    keyboard_controller.press(Key.backspace)
                    keyboard_controller.release(Key.backspace)
                elif key_action == 'enter':
                    keyboard_controller.press(Key.enter)
                    keyboard_controller.release(Key.enter)
                elif key_action == 'shift':
                    keyboard_controller.press(Key.shift)
                    keyboard_controller.release(Key.shift)
                elif hasattr(Key, key_action):
                    key_to_press = getattr(Key, key_action)
                    keyboard_controller.press(key_to_press)
                    keyboard_controller.release(key_to_press)
                else:
                    keyboard_controller.press(key_action)
                    keyboard_controller.release(key_action)
            except ValueError:
                print(f"Failed to press key '{key_action}'")
            print(f"Pressed key '{key_action}'")


def record_new_file():
    # Start the listeners in separate threads
    mouse_thread = threading.Thread(target=start_mouse_listener)
    keyboard_thread = threading.Thread(target=start_keyboard_listener)
    
    mouse_thread.start()
    keyboard_thread.start()

    print("Listening for mouse clicks and keyboard inputs... Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive while the listeners are running
        while mouse_thread.is_alive() and keyboard_thread.is_alive():
            mouse_thread.join(0.1)
            keyboard_thread.join(0.1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught. Exiting gracefully.")
        if mouse_listener:
            mouse_listener.stop()
        if keyboard_listener:
            keyboard_listener.stop()
        mouse_thread.join()
        keyboard_thread.join()
        keys.pop()
        keys.pop()

        # Print recorded positions and keyboard inputs
        print("All mouse positions:", pos)
        print("X positions:", posx)
        print("Y positions:", posy)
        print("Keyboard inputs:", keys)
        print("Timestamps:", timestamps)

        # Ask user for the output CSV file name
        output_file_name = input("Enter the name of the CSV file to save: ")
        output_file_path = f"{program_location}\\scripts\\{output_file_name}.csv"
        print(f"File path: {output_file_path}")  # Print the file path for debugging
        print(f"Lengths: posx={len(posx)}, posy={len(posy)}, keys={len(keys)}")  # Debugging lengths
        save_to_csv(output_file_path, posx, posy, keys)
        print(f"Data saved to {output_file_path}")
def main(): 
    is_new_file = input("New script? (y/n): ").lower() == 'y'
    if is_new_file:
        # Start new file recording if is_new_file is True
        record_new_file()
    else:
        file_name = input("Enter the name of the CSV file to read: ")
        file_path = f"{program_location}\\scripts\\{file_name}.csv"
        print(f"File path: {file_path}")  # Print the file path for debugging
        file_contents = read_csv(file_path)
        if isinstance(file_contents, list):
            print("File contents:")
            for row in file_contents:
                print(row)
            # Move the mouse and click based on the CSV file contents
            global posx, posy, keys
            posx = [row['posx'] for row in file_contents]
            posy = [row['posy'] for row in file_contents]
            keys = [row['keys'] for row in file_contents]
            timestamps = [row['timestamps'] for row in file_contents]
            print(f"Lengths: posx={len(posx)}, posy={len(posy)}, keys={len(keys)}, timestamps={len(timestamps)}")  # Debugging lengths
            print("Positions read from CSV:")
            print(f"posx: {posx}")
            print(f"posy: {posy}")
            move_mouse_and_click()
        else:
            print(file_contents)

if __name__ == "__main__":
    main()
