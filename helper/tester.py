from constants.informer import INFO
from helper.informer import Informer


class Tester():
    def __init__(self, next_input, next_answer, test_end_input='', did_test_end=None, first_info='\n'):
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
        print("Testing", name, "...", end=end)
        results = self.run_test()
        print(f"Finished {name}: PASSED " if results['passed'] else f"FAILED {name} test", f"({results['correct']}/{results['total']})" )
        return results['passed']

class StackTester(Tester):
    def __init__(self, question_answer, get_input_from_question, first_info='\n'):
        self.question_list = list(question_answer.keys())
        self.answer_list = list(question_answer.values())
        get_next_input = lambda: get_input_from_question(self.question_list.pop(0)) if len(self.question_list) > 0 else None
        get_next_answer = lambda total_tests: self.answer_list.pop(0) if len(self.answer_list) > 0 else None
        super().__init__(get_next_input, get_next_answer, test_end_input = None, first_info=first_info)