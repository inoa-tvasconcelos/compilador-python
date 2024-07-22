class Tester():
    def __init__(self, next_input, next_answer, test_end_input='', did_test_end=None):
        self.next_answer = next_answer
        self.next_input = next_input
        self.test_end_input = test_end_input
        self.did_test_end = did_test_end

    def run_test(self):
        correct_answer = 0
        total_tests = 0

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
        total_tests += 1
        while True:
            test_input = self.next_input()
            if self.test_end(test_input):
                break
            expected_output = self.next_answer(total_tests)
            if test_input == expected_output:
                correct_answer += 1
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
    
    def printed_test(self, name):
        print("Testing", name, "...", end=" ")
        results = self.run_test()
        print("PASSED" if results['passed'] else "FAILED", f"({results['correct']}/{results['total']})" )
        return results['passed']