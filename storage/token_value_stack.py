from collections import deque

class TokenValueStack(deque):
    def __init__(self):
        super().__init__()

    def store(self, token_value):
        self.append(token_value)
        return len(self) - 1 
    
    def get(self,index, default=None):
        try :
            return self[index]
        except:
            return default

if __name__ == "__main__":
    stack = TokenValueStack()
    try:
        assert stack.store("test") == 0
        assert stack.store("test1") == 1
        assert stack.store("test2") == 2
        assert stack[2] == "test2"
        assert stack[1] == "test1"
        assert stack[0] == "test"
        assert len(stack) == 3
        print("All tests passed")
    except Exception as e:
        print("There was an exception:", e)
        print("Tests did not pass")