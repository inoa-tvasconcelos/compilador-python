from constants.lexical import KeyWords


class TypeVerifier:
  def __init__(self, syntactical_analyser, scope_verifier):
      self.syntactical_analyser = syntactical_analyser
      self.scope_verifier = scope_verifier
      self.errors = []
  
  def verify(self):
      for assignment in self.syntactical_analyser.assignments:
          lhs_var = assignment['lhs']
          rhs_expr = assignment['rhs']
          lhs_type = self.get_type(lhs_var)
          rhs_type = self.evaluate_expression(rhs_expr)
          if lhs_type != rhs_type:
              self.errors.append(f"Type error in assignment: cannot assign '{rhs_type}' to '{lhs_type}'")
  
  def get_type(self, var_name):
      var_symbol = self.scope_verifier.find(var_name)
      if var_symbol:
          return var_symbol.var_type
      else:
          self.errors.append(f"Undefined variable '{var_name}'")
          return None
  
  def evaluate_expression(self, expr):
      if expr[0] == 'BIN_OP':
          operator = expr[1]
          left_expr = expr[2]
          right_expr = expr[3]
          left_type = self.evaluate_expression(left_expr)
          right_type = self.evaluate_expression(right_expr)
          result_type = self.apply_operator(operator, left_type, right_type)
          return result_type
      elif expr[0] == 'UNARY_OP':
          operator = expr[1]
          operand_expr = expr[2]
          operand_type = self.evaluate_expression(operand_expr)
          result_type = self.apply_unary_operator(operator, operand_type)
          return result_type
      elif expr[0] == 'VAR':
          var_name = expr[1]
          var_symbol = self.scope_verifier.find(var_name)
          if var_symbol:
              return var_symbol.var_type
          else:
              self.errors.append(f"Undefined variable '{var_name}'")
              return None
      elif expr[0] == 'FIELD_ACCESS':
          base_expr = expr[1]
          field_name = expr[2]
          base_type = self.evaluate_expression(base_expr)
          if base_type in self.struct_definitions:
              struct_fields = self.struct_definitions[base_type]
              if field_name in struct_fields:
                  return struct_fields[field_name]
              else:
                  self.errors.append(f"Struct '{base_type}' has no field '{field_name}'")
                  return None
          else:
              self.errors.append(f"Type '{base_type}' is not a struct")
              return None
      elif expr[0] == 'LIT':
          token_type = expr[1]
          if token_type == KeyWords.INTEGER:
              return 'integer'
          elif token_type == KeyWords.FLOAT:
              return 'float'
          elif token_type == KeyWords.STRING:
              return 'string'
          elif token_type in [KeyWords.TRUE, KeyWords.FALSE]:
              return 'boolean'
          else:
              return None
      else:
          self.errors.append(f"Unknown expression type '{expr[0]}'")
          return None

  def apply_operator(self, operator, left_type, right_type):
      operator_str = KeyWords().keyword_to_string(operator)
      if operator in [KeyWords.PLUS, KeyWords.MINUS, KeyWords.MULTIPLY, KeyWords.DIVIDE, KeyWords.EXPONENT]:
          if left_type == right_type and left_type in ['integer', 'float']:
              if operator == KeyWords.DIVIDE:
                  return 'float'
              else:
                  return left_type
          else:
              self.errors.append(f"Type error: cannot apply operator '{operator_str}' to types '{left_type}' and '{right_type}'")
              return None
      elif operator in [KeyWords.GREATER_THAN, KeyWords.LESS_THAN, KeyWords.EQUALITY, KeyWords.NOT_EQUAL, KeyWords.GREATER_THAN_EQUAL, KeyWords.LESS_THAN_EQUAL]:
          if left_type == right_type and left_type in ['integer', 'float']:
              return 'boolean'
          else:
              self.errors.append(f"Type error: cannot compare types '{left_type}' and '{right_type}' with operator '{operator_str}'")
              return None
      elif operator in [KeyWords.AND, KeyWords.OR]:
          if left_type == right_type and left_type == 'boolean':
              return 'boolean'
          else:
              self.errors.append(f"Type error: logical operator '{operator_str}' requires boolean operands")
              return None
      else:
          self.errors.append(f"Unsupported operator '{operator_str}'")
          return None

  def apply_unary_operator(self, operator, operand_type):
      operator_str = KeyWords().keyword_to_string(operator)
      if operator == KeyWords.MINUS:
          if operand_type in ['integer', 'float']:
              return operand_type
          else:
              self.errors.append(f"Type error: unary operator '{operator_str}' requires numeric operand")
              return None
      elif operator == KeyWords.NOT:
          if operand_type == 'boolean':
              return 'boolean'
          else:
              self.errors.append(f"Type error: unary operator '{operator_str}' requires boolean operand")
              return None
      else:
          self.errors.append(f"Unsupported unary operator '{operator_str}'")
          return None

  def get_variable_type(self, var_name):
      var_symbol = self.scope_verifier.find(var_name)
      if var_symbol:
          return var_symbol.var_type
      else:
          self.errors.append(f"Undefined variable '{var_name}'")
          return None
