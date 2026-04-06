import json
import os
from datetime import datetime
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

# Data storage: using /tmp for ephemeral storage (use DynamoDB for production)
CLASSES_FILE = os.environ.get("CLASSES_FILE", "/tmp/kid_classes.json")

def load_classes():
    try:
        if os.path.exists(CLASSES_FILE):
            with open(CLASSES_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_classes(classes):
    try:
        with open(CLASSES_FILE, "w") as f:
            json.dump(classes, f, indent=2)
    except Exception:
        pass

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = "Welcome to Kid's Classes Manager. You can add a class, list classes, record attendance, or check payment reminders. What would you like to do?"
        handler_input.response_builder.speak(speech).ask("What would you like to do?")
        return handler_input.response_builder.response

class AddClassIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AddClassIntent")(handler_input)

    def handle(self, handler_input):
        slots = getattr(handler_input.request_envelope.request.intent, "slots", {})
        class_name = None
        day = None
        time = None
        instructor = None
        cost = None

        if slots:
            if "ClassName" in slots and slots["ClassName"].value:
                class_name = slots["ClassName"].value
            if "Day" in slots and slots["Day"].value:
                day = slots["Day"].value
            if "Time" in slots and slots["Time"].value:
                time = slots["Time"].value
            if "Instructor" in slots and slots["Instructor"].value:
                instructor = slots["Instructor"].value
            if "Cost" in slots and slots["Cost"].value:
                cost = slots["Cost"].value

        if not class_name:
            handler_input.response_builder.speak("What is the name of the class?").ask("Class name?")
            return handler_input.response_builder.response

        classes = load_classes()
        class_id = class_name.lower().replace(" ", "_")
        
        classes[class_id] = {
            "name": class_name,
            "day": day or "Not set",
            "time": time or "Not set",
            "instructor": instructor or "Not set",
            "cost": cost or "Not set",
            "attendance": [],
            "payment_status": "pending"
        }
        save_classes(classes)
        
        speech = f"Added {class_name} to the schedule."
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response

class ListClassesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ListClassesIntent")(handler_input)

    def handle(self, handler_input):
        classes = load_classes()
        
        if not classes:
            speech = "No classes added yet. You can add one by saying add a class."
        else:
            speech = "Here are the classes: "
            for class_id, info in classes.items():
                speech += f"{info['name']} on {info['day']} at {info['time']}, taught by {info['instructor']}. "
        
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response

class RecordAttendanceIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("RecordAttendanceIntent")(handler_input)

    def handle(self, handler_input):
        slots = getattr(handler_input.request_envelope.request.intent, "slots", {})
        class_name = None
        attendance = None

        if slots:
            if "ClassName" in slots and slots["ClassName"].value:
                class_name = slots["ClassName"].value
            if "AttendanceStatus" in slots and slots["AttendanceStatus"].value:
                attendance = slots["AttendanceStatus"].value

        if not class_name:
            handler_input.response_builder.speak("Which class?").ask("Which class?")
            return handler_input.response_builder.response

        if not attendance:
            handler_input.response_builder.speak("Did the child attend or miss?").ask("Attend or miss?")
            return handler_input.response_builder.response

        classes = load_classes()
        class_id = class_name.lower().replace(" ", "_")
        
        if class_id not in classes:
            speech = f"Class {class_name} not found."
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            record = {"date": today, "status": attendance}
            classes[class_id]["attendance"].append(record)
            save_classes(classes)
            speech = f"Recorded {attendance} for {class_name} on {today}."
        
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response

class CheckPaymentIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CheckPaymentIntent")(handler_input)

    def handle(self, handler_input):
        slots = getattr(handler_input.request_envelope.request.intent, "slots", {})
        class_name = None

        if slots and "ClassName" in slots and slots["ClassName"].value:
            class_name = slots["ClassName"].value

        classes = load_classes()
        
        if not class_name:
            # Return payment status for all classes
            speech = "Payment status: "
            for class_id, info in classes.items():
                speech += f"{info['name']} is {info['payment_status']}. "
        else:
            class_id = class_name.lower().replace(" ", "_")
            if class_id not in classes:
                speech = f"Class {class_name} not found."
            else:
                status = classes[class_id].get("payment_status", "unknown")
                cost = classes[class_id].get("cost", "Not set")
                speech = f"Payment for {class_name} is {status}. Cost is {cost}."
        
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response

class UpdatePaymentIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("UpdatePaymentIntent")(handler_input)

    def handle(self, handler_input):
        slots = getattr(handler_input.request_envelope.request.intent, "slots", {})
        class_name = None
        payment_status = None

        if slots:
            if "ClassName" in slots and slots["ClassName"].value:
                class_name = slots["ClassName"].value
            if "PaymentStatus" in slots and slots["PaymentStatus"].value:
                payment_status = slots["PaymentStatus"].value

        if not class_name or not payment_status:
            handler_input.response_builder.speak("Please specify the class and payment status.").ask("Class and status?")
            return handler_input.response_builder.response

        classes = load_classes()
        class_id = class_name.lower().replace(" ", "_")
        
        if class_id not in classes:
            speech = f"Class {class_name} not found."
        else:
            classes[class_id]["payment_status"] = payment_status
            save_classes(classes)
            speech = f"Updated {class_name} payment status to {payment_status}."
        
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response

class AttendanceReportIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AttendanceReportIntent")(handler_input)

    def handle(self, handler_input):
        slots = getattr(handler_input.request_envelope.request.intent, "slots", {})
        class_name = None

        if slots and "ClassName" in slots and slots["ClassName"].value:
            class_name = slots["ClassName"].value

        classes = load_classes()
        
        if not class_name:
            speech = "Please specify which class."
        else:
            class_id = class_name.lower().replace(" ", "_")
            if class_id not in classes:
                speech = f"Class {class_name} not found."
            else:
                attendance_records = classes[class_id].get("attendance", [])
                total = len(attendance_records)
                attended = sum(1 for r in attendance_records if r["status"].lower() in ["attended", "present", "yes"])
                
                if total == 0:
                    speech = f"No attendance records for {class_name}."
                else:
                    rate = (attended / total) * 100
                    speech = f"{class_name}: {attended} out of {total} classes attended, that's {rate:.0f}% attendance rate."
        
        handler_input.response_builder.speak(speech).set_should_end_session(False)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddClassIntentHandler())
sb.add_request_handler(ListClassesIntentHandler())
sb.add_request_handler(RecordAttendanceIntentHandler())
sb.add_request_handler(CheckPaymentIntentHandler())
sb.add_request_handler(UpdatePaymentIntentHandler())
sb.add_request_handler(AttendanceReportIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

lambda_handler = sb.lambda_handler()
