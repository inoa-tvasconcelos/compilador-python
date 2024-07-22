from constants.informer import INFO
from helper.informer import Informer


class Tester():
    id = 0

    def __init__(self, next_input, next_answer, test_end_input='', did_test_end=None, first_info='\n', reset = False):
        if reset:
            Tester.id = 0
        self.id = Tester.id
        Tester.id += 1
        self.next_answer = next_answer
        self.next_input = next_input
        self.test_end_input = test_end_input
        self.did_test_end = did_test_end
        self.first_info = first_info

    def run_test(self):
        correct_answer = 0
        total_tests = 0
        first_info = self.first_info

        test_input = self.next_input()
        if (self.test_end(test_input)):
            return {
                'correct': 0,
                'total': 0,
                'passed': True
            }
        expected_output = self.next_answer(total_tests)
        if test_input == expected_output:
            correct_answer += 1
        else:
            Informer(f"Expected {expected_output} but got {test_input}", INFO, specification=first_info)
            first_info = ""
        total_tests += 1
        while True:
            test_input = self.next_input()
            if self.test_end(test_input):
                break
            expected_output = self.next_answer(total_tests)
            if test_input == expected_output:
                correct_answer += 1
            else:
                Informer(f"Expected {expected_output} but got {test_input}", INFO, specification=first_info)
                first_info = ""
            total_tests += 1
        return {
            'correct': correct_answer,
            'total': total_tests,
            'passed': correct_answer == total_tests
        }
    
    def test_end(self, input):
        if self.did_test_end is not None:
            return self.did_test_end(input)
        return input == self.test_end_input
    
    def printed_test(self, name, end=" "):
        prefix = ""
        if (self.id > 0):
            prefix += f"({self.id})"
            space = " "*(8 - len(prefix))
            prefix = space+prefix
        prefix_text = f"{prefix} Testing {name} ..."
        print(prefix_text, end=end)
        results = self.run_test()
        parsed_text = f"Finished {name}: PASSED" if results['passed'] else f"FAILED {name} test"
        if (self.id > 0):
            space = " "*(45 - len(parsed_text))
            parsed_text = space + parsed_text
        parsed_results = f"({results['correct']}/{results['total']})"
        result_space = -len(parsed_text)
        if (self.id > 0):
            result_space -= len(prefix_text) - 95
        parsed_results = " "*result_space + parsed_results
        print(parsed_text, parsed_results)
        return results['passed']

class StackTester(Tester):
    def __init__(self, question_answer, get_input_from_question, first_info='\n', reset = False):
        self.question_list = list(question_answer.keys())
        self.answer_list = list(question_answer.values())
        get_next_input = lambda: get_input_from_question(self.question_list.pop(0)) if len(self.question_list) > 0 else None
        get_next_answer = lambda total_tests: self.answer_list.pop(0) if len(self.answer_list) > 0 else None
        super().__init__(get_next_input, get_next_answer, test_end_input = None, first_info=first_info, reset=reset)