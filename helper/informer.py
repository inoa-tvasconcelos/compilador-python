import os
from constants.informer import *

class Informer:
    def __init__(self, message, severity=ERROR, specification=""):
        self.severity = severity
        self.specification = specification
        self.message = self.parse_message(message)
        sensitivity = self.get_severity_sensitivity()
        if (severity < sensitivity):
            self.stdout()
            return
        self.raise_exception()
        
    def get_severity_sensitivity(self):
        sensitivity = os.environ.get('ERROR_SENSITIVITY')
        if (sensitivity == None):
            return DEFAULT_ERROR_SENSITIVITY
        return sensitivity
    
    def stdout(self):
        print(self.message)

    def raise_exception(self):
        raise Exception(self.message)

    def get_message_prefix(self):
        if (self.severity == INFO):
            return f"{self.specification} INFO"
        if (self.severity == WARNING):
            return f"{self.specification} WARNING"
        if (self.severity == ERROR):
            return f"{self.specification} ERROR"
        return f"{self.specification} SEVERITY LEVEL {self.severity}"
    
    def parse_message(self, message):
        return f'{self.get_message_prefix()}: {message}'

# Localized tests
if __name__ == "__main__":
    Informer("This is a test message", INFO)
    Informer("This is a test message", WARNING)
    Informer("This is a test message", WARNING, "Lexical")
    try:
        Informer("This is a test message", ERROR)
    except Exception as e:
        print("There was an exception:", e)
    try:
        Informer("This is a test message", ERROR, "Lexical")
    except Exception as e:
        print("There was an exception:", e)