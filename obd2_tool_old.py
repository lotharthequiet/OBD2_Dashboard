import pygame
import sys
import math
import obd
import json

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 800
FPS = 60
GRAY = (192, 192, 192)
DARK_GRAY = (32, 32, 32)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FONT_SIZE = 24
APP_TITLE = "OBD-II Tool"
# Start positions for the gauge needles.
SPEEDOMETER_START = 210
TACHOMETER_START = 225
FUEL_START = 225
TEMP_START = 315

# Initial values set to zero
current_mode = "Dashboard"  # Default mode
speed = 0
rpm = 0
battery_voltage = 0
engine_temperature = 0
oil_pressure = 0
fuel_level = 0
gear = "P"

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"{APP_TITLE}")

# Load font
font = pygame.font.Font(None, FONT_SIZE)

def load_obd2_codes(filename='obd2_codes.json'):
    with open(filename, 'r') as json_file:
        try:
            obd2_codes = json.load(json_file)
        except:
            print("Error loading DTC JSON file.")
        else:
            print("DTC JSON file loaded.")
    return obd2_codes

def draw_gauge_needle(screen, center_x, center_y, angle, length, needle_color):
    x = int(center_x + length * math.cos(angle))
    y = int(center_y - length * math.sin(angle))
    x_thick = int(center_x + 10 * math.cos(angle))
    y_thick = int(center_y - 10 * math.sin(angle))

    pygame.draw.polygon(screen, needle_color, [(x, y), (x_thick, y_thick + 5), (x_thick, y_thick - 5)])

# Define a function to draw the instrument
def draw_instrument(center_x, center_y, value, max_value, bezel_color, size_ratio, needle_color, needle_start):
    gauge_radius = int(120 * size_ratio)
    pygame.draw.circle(screen, bezel_color, (center_x, center_y), gauge_radius + 5)
    pygame.draw.circle(screen, WHITE, (center_x, center_y), gauge_radius)

    #angle = math.radians(90 + value / max_value * 180)
    angle = math.radians(needle_start + value / max_value * 180)

    draw_gauge_needle(screen, center_x, center_y, angle, gauge_radius, needle_color)

