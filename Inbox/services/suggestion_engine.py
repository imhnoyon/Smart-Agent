# import re

# class BaseSuggestionProvider:
#     def suggest(self, message_text: str) -> str:
#         raise NotImplementedError("Suggestion providers must implement the suggest method.")

# class PatternRule:
#     def __init__(self, patterns, template):
#         # List of regex pattern strings
#         self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
#         self.template = template

#     def matches(self, text):
#         return any(pattern.search(text) for pattern in self.patterns)

# class RuleBasedSuggestionProvider(BaseSuggestionProvider):
#     def __init__(self):
#         # Extensible rule matrix
#         self.rules = [
#             PatternRule(
#                 patterns=[r"refund", r"money\s*back", r"reimburse"],
#                 template=(
#                     "We are sorry for the inconvenience... "
    
#                 )
#             ),
#             PatternRule(
#                 patterns=[r"cancel", r"unsubscribe", r"close\s*account"],
#                 template=(
#                     "Thank you for contacting us. We're sorry to see you go! To assist with "
#                     "cancelling your subscription or closing your account, please confirm the email "
#                     "address associated with your account. We will handle the cancellation right away."
#                 )
#             ),
#             PatternRule(
#                 patterns=[r"billing", r"invoice", r"charge", r"payment"],
#                 template=(
#                     "I understand you have a question regarding billing. Could you please provide "
#                     "details of the specific transaction or invoice you're referencing? I'd be happy "
#                     "to look into this charge for you."
#                 )
#             ),
#             PatternRule(
#                 patterns=[r"not\s*working", r"broken", r"bug", r"error", r"crash"],
#                 template=(
#                     "We apologize for the technical issue you're experiencing. To help us troubleshoot, "
#                     "could you please provide your browser/OS version, and a screenshot or the exact error "
#                     "message if possible? We want to get this resolved for you as quickly as possible."
#                 )
#             ),
#             PatternRule(
#                 patterns=[r"hello", r"hi", r"hey", r"greetings"],
#                 template=(
#                     "Hello! Thanks for reaching out to customer support. How can I assist you today?"
#                 )
#             ),
#         ]
#         self.default_template = (
#             "We are sorry for the inconvenience... "
#         )

#     def suggest(self, message_text: str) -> str:
#         if not message_text:
#             return self.default_template

#         for rule in self.rules:
#             if rule.matches(message_text):
#                 return rule.template

#         return self.default_template

# # Global instance for easy imports and dependency injection
# suggestion_engine = RuleBasedSuggestionProvider()



import re

RULES = [
    {
        "patterns": [r"refund", r"money\s*back", r"reimburse"],
        "response": (
            "We're sorry to hear you'd like a refund. Could you share your order ID "
            "or the email used at checkout?"
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
    """
    Return suggestion based on message content.
    """

    if not message:
        return DEFAULT_RESPONSE

    message = message.strip()

    for rule in RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, message, re.IGNORECASE):
                return rule["response"]

    return DEFAULT_RESPONSE