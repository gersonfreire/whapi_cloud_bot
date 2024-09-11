import requests

# Define API details
api_key = "IggSqEFstZ8K4E7Pt1XMQFGx5bn3a4L5"
api_url = "https://gate.whapi.cloud/messages/text"

# Function to send interactive message
def send_interactive_message(to_number, buttons):
  """
  Sends an interactive message with buttons to a WhatsApp conversation.

  Args:
      to_number: The phone number of the recipient (in international format).
      buttons: A list of dictionaries representing the buttons.
                Each dictionary should have keys: 'title' (text on button) 
                and 'id' (unique identifier for the button).
  """
  payload = {
    "api_key": api_key,
    "to": to_number,
    "text": "Select an option:",
    "type": "interactive",
    "buttons": buttons
  }

  response = requests.post(api_url + "messages/interactive", json=payload)

  if response.status_code == 200:
    print("Interactive message sent successfully!")
  else:
    print("Error sending message:", response.text)

# Example usage
buttons = [
  {"title": "Option 1", "id": "1"},
  {"title": "Option 2", "id": "2"},
  {"title": "Option 3", "id": "3"}
]

send_interactive_message("+5527996012345", buttons)
# This will send an interactive message with 3 buttons to the number +15555555555.
# The buttons will have the titles "Option 1", "Option 2", and "Option 3".
