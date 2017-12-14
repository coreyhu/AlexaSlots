import random


# Helpers that build all of the responses


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# Functions that control the skill's behavior

def get_welcome_response():
    session_attributes = {'balance': 100}
    card_title = "Welcome"
    speech_output = "Beepity deepity. I'm a slot machine. Here's $100. Cha-ching. " \
                    "How much would you like to bet? " \
                    "deep doop beep boop"
    reprompt_text = "Beep bop. Not sure what you said. How much would you like to bet? " \
                    "You can bet by saying" \
                    "I'd like to bet 4 dollars"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Wise choice. Your ending balance is" \
                    "But it's all fake anyway!"

    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def add_to_balance(amount, session):
    current_balance = 0
    if session.get('attributes', {}) and "balance" in session.get('attributes', {}):
        current_balance = session['attributes']['balance']
    return {'balance': current_balance + amount}


def set_color_in_session(intent, session):
    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = False

    if 'betAmount' in intent['slots']:
        bet_amount = int(intent['slots']['betAmount']['value'])
        balance = session_attributes['balance']

        if bet_amount > balance:
            session_attributes = {'balance': balance}
            speech_output = "Nice try. You only have " + str(balance) + ". Try again or say quit"
            reprompt_text = None
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

        earnings = random.randint(0, 2 * bet_amount)
        descriptor = 'gain ' if earnings > bet_amount else 'lose '

        session_attributes = add_to_balance(earnings - bet_amount, session)
        balance = session_attributes.get('balance')

        speech_output = "Bopity beepity. Putting in " + str(bet_amount) + " dollars. " \
                                                                       "Ka-ching. You " + descriptor \
                        + str(earnings - bet_amount) + " dollars. Your current balance is " + str(balance) + " dollars. "

        if balance <= 0:
            speech_output += "Tragic, you're broke and worthless. Better luck next time!"
            should_end_session = True
            reprompt_text = None
        else:
            speech_output += "How much would you like to bet? Or say quit to quit."
            reprompt_text = "How much would you like to bet? Or say quit to quit. " \
                            "Or ask for your balance by asking, " \
                            "what's my balance?"
    else:
        speech_output = "I'm not sure how much you'd like to bet. " \
                        "Try again."
        reprompt_text = "I'm not sure how much you'd like to bet. " \
                        "You can tell me how much you'd like to bet by saying, " \
                        "I'd like to bet 4 dollars."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_balance_from_session(intent, session):
    session_attributes = session.get('attributes')
    reprompt_text = None

    if session.get('attributes', {}) and 'balance' in session.get('attributes', {}):
        balance = session['attributes']['balance']
        speech_output = "Your balance is " + balance
    else:
        speech_output = "Your balance is zero."

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, False))


# Events

def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "SpinIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "BalanceIntent":
        return get_balance_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
