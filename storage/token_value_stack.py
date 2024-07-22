from collections import deque

class TokenValueStack(deque):
    def __init__(self):
        super().__init__()

    def store(self, token_value):
        self.append(token_value)
        return len(self) - 1 