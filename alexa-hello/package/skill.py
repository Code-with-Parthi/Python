import json
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
