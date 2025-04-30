# Snake Game with System Info and Webhook
This is a classic Snake game built using Pygame, enhanced with functionality to report system information and game scores to a Discord webhook.
To be used for educational purposes only. Im not responsible for any damages caused by this script.

##Features
Classic Snake Gameplay: Play the traditional Snake game, eating food to grow and avoiding collisions.

AI Mode: Toggle an AI player that attempts to find the shortest path to the food using Breadth-First Search (BFS).

Adjustable Speed: Change the game speed between Slow, Normal, and Fast.

System Information Reporting: Upon launching the script, it gathers local and public IP addresses, device name, and operating system information and sends a report to a configured Discord webhook.

VPN/Proxy Detection (Optional): Integrates with the IPQualityScore API to attempt to detect if a VPN or proxy is being used (requires an API key).

Game Score Reporting: When a game ends (Game Over), the final score, AI mode status, and game speed are sent to the same Discord webhook.

Interactive Menu: A simple menu allows you to start the game, change speed, and toggle AI mode using mouse clicks or keyboard shortcuts.

##Requirements
Python 3.x

Pygame library

Requests library

##Setup
Install Python: If you don't have Python installed, download and install it from python.org.

Install Required Libraries: Open your terminal or command prompt and run the following command:

pip install pygame requests

Obtain Discord Webhook URL:

In your Discord server, go to Server Settings > Integrations > Create Webhook.

Give your webhook a name and select the channel where messages will be sent.

Copy the Webhook URL.

Obtain IPQualityScore API Key (Optional):

If you want to use the VPN/proxy detection feature, sign up for an account on ipqualityscore.com and obtain an API key. This feature is optional, and the script will still run without it (though VPN detection will be skipped).

##Configuration
Open the snake_game.py (or whatever you named your file) in a text editor and make the following changes:

Discord Webhook URL: Find the line:

discord_webhook_url = "YOUR_DISCORD_WEBHOOK_URL" (line 857)

Replace "YOUR_DISCORD_WEBHOOK_URL" with the Discord webhook URL you copied.

IPQualityScore API Key (Optional): If you obtained an API key from IPQualityScore, find the line:

api_key = "YOUR_IPQUALITYSCORE_API_KEY"

Replace "YOUR_IPQUALITYSCORE_API_KEY" with your actual IPQualityScore API key. If you don't have a key or don't want this feature, leave it as is, and the script will skip the VPN check.

##How to Run
Save the code with your configurations (e.g., as snake_game.py).

Open your terminal or command prompt.

Navigate to the directory where you saved the file.

Run the script using the command:

python snake_game.py

The script will first attempt to gather system information and send it to the webhook. Then, the Pygame window for the Snake game will open.

##Game Controls
Arrow Keys: Move the snake (in manual mode).

A: Toggle AI mode ON/OFF (during gameplay).

S: Change game speed (during gameplay).

Space: Start a new game from the menu or restart after Game Over.

Mouse Click: Interact with menu buttons.

##Notes
The initial system information report is sent when the script starts.

The game over score and settings report is sent when the snake collides.

Using external APIs (ipify.org, ipinfo.io, ipqualityscore.com) may be subject to usage limits.

Ensure your firewall or network settings do not block the script from making outbound requests to the internet for IP information and webhook sending.

Enjoy the game!
