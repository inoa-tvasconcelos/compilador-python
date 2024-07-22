from abc import *
import os

from helper.informer import Informer
from helper.tester import Tester

class Analyser:
    @abstractmethod
    def get_next_char(self):
        """
        Returns the next character from the source 
        If there are no more characters, returns an empty string
        """
        pass
    @abstractmethod
    def revert_to_last_char(self):
        """
        Ignores last 'get_next_char' call (reverts the index)
        """
        pass
    @abstractmethod
    def get_current_index(self):
        """
        Returns the current index of the analyser
        """
        pass
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return self

class TextAnalyser(Analyser):
    def __init__(self, text):
        self.text = text
        self.index = 0

    def get_next_char(self):
        if self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            return char
        return ''
    
    def revert_to_last_char(self):
        self.index -= 1
    
    def get_current_index(self):
        return self.index

class FileAnalyser(Analyser):
    def __init__(self, file_location):
        self.file = None
        self.file_location = file_location
    def __enter__(self):
        self.file = open(self.file_location, 'r')
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.file is not None:
            self.file.close()
    def get_next_char(self):
        self.check_file_open()
        return self.file.read(1)
    def revert_to_last_char(self):
        self.check_file_open()
        self.file.seek(-1, 1)
    def get_current_index(self):
        self.check_file_open()
        return self.file.tell()
    def check_file_open(self):
        if (not self.file):
            Informer("File not opened. Did you use this class within a 'with' statement?")
    
def run_tests():
    dirname = os.path.dirname(__file__)
    test_file = os.path.join(dirname, '../tests/mocks/analyser.mock')
    passed = True
    with open(test_file) as file:
        answer = file.read()
        get_answer = lambda i: answer[i]
    with FileAnalyser(test_file) as analyser:
        text_tester = Tester(lambda: analyser.get_next_char(), get_answer)
        if (not text_tester.printed_test("File Analyser")):
            passed = False
    with TextAnalyser(answer) as analyser:
        test_tester = Tester(lambda: analyser.get_next_char(), get_answer)
        if (not test_tester.printed_test("Text Analyser")):
            passed = False
    return passed

# Localized tests
if __name__ == "__main__":
    run_tests()