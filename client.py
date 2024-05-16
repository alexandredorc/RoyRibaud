import requests

# URL of the GitHub Pages site
server_url = "https://<your-username>.github.io/<your-repository>"

def send_message(role, message):
    params = {
        'method': 'POST',
        'role': role,
        'message': message
    }
    response = requests.get(server_url, params=params)
    return response.text

def get_game_state():
    params = {
        'method': 'GET'
    }
    response = requests.get(server_url, params=params)
    return response.text

# Example usage
if __name__ == "__main__":
    # Send a message
    role = 'host'  # or 'client'
    message = "Hello from Host"
    send_response = send_message(role, message)
    print(f"Send Response from server: {send_response}")

    # Get the game state
    game_state_response = get_game_state()
    print(f"Game State from server: {game_state_response}")
