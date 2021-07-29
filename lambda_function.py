# -*- coding: utf-8 -*-

# This sample Alexa skill which books ticket from portland to JFK NewYork
# This skill uses skyscanner API to recieve flight details 
# After fetching flight details it allows user to pick a flight and sets a reminder about travel
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import os
import json
import calendar
import requests
from datetime import date as Date
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])


from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Welcome, Let me help in your ticket booking !!! What is your Source, Destination and date of travel ? "
        reprompt_text = "Re-enter your source and destination details"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )



class ReceiveJourneyDetailsIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ReceiveJourneyDetailsIntent")(handler_input)


    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        month = slots["month"].value
        date = slots["date"].value
        destination = slots["destination"].value
        origin = slots["source"].value
        now_date = Date.today()
        current_year = now_date.year
        month_as_index = list(calendar.month_abbr).index(month[:3].title())
        next_travel = Date(current_year, month_as_index, int(date))
        diff_days = (next_travel - now_date).days
        if(diff_days > 0):
            speak_output = "Let me find tickets for your travel from {origin} to {destination} on {month} {date}.".format(origin=origin, destination=destination, month=month, date=date)
        else:
            speak_output = " Date given is invalid "
            return (handler_input.response_builder.speak(speak_output)
                # .ask("Re-enter your source and destination details")
                .response)
        
        url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/PDX-sky/JFK-sky/2021-09-09"
        # .format(next_travel=next_travel)
        headers = {
                    'x-rapidapi-key': "2f10781b51msh9b86969dac021aap1bcf53jsn67d9e956cf54",
                    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
                  }
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()
        res = json.loads(response.text)
        attributes_manager = handler_input.attributes_manager 
        travel_attributes = []
        num_results = len(res.get("Quotes"))
        if(num_results == 0):
            return (handler_input.response_builder.speak("Looks like there are no flights on {month} {date}".format(month=month,date=date))
                # .ask("Re-enter your source and destination details")
                .response)
        for idx, object in enumerate(res.get("Quotes")):
	        price = object.get("MinPrice")
	        direct_ind = object.get("Direct")
	        if(direct_ind):
	            str_ind = "Direct flight "
	        else:
	            str_ind = "Not a direct flight "
	        Airlinesid = int(object.get("OutboundLeg").get("CarrierIds")[0])
	        Airlinesname = res.get("Carriers")[idx].get("Name")
	        dest_Airportname = (res.get("Places")[idx].get("Name"))
	        
	        travel_attributes.append({ "destination" : destination,
                                 "origin"   : origin,
                                # "Travel_date" : month + date
                                "month" : month,
                                "date"  : date,
                                "price" : price,
                                "airlines" : Airlinesname,
                                "CarrierIds" : Airlinesid,
                                "Airportname": dest_Airportname
                             })
	        speak_output = speak_output + "flight {Airlinesid} is a {str_ind} which costs a minimum of {price} dollars run by {Airlinesname} from {Airportname}. Pick a flight number you want to choose".format(Airlinesid=Airlinesid, str_ind=str_ind, price=price, Airlinesname=Airlinesname,Airportname=dest_Airportname)
	        attributes_manager.persistent_attributes = travel_attributes
	        attributes_manager.save_persistent_attributes() 
        

        return (handler_input.response_builder.speak(speak_output)
                # .ask("Re-enter your source and destination details")
                .response)


class CaptureuserinputIntentHandler(AbstractRequestHandler):
    """Handler for travel reminder Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input) and ask_utils.is_intent_name("CaptureuserinputIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        attributes_manager = handler_input.attributes_manager 
        attr = handler_input.attributes_manager.persistent_attributes
        flight_num = slots["flightid"].value
        speak_buf = " You have chosen flight {flight_num}".format(flight_num=flight_num)
        for i in range(len(attr)):
            if (int(attr[i]['CarrierIds']) == int(flight_num)):
                attributes_manager.persistent_attributes = attr
                attributes_manager.save_persistent_attributes() 
                speak_buf = speak_buf + " Your journey details are, CarrierId number {flight_num} run by {airlines} airlines on {month} {date} to {dest_Airportname} airport".format(flight_num=flight_num, airlines = attr[0]['airlines'], month= attr[0]['month'], date= attr[0]['date'], dest_Airportname=attr[0]['Airportname'])
            else:
                speak_buf = speak_buf + " You have chosen wrong flight number . "
        return (
            handler_input.response_builder
                .speak(speak_buf)
                .ask(" Please choose flight id from list prompted. ")
                .response
        )

class RemindertravelIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return  ask_utils.is_request_type("IntentRequest")(handler_input) and ask_utils.is_intent_name("RemindertravelIntent")(handler_input)
    
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        month = attr[0]['month'] 
        date = attr[0]['date']
        now_date = Date.today()
        slots = handler_input.request_envelope.request.intent.slots
        reminder_choice = str(slots["bool"].value)
        if((reminder_choice == "no") or (reminder_choice == "nope")):
            return (
            handler_input.response_builder
                .speak("Is there anything else i can help you with?")
                # .ask("Re-enter the flight details")
                .response)
        current_year = now_date.year
        month_as_index = list(calendar.month_abbr).index(month[:3].title())
        next_travel = Date(current_year, month_as_index, int(date))
        diff_days = (next_travel - now_date).days
        if(diff_days > 0):
            speak_output = "{bool} Travel reminder, it looks like there are {days} more days for your travel which is on {month} {date} to {destination_airport} {destination} from {origin}".format(bool=reminder_choice, days=diff_days, month=attr[0]['month'], date=attr[0]['date'],  destination_airport=attr[0]['Airportname'], destination=attr[0]['destination'], origin=attr[0]['origin'])
        elif(diff_days == 0):
            speak_output = " Today is your travel to {destination_airport} {destination} from {origin} by {flight_id}" .format(destination_airport=attr[0]['Airportname'],destination=attr[0]['destination'],origin=attr[0]['origin'],flight_id=attr[0]['CarrierIds'])
        else:
            speak_output = "It looks like you missed the travel to {destination} on {month} {date}. Do you want any other help? ".format(destination=attr[0]['destination'], month=attr[0]['month'],date=attr[0]['date'])
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("Re-enter the flight details")
                .response
        )



class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


# sb = SkillBuilder()
sb = CustomSkillBuilder(persistence_adapter=s3_adapter)


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ReceiveJourneyDetailsIntentHandler())
sb.add_request_handler(CaptureuserinputIntentHandler())
sb.add_request_handler(RemindertravelIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
# sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
