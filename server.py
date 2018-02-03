import re

from flask import Flask, request
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.twiml.messaging_response import Message, MessagingResponse

from config import PRIVATE_NUMBER, TWILIO_NUMBER

app = Flask(__name__)


@app.route('/sms', methods=['POST'])
def sms():
    from_number = request.form['From']
    msg_body = request.form['Body']

    if from_number == PRIVATE_NUMBER:  # if I am sending the sms
        msg, to_number = decode_message(msg_body)
        return send_message(msg, to_number)
    else:  # if an attendee is sending the sms
        msg = encode_message(msg_body, from_number)
        return send_message(msg, PRIVATE_NUMBER)


@app.route('/call', methods=['GET', 'POST'])
def call():
    from_number = request.form['From']

    if from_number != PRIVATE_NUMBER:  # if an attendee is calling
        return perform_call(PRIVATE_NUMBER)
    else:  # if I am calling
        response = VoiceResponse()
        g = Gather(action="/aliasing", finish_on_key="#", method="POST")
        g.say("Hello Gorgeous. Dial the number you want to call followed by the hash symbol.")
        response.append(g)
        return str(response)


@app.route("/aliasing", methods=['GET', 'POST'])
def aliasing():
    # Get the digit pressed by the user
    number = request.values.get('Digits')

    if number:
        return perform_call(number, TWILIO_NUMBER)
    return "Aliasing failed."


def perform_call(number, caller_id=None):
    response = VoiceResponse()
    # Connect the dialed number to the incoming caller.
    response.dial(number, caller_id=caller_id)
    return str(response)


def send_message(msg, number):
    response = MessagingResponse()
    response.message(msg, to=number, from_=TWILIO_NUMBER)
    return str(response)


def encode_message(msg, number):
    return "{}: {}".format(number, msg)


def decode_message(msg):
    pattern = re.compile('^\+\d*')
    number = pattern.match(msg).group()
    body = msg[len(number) + 2:]
    return body, number


if __name__ == '__main__':
    app.run()
