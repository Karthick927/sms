from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()  # Load .env file

app = Flask(__name__)

# Twilio credentials
ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Available slots (you can modify this)
SLOTS = {
    '1': '9:00 AM - 10:00 AM',
    '2': '10:00 AM - 11:00 AM',
    '3': '11:00 AM - 12:00 PM',
    '4': '2:00 PM - 3:00 PM',
    '5': '3:00 PM - 4:00 PM'
}

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Handle incoming calls"""
    response = VoiceResponse()
    
    gather = Gather(num_digits=1, action='/handle-slot', method='POST')
    gather.say('Welcome to our booking system. Please select a slot.')
    gather.say('Press 1 for 9 AM to 10 AM')
    gather.say('Press 2 for 10 AM to 11 AM')
    gather.say('Press 3 for 11 AM to 12 PM')
    gather.say('Press 4 for 2 PM to 3 PM')
    gather.say('Press 5 for 3 PM to 4 PM')
    
    response.append(gather)
    response.say('We did not receive your selection. Goodbye.')
    
    return str(response)

@app.route("/handle-slot", methods=['POST'])
def handle_slot():
    """Process the slot selection"""
    response = VoiceResponse()
    
    digit = request.form.get('Digits')
    caller_number = request.form.get('From')
    
    if digit in SLOTS:
        slot_time = SLOTS[digit]
        response.say(f'You have selected slot {digit}, which is {slot_time}. Your booking is confirmed.')
        
        # Send SMS confirmation
        try:
            message = client.messages.create(
                body=f"Booking Confirmed! Your slot is: {slot_time}. Thank you!",
                from_=TWILIO_NUMBER,
                to=caller_number
            )
            print(f"SMS sent to {caller_number}: {message.sid}")
        except Exception as e:
            print(f"Error sending SMS: {e}")
    else:
        response.say('Invalid selection. Please try again.')
        response.redirect('/voice')
    
    return str(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
