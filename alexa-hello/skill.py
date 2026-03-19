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

# News fetcher: read Vikatan RSS feed and return top headlines
import urllib.request
import xml.etree.ElementTree as ET
import ssl

VIKATAN_RSS = "https://www.vikatan.com/api/v1/collections/latest-news.rss?&time-period=last-24-hours"

def fetch_vikatan_headlines(limit=3):
    try:
        # Create a default context and then disable verification
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(VIKATAN_RSS, timeout=5, context=ctx) as resp:
            data = resp.read()
            print(data)  # Debug: print raw RSS data
        root = ET.fromstring(data)
        # RSS feeds typically have channel/item/title
        titles = []
        for item in root.findall('.//item'):
            title_el = item.find('title')
            if title_el is not None and title_el.text:
                titles.append(title_el.text.strip())
            if len(titles) >= limit:
                break
        print(titles)
        return titles
    except Exception as e:
        print("Error fetching Vikatan RSS feed")
        print(e.__str__)
        return []


class ReadNewsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ReadNewsIntent")(handler_input)

    def handle(self, handler_input):
        headlines = fetch_vikatan_headlines(limit=3)
        if not headlines:
            speech = "Sorry, I couldn't fetch the news right now."
        else:
            speech = "Here are the latest Vikatan headlines: " + " ... ".join(headlines)

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
sb.add_request_handler(ReadNewsIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

lambda_handler = sb.lambda_handler()

if __name__ == "__main__":
    fetch_vikatan_headlines()