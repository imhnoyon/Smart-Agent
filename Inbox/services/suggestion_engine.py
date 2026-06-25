import re
RULES = [
    {
        "patterns": [r"refund", r"money\s*back", r"reimburse"],
        "response": (
            "We are sorry for the inconvenience.."
            
        ),
    },
    {
        "patterns": [r"cancel", r"unsubscribe", r"close\s*account"],
        "response": (
            "Sorry to see you go! To process your cancellation, could you confirm "
            "the email address on your account?"
        ),
    },
    {
        "patterns": [r"billing", r"invoice", r"charge", r"payment"],
        "response": (
            "Happy to help with your billing question. Which transaction or invoice "
            "are you referring to?"
        ),
    },
    {
        "patterns": [r"not\s*working", r"broken", r"bug", r"error", r"crash"],
        "response": (
            "Sorry you're running into this! Please share your browser, OS, and "
            "any error message."
        ),
    },
]

DEFAULT_RESPONSE = (
    "Thanks for reaching out! Could you provide more details?"
)


def get_suggestion(message):
    if not message:
        return DEFAULT_RESPONSE

    message = message.strip()

    for rule in RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, message, re.IGNORECASE):
                return rule["response"]

    return DEFAULT_RESPONSE