def draw_shiftindicator(center_x, center_y, gear, color):
    button_width = 50
    button_height = 50
    font = pygame.font.Font(None, 36)
    pygame.draw.rect(screen, color, (center_x - button_width // 2, center_y - button_height // 2, button_width, button_height))
    button_text = font.render(f"{gear}", True, WHITE)
    button_text_rect = button_text.get_rect(center=(center_x, center_y))
    screen.blit(button_text, button_text_rect)

def draw_separator(center_x, center_y, color):
    rect_width = 550
    rect_height = 250
    pygame.draw.rect(screen, color, (center_x - rect_width // 2, center_y - rect_height // 2, rect_width, rect_height))

def draw_infocenter(center_x, center_y, color, bezelcolor, fontsize):
    rect_width = 150
    rect_height = 200
    bezel_width = 5
    pygame.draw.rect(screen, bezelcolor, (center_x - rect_width // 2 - bezel_width, center_y - rect_height // 2 - bezel_width, rect_width + 2 * bezel_width, rect_height + 2 * bezel_width))
    pygame.draw.rect(screen, color, (center_x - rect_width // 2, center_y - rect_height // 2, rect_width, rect_height))

def draw_tachometer_labels(center_x, center_y):
    font = pygame.font.Font(None, 24)
    label_radius = int(140 * .9)
    labels = ["0", "1", "2", "3", "4", "5", "6", "7"]

    for angle, label in zip(range(-135, 136, 35), labels):
        angle_rad = math.radians(90 - angle)  # Change the sign to make it clockwise
        x = int(center_x + label_radius * math.cos(angle_rad))
        y = int(center_y - label_radius * math.sin(angle_rad))
        label_rendered = font.render(label, True, BLACK)
        label_rect = label_rendered.get_rect(center=(x, y))
        screen.blit(label_rendered, label_rect)

def draw_speedometer_labels(center_x, center_y, max_speed):
    font = pygame.font.Font(None, 24)
    label_radius = int(140 * .9)
    
    for speed in range(0, max_speed + 1, 10):
        angle = 210 - 1.3 * (speed / max_speed) * 180  # Starting at 7 o'clock position
        angle_rad = math.radians(angle)
        x = int(center_x + label_radius * math.cos(angle_rad))
        y = int(center_y - label_radius * math.sin(angle_rad))
        
        label = font.render(str(speed), True, BLACK)  # Font color set to BLACK
        label_rect = label.get_rect(center=(x, y))
        screen.blit(label, label_rect)

def draw_fuel_gauge_labels(center_x, center_y, label_color):
    font_base = pygame.font.Font(None, 14)
    label_radius = int(85 * .9)
    label_text = "--------------------"

    for i in range(len(label_text)):
        char = label_text[i]
        size_factor = 1.0  # Default size factor

        # Apply size and bold formatting based on position
        if i == 0 or i == len(label_text) - 1:
            size_factor = 3.0  # First and last characters: 3x size
            font_base.set_bold(True)
        elif i == 4 or i == 9 or i == 14:
            size_factor = 2.0  # 5th, 10th, and 15th characters: 2x size
            font_base.set_bold(True)
        else:
            font_base.set_bold(False)

        # Render the label with the specified size and formatting
        font_size = int(14 * size_factor)
        font = pygame.font.Font(None, font_size)
        if font_base.get_bold():
            font.set_bold(True)

        angle = 315 + i * 12  # Adjust angle based on label count (12 degrees between each label)
        angle_rad = math.radians(angle)
        x = int(center_x + label_radius * math.cos(angle_rad))
        y = int(center_y - label_radius * math.sin(angle_rad))

        label_rendered = font.render(char, True, label_color)  # Use the specified label color
        label_rect = label_rendered.get_rect(center=(x, y))
        screen.blit(label_rendered, label_rect)


# Define a function to draw the dashboard screen
def draw_dashboard_screen(engine_temperature, speed, rpm, fuel_level):
    screen.fill(BLACK)
    draw_separator(800, 400, DARK_GRAY)
    draw_infocenter(800, 400, BLACK, GRAY, 24)
    draw_instrument(655, 210, engine_temperature, 100, BLACK, 2/3, RED, TEMP_START)    # Temp
    draw_instrument(515, 360, rpm, 8000, GRAY, 1.3, RED, TACHOMETER_START)             # Tachometer
    draw_tachometer_labels(515, 360)                                            # Tachometer Labels
    draw_shiftindicator(800, 225, gear, BLUE)
    draw_instrument(945, 210, fuel_level, 100, BLACK, 2/3, RED, FUEL_START)            # Fuel
    draw_fuel_gauge_labels(945, 210, RED)
    draw_instrument(1085, 360, speed, 120, GRAY, 1.3, RED, SPEEDOMETER_START)            # Speedometer
    draw_speedometer_labels(1085, 360, 120)                                     # Speedometer Labels

def draw_sensors_screen(engine_temperature, speed, rpm, fuel_level):
    screen.fill(BLACK)

def draw_diagnostics_screen(engine_temperature, speed, rpm, fuel_level):
    screen.fill(BLACK)

def draw_log_screen(engine_temperature, speed, rpm, fuel_level):
    screen.fill(BLACK)

# Define a function to draw the mode button
def draw_mode_button(mode):
    button_width = 125
    button_height = 50
    pygame.draw.rect(screen, BLUE, (25, HEIGHT - button_height, button_width, button_height))
    
    button_text = font.render(f"{mode}", True, WHITE)
    button_text_rect = button_text.get_rect(center=(25 + button_width // 2, HEIGHT - button_height // 2))
    screen.blit(button_text, button_text_rect)

def poll_dashboard_info():
    connection = obd.OBD()  # auto-connect to USB or RF port

    if connection.is_connected():
        # Speed
        speed_cmd = obd.commands.SPEED
        speed_response = connection.query(speed_cmd)
        speed = speed_response.value.magnitude if speed_response.success else None

        # RPM (Engine Revolutions Per Minute)
        rpm_cmd = obd.commands.RPM
        rpm_response = connection.query(rpm_cmd)
        rpm = rpm_response.value.magnitude if rpm_response.success else None

        # Fuel Level
        fuel_cmd = obd.commands.FUEL_LEVEL
        fuel_response = connection.query(fuel_cmd)
        fuel_level = fuel_response.value.magnitude if fuel_response.success else None

        # Engine Coolant Temperature
        temp_cmd = obd.commands.COOLANT_TEMP
        temp_response = connection.query(temp_cmd)
        engine_temp = temp_response.value.magnitude if temp_response.success else None

        # Transmission Fluid Temperature (for automatic transmissions)
        trans_temp_cmd = obd.commands.TRANSMISSION_TEMP
        trans_temp_response = connection.query(trans_temp_cmd)
        trans_temp = trans_temp_response.value.magnitude if trans_temp_response.success else None

        # Current Gear (for automatic transmissions)
        gear_cmd = obd.commands.THROTTLE_POS
        gear_response = connection.query(gear_cmd)
        current_gear = gear_response.value.magnitude if gear_response.success else None

        # Print the retrieved information
        print(f"Vehicle Speed: {speed} km/h")
        print(f"Engine RPM: {rpm} RPM")
        print(f"Fuel Level: {fuel_level}%")
        print(f"Engine Temperature: {engine_temp} °C")
        print(f"Transmission Fluid Temperature: {trans_temp} °C")
        print(f"Current Gear: {current_gear}")

    else:
        print("Connection to OBD-II port failed.")

def get_dtc():
    # Connect to the OBD-II adapter (make sure it's plugged in)
    connection = obd.OBD()

    # Check if the connection was successful
    if not connection.is_connected():
        print("Error: Unable to connect to OBD-II adapter")
        return

    # Query for trouble codes
    response = connection.query(obd.commands.GET_DTC)

    # Check if the query was successful
    if response.is_null():
        print("Error: Unable to retrieve trouble codes")
        return

    # Print the retrieved trouble codes
    for dtc in response.value:
        print(f"Diagnostic Trouble Code: {dtc.code}, Description: {dtc.description}")

    # Close the OBD-II connection
    connection.close()

running = True
DiagTroubleCodes = load_obd2_codes()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if 25 <= event.pos[0] <= 125 and HEIGHT - 50 <= event.pos[1] <= HEIGHT:
                # Switch between Dash, Sensors, Diag modes
                if current_mode == "Dashboard":
                    current_mode = "Sensors"
                elif current_mode == "Sensors":
                    current_mode = "Diagnostics"
                elif current_mode == "Diagnostics":
                    current_mode = "Logs"
                else:
                    current_mode = "Dashboard"

    # Draw
    if current_mode == "Dashboard":
        pygame.display.set_caption(f"OBD-II Tool - {current_mode}")
        draw_dashboard_screen(engine_temperature, speed, rpm, fuel_level)
    if current_mode == "Sensors":
        pygame.display.set_caption(f"OBD-II Tool - {current_mode}")
        draw_sensors_screen(engine_temperature, speed, rpm, fuel_level)
    if current_mode == "Diagnostics":
        pygame.display.set_caption(f"OBD-II Tool - {current_mode}")
        draw_diagnostics_screen(engine_temperature, speed, rpm, fuel_level)
    if current_mode == "Logs":
        pygame.display.set_caption(f"OBD-II Tool - {current_mode}")
        draw_log_screen(engine_temperature, speed, rpm, fuel_level)

    draw_mode_button(current_mode)

    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(FPS)

pygame.quit()
sys.exit()
