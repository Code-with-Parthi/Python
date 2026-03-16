import json
import os
from datetime import datetime
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective


def supports_apl(handler_input):
    try:
        return (
            handler_input.request_envelope.context.system.device.supported_interfaces
            .alexa_presentation_apl
            is not None
        )
    except Exception:
        return False


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = "Hello! Welcome to the Hello Sample for Echo Show."
        apl_doc = None
        try:
            with open("apl/hello_apl.json") as f:
                apl_doc = json.load(f)
        except Exception:
            apl_doc = None

        if supports_apl(handler_input) and apl_doc:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="helloToken",
                    document=apl_doc,
                    datasources={}
                )
            )

        handler_input.response_builder.speak(speech).set_should_end_session(True)
        return handler_input.response_builder.response


class HelloIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HelloIntent")(handler_input)

    def handle(self, handler_input):
        speech = "Hello from your Echo Show!"
        handler_input.response_builder.speak(speech).set_should_end_session(True)
        return handler_input.response_builder.response


class ShowTimeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ShowTimeIntent")(handler_input)

    def handle(self, handler_input):
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        speech = f"The current time is {time_str}."
        handler_input.response_builder.speak(speech).set_should_end_session(True)
        return handler_input.response_builder.response


# Grocery list helpers (ephemeral storage using /tmp)
GROCERY_FILE = os.environ.get("GROCERY_FILE", "/tmp/grocery.json")

def load_grocery_list():
    try:
        if os.path.exists(GROCERY_FILE):
            with open(GROCERY_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_grocery_list(items):
    try:
        with open(GROCERY_FILE, "w") as f:
            json.dump(items, f)
    except Exception:
        pass


class CreateListIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CreateListIntent")(handler_input)

    def handle(self, handler_input):
        save_grocery_list([])
        speech = "Created an empty grocery list. You can add items by saying, add milk."
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class AddItemIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AddItemIntent")(handler_input)

    def handle(self, handler_input):
        slots = getattr(handler_input.request_envelope.request.intent, "slots", {})
        item = None
        if slots and "Item" in slots and slots["Item"].value:
            item = slots["Item"].value

        if not item:
            handler_input.response_builder.speak("I didn't catch the item. What would you like to add?").ask("What should I add?")
            return handler_input.response_builder.response

        items = load_grocery_list()
        items.append(item)
        save_grocery_list(items)
        speech = f"Added {item} to your grocery list."
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class RemoveItemIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("RemoveItemIntent")(handler_input)

    def handle(self, handler_input):
        slots = getattr(handler_input.request_envelope.request.intent, "slots", {})
        item = None
        if slots and "Item" in slots and slots["Item"].value:
            item = slots["Item"].value

        if not item:
            handler_input.response_builder.speak("Which item should I remove?").ask("Which item should I remove?")
            return handler_input.response_builder.response

        items = load_grocery_list()
        lowered = [i.lower() for i in items]
        if item.lower() in lowered:
            idx = lowered.index(item.lower())
            removed = items.pop(idx)
            save_grocery_list(items)
            speech = f"Removed {removed} from your grocery list."
        else:
            speech = f"I couldn't find {item} on your list."

        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class ClearListIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ClearListIntent")(handler_input)

    def handle(self, handler_input):
        save_grocery_list([])
        speech = "Cleared your grocery list."
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class ShowListIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ShowListIntent")(handler_input)

    def handle(self, handler_input):
        items = load_grocery_list()
        if not items:
            speech = "Your grocery list is empty."
        else:
            speech = "Your grocery list contains: " + ", ".join(items)

        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloIntentHandler())
sb.add_request_handler(ShowTimeIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

lambda_handler = sb.lambda_handler()
