from constants.syntatical import *


class Symbol:
    def __init__(self, name, symbol_type):
        self.name = name
        self.symbol_type = symbol_type
        self.next = None

class ScopeVerifier:
    def __init__(self, syntatical_variable_list):
        self.syntatical_variable_list = syntatical_variable_list
        self.label_index = 0
        self.scope_stack = []
        self.current_level = -1  
        
    def define(self, name, symbol_type):
        symbol = Symbol(name, symbol_type)
        if len(self.scope_stack) <= self.current_level:
            self.scope_stack.append(None)
        
        current_scope = self.scope_stack[self.current_level]
        aux = current_scope
        while aux is not None:
            if aux.name == name:
                raise ValueError(f"Redeclaração de '{name}'.")
            aux = aux.next
        
        if self.scope_stack[self.current_level] is None:
            self.scope_stack[self.current_level] = symbol
        else:
            aux = self.scope_stack[self.current_level]
            while aux.next is not None:
                aux = aux.next
            aux.next = symbol

    def search(self, name):
        if self.current_level >= 0:
            obj = self.scope_stack[self.current_level]
            while obj is not None:
                if obj.name == name:
                    return obj
                obj = obj.next
        return None

    def find(self, name):
        for level in range(self.current_level, -1, -1):
            obj = self.scope_stack[level]
            while obj is not None:
                if obj.name == name:
                    return obj
                obj = obj.next
        return None

    def build_stack(self):
        for [secondary_token, current_level, type, details] in self.syntatical_variable_list:
            if current_level > self.current_level:
                self.current_level = current_level
                self.scope_stack.append(None)  
            elif current_level < self.current_level:
                while self.current_level > current_level:
                    self.scope_stack.pop()  
                    self.current_level -= 1

            if type == 'VARIABLE_DECLARATION':
                self.define(secondary_token, 'variable')
            elif type == 'VARIABLE_USAGE':
                var = self.find(secondary_token)
                if var is None:
                    raise ValueError(f"Não é encontrado no escopo o '{secondary_token}'.")
            elif type == 'FUNCTION_DECLARATION':
                self.define(secondary_token, 'function')
            elif type == 'FUNCTION_USAGE':
                func = self.find(secondary_token)
                if func is None:
                    raise ValueError(f"Não é possível encontrar '{secondary_token}'.")
            elif type == 'TYPE_DECLARATION':
                self.define(secondary_token, 'type')
            elif type == 'TYPE_USAGE':
                type_obj = self.find(secondary_token)
                if type_obj is None:
                    raise ValueError(f"Tipo '{secondary_token}' não encontrado no escopo.")
