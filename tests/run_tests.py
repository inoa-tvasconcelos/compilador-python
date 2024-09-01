from helper.analyser import run_tests as run_analyser_tests
from logic.lexical.tests import test_token_extractor as run_token_extractor_tests

def protected_test(name, test_fn):
    print(f"Running {name} tests...")
    try:
        if (test_fn()):
            print(name, "finished successfully!")
        else:
            print(name, "failed without raising an exception!")
    except Exception as e:
        print(name, "failed catastrophically!")
        print("Exception:", e)

def run_test_template(name, test_infos):
    print(f"Running {name} tests...")
    for test_name, test_fn in test_infos:
        protected_test(test_name, test_fn)
    print(f"Finished running {name} tests!")

def run_helper_tests():
    run_test_template("helper", [
        ("analyser", run_analyser_tests)
    ])

def run_lexical_tests():
    run_test_template("lexical", [
        ("token_extractor", run_token_extractor_tests)
    ])

def run_syntactic_tests():
    run_test_template("syntactic", [])

def run_semantic_tests():
    run_test_template("semantic", [])

def run_all_tests():
    run_helper_tests()
    run_lexical_tests()
    run_syntactic_tests()
    run_semantic_tests()

if __name__ == "__main__":
    run_all_tests()