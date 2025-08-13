# dvge/core/variable_system.py

"""Enhanced Variable System with mathematical operations and text substitution."""

import re
import random
from typing import Dict, Any, Union


class VariableSystem:
    """Handles advanced variable operations and text substitution."""
    
    def __init__(self):
        self.variables = {}
        self.flags = {}
    
    def set_variables_ref(self, variables_dict: Dict[str, Union[int, float]]):
        """Sets reference to the app's variables dictionary."""
        self.variables = variables_dict
    
    def set_flags_ref(self, flags_dict: Dict[str, bool]):
        """Sets reference to the app's flags dictionary."""
        self.flags = flags_dict
    
    def evaluate_math_expression(self, expression: str) -> Union[int, float]:
        """Safely evaluates mathematical expressions with variables."""
        try:
            # Replace variable names with their values
            expr = expression
            for var_name, value in self.variables.items():
                expr = expr.replace(f"{{{var_name}}}", str(value))
            
            # Add support for random() function
            expr = re.sub(r'random\((\d+),\s*(\d+)\)', 
                         lambda m: str(random.randint(int(m.group(1)), int(m.group(2)))), 
                         expr)
            
            # Safe evaluation (only allow basic math operations)
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expr):
                return eval(expr)
            else:
                return 0
        except:
            return 0
    
    def substitute_text(self, text: str) -> str:
        """Substitutes variables and expressions in text using {variable} syntax."""
        if not text:
            return text
        
        # Replace simple variables {variable_name}
        for var_name, value in self.variables.items():
            text = text.replace(f"{{{var_name}}}", str(value))
        
        # Replace flag references {flag_name}
        for flag_name, value in self.flags.items():
            text = text.replace(f"{{{flag_name}}}", "true" if value else "false")
        
        # Replace mathematical expressions {= expression}
        math_pattern = r'\{=([^}]+)\}'
        def replace_math(match):
            expression = match.group(1)
            result = self.evaluate_math_expression(expression)
            return str(int(result)) if isinstance(result, float) and result.is_integer() else str(result)
        
        text = re.sub(math_pattern, replace_math, text)
        
        # Replace conditional text {condition ? true_text : false_text}
        conditional_pattern = r'\{([^?}]+)\?([^:}]*):([^}]*)\}'
        def replace_conditional(match):
            condition = match.group(1).strip()
            true_text = match.group(2).strip()
            false_text = match.group(3).strip()
            
            # Evaluate condition
            condition_result = self._evaluate_condition(condition)
            return true_text if condition_result else false_text
        
        text = re.sub(conditional_pattern, replace_conditional, text)
        
        return text
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluates a condition string."""
        try:
            # Handle variable comparisons
            for var_name, value in self.variables.items():
                condition = condition.replace(f"{var_name}", str(value))
            
            # Handle flag references
            for flag_name, value in self.flags.items():
                condition = condition.replace(f"{flag_name}", str(value).lower())
            
            # Simple condition evaluation
            if '>=' in condition:
                left, right = condition.split('>=')
                return float(left.strip()) >= float(right.strip())
            elif '<=' in condition:
                left, right = condition.split('<=')
                return float(left.strip()) <= float(right.strip())
            elif '>' in condition:
                left, right = condition.split('>')
                return float(left.strip()) > float(right.strip())
            elif '<' in condition:
                left, right = condition.split('<')
                return float(left.strip()) < float(right.strip())
            elif '==' in condition:
                left, right = condition.split('==')
                return left.strip() == right.strip()
            elif '!=' in condition:
                left, right = condition.split('!=')
                return left.strip() != right.strip()
            
            # If it's just a flag name or true/false
            condition = condition.strip().lower()
            return condition in ['true', '1'] or condition in self.flags and self.flags[condition]
        except:
            return False
    
    def apply_variable_effect(self, var_name: str, operation: str, value: Union[str, int, float]):
        """Applies mathematical operations to variables."""
        if var_name not in self.variables:
            self.variables[var_name] = 0
        
        try:
            if isinstance(value, str):
                # If value contains variables or expressions, evaluate it
                if '{' in value or any(op in value for op in ['+', '-', '*', '/']):
                    value = self.evaluate_math_expression(value)
                else:
                    value = float(value) if '.' in value else int(value)
            
            current_value = self.variables[var_name]
            
            if operation == '=':
                self.variables[var_name] = value
            elif operation == '+=':
                self.variables[var_name] = current_value + value
            elif operation == '-=':
                self.variables[var_name] = current_value - value
            elif operation == '*=':
                self.variables[var_name] = current_value * value
            elif operation == '/=':
                if value != 0:
                    self.variables[var_name] = current_value / value
            elif operation == '%=':
                if value != 0:
                    self.variables[var_name] = current_value % value
            elif operation == 'min':
                self.variables[var_name] = min(current_value, value)
            elif operation == 'max':
                self.variables[var_name] = max(current_value, value)
            
            # Keep integers as integers when possible
            if isinstance(self.variables[var_name], float) and self.variables[var_name].is_integer():
                self.variables[var_name] = int(self.variables[var_name])
                
        except (ValueError, TypeError, ZeroDivisionError):
            pass  # Ignore errors and keep original value