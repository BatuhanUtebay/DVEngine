"""Advanced condition evaluation system for DVGE scripting."""

import re
import json
import operator
from typing import Any, Dict, List, Union, Callable, Optional
from datetime import datetime
import math


class ConditionEvaluator:
    """Advanced condition evaluation with support for complex expressions."""
    
    def __init__(self, variable_system=None):
        self.variable_system = variable_system
        
        # Operators mapping
        self.operators = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "%": operator.mod,
            "**": operator.pow,
            "and": operator.and_,
            "or": operator.or_,
            "not": operator.not_,
        }
        
        # String operators
        self.string_operators = {
            "contains": lambda a, b: str(b).lower() in str(a).lower(),
            "starts_with": lambda a, b: str(a).lower().startswith(str(b).lower()),
            "ends_with": lambda a, b: str(a).lower().endswith(str(b).lower()),
            "matches": lambda a, b: bool(re.match(str(b), str(a))),
            "length": lambda a: len(str(a)),
            "empty": lambda a: len(str(a).strip()) == 0,
            "not_empty": lambda a: len(str(a).strip()) > 0
        }
        
        # List/array operators
        self.list_operators = {
            "in": lambda a, b: a in b if isinstance(b, (list, tuple, set, str)) else False,
            "not_in": lambda a, b: a not in b if isinstance(b, (list, tuple, set, str)) else True,
            "has": lambda a, b: b in a if isinstance(a, (list, tuple, set, str)) else False,
            "count": lambda a: len(a) if hasattr(a, '__len__') else 0,
            "any": lambda a: any(a) if hasattr(a, '__iter__') else bool(a),
            "all": lambda a: all(a) if hasattr(a, '__iter__') else bool(a)
        }
        
        # Mathematical functions
        self.math_functions = {
            "abs": abs,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
            "min": min,
            "max": max,
            "sum": sum,
            "avg": lambda x: sum(x) / len(x) if x else 0,
            "sqrt": math.sqrt,
            "pow": pow,
            "random": lambda: __import__('random').random()
        }
        
        # Date/time functions
        self.date_functions = {
            "now": lambda: datetime.now(),
            "today": lambda: datetime.now().date(),
            "age": self._calculate_age,
            "days_since": self._days_since,
            "format_date": self._format_date
        }
        
        # All available functions
        self.functions = {
            **self.string_operators,
            **self.list_operators,
            **self.math_functions,
            **self.date_functions
        }
    
    def evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any] = None) -> bool:
        """Evaluate a single condition."""
        if context is None:
            context = {}
        
        # Get variable value
        variable_name = condition.get("variable", "")
        variable_value = self._get_variable_value(variable_name, context)
        
        # Get comparison value
        compare_value = condition.get("value", "")
        if isinstance(compare_value, str) and compare_value.startswith("$"):
            # Reference to another variable
            compare_value = self._get_variable_value(compare_value[1:], context)
        
        # Get operator
        operator_name = condition.get("operator", "==")
        
        # Convert values based on data type
        data_type = condition.get("data_type", "string")
        variable_value = self._convert_value(variable_value, data_type)
        compare_value = self._convert_value(compare_value, data_type)
        
        # Evaluate condition
        result = self._apply_operator(variable_value, operator_name, compare_value)
        
        # Apply negation if specified
        if condition.get("negated", False):
            result = not result
        
        return bool(result)
    
    def evaluate_conditions_list(self, conditions: List[Dict[str, Any]], 
                                logic: str = "AND", context: Dict[str, Any] = None) -> bool:
        """Evaluate a list of conditions with specified logic."""
        if not conditions:
            return True
        
        results = []
        for condition in conditions:
            result = self.evaluate_condition(condition, context)
            results.append(result)
        
        if logic.upper() == "AND":
            return all(results)
        elif logic.upper() == "OR":
            return any(results)
        else:
            # Custom logic - not implemented in this basic version
            return all(results)
    
    def evaluate_expression(self, expression: str, context: Dict[str, Any] = None) -> Any:
        """Evaluate a complex expression string."""
        if context is None:
            context = {}
        
        # This is a simplified expression evaluator
        # In a full implementation, you'd use a proper parser
        
        try:
            # Replace variables with their values
            processed_expression = self._replace_variables(expression, context)
            
            # Replace function calls
            processed_expression = self._replace_functions(processed_expression, context)
            
            # Safe evaluation (limited scope)
            safe_dict = {
                "__builtins__": {},
                "True": True,
                "False": False,
                "None": None,
                **self.functions
            }
            
            result = eval(processed_expression, safe_dict)
            return result
            
        except Exception as e:
            print(f"Error evaluating expression '{expression}': {e}")
            return False
    
    def _get_variable_value(self, variable_name: str, context: Dict[str, Any]) -> Any:
        """Get variable value from context or variable system."""
        # First check context
        if variable_name in context:
            return context[variable_name]
        
        # Then check variable system
        if self.variable_system:
            if hasattr(self.variable_system, 'get_variable'):
                return self.variable_system.get_variable(variable_name)
            elif hasattr(self.variable_system, 'variables') and variable_name in self.variable_system.variables:
                return self.variable_system.variables[variable_name]
            elif hasattr(self.variable_system, 'flags') and variable_name in self.variable_system.flags:
                return self.variable_system.flags[variable_name]
        
        # Default value
        return ""
    
    def _convert_value(self, value: Any, data_type: str) -> Any:
        """Convert value to specified data type."""
        try:
            if data_type == "number":
                return float(value) if '.' in str(value) else int(value)
            elif data_type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ("true", "yes", "1", "on")
                return bool(value)
            elif data_type == "string":
                return str(value)
            elif data_type == "list":
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except:
                        return value.split(",")
                return list(value) if hasattr(value, '__iter__') else [value]
            elif data_type == "object":
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except:
                        return {"value": value}
                return value
            else:
                return value
        except (ValueError, TypeError):
            return value
    
    def _apply_operator(self, left: Any, operator_name: str, right: Any) -> Any:
        """Apply operator to two values."""
        # Standard operators
        if operator_name in self.operators:
            return self.operators[operator_name](left, right)
        
        # String operators
        if operator_name in self.string_operators:
            return self.string_operators[operator_name](left, right)
        
        # List operators
        if operator_name in self.list_operators:
            return self.list_operators[operator_name](left, right)
        
        # Default to equality
        return left == right
    
    def _replace_variables(self, expression: str, context: Dict[str, Any]) -> str:
        """Replace variable references in expression."""
        # Find all variable references like ${variable_name}
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_name = match.group(1)
            value = self._get_variable_value(var_name, context)
            
            # Return properly quoted value
            if isinstance(value, str):
                return f'"{value}"'
            elif value is None:
                return "None"
            else:
                return str(value)
        
        return re.sub(pattern, replace_var, expression)
    
    def _replace_functions(self, expression: str, context: Dict[str, Any]) -> str:
        """Replace function calls in expression."""
        # This is a simplified implementation
        # A full implementation would need a proper parser
        
        # Handle common function patterns
        for func_name in self.functions:
            pattern = rf'{func_name}\(([^)]*)\)'
            if re.search(pattern, expression):
                # This would need more sophisticated parsing
                # For now, we'll leave function calls as-is
                pass
        
        return expression
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _days_since(self, date_str: str) -> int:
        """Calculate days since a given date."""
        try:
            past_date = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.now()
            return (today - past_date).days
        except:
            return 0
    
    def _format_date(self, date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
        """Format a date object."""
        try:
            if isinstance(date_obj, str):
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
            return date_obj.strftime(format_str)
        except:
            return str(date_obj)
    
    def validate_expression(self, expression: str) -> Dict[str, Any]:
        """Validate an expression and return validation results."""
        errors = []
        warnings = []
        
        try:
            # Check for balanced parentheses
            if expression.count('(') != expression.count(')'):
                errors.append("Unbalanced parentheses")
            
            # Check for valid variable references
            var_pattern = r'\$\{([^}]+)\}'
            var_matches = re.findall(var_pattern, expression)
            for var_name in var_matches:
                if not var_name.isidentifier():
                    warnings.append(f"Variable name '{var_name}' may not be valid")
            
            # Check for dangerous operations
            dangerous_patterns = [
                r'__\w+__',  # Dunder methods
                r'import\s+',  # Import statements
                r'exec\s*\(',  # Exec calls
                r'eval\s*\(',  # Eval calls
                r'open\s*\(',  # File operations
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, expression):
                    errors.append(f"Potentially unsafe operation detected: {pattern}")
            
            # Try to parse the expression
            try:
                # Create a test context
                test_context = {"test_var": "test_value", "test_num": 42}
                processed = self._replace_variables(expression, test_context)
                
                # Try to compile (but not execute)
                compile(processed, '<string>', 'eval')
                
            except SyntaxError as e:
                errors.append(f"Syntax error: {e}")
            except Exception as e:
                warnings.append(f"Potential runtime error: {e}")
        
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_available_functions(self) -> Dict[str, str]:
        """Get list of available functions with descriptions."""
        return {
            # String functions
            "contains(text, substring)": "Check if text contains substring",
            "starts_with(text, prefix)": "Check if text starts with prefix",
            "ends_with(text, suffix)": "Check if text ends with suffix",
            "matches(text, pattern)": "Check if text matches regex pattern",
            "length(text)": "Get length of text",
            "empty(text)": "Check if text is empty",
            
            # List functions
            "in(item, list)": "Check if item is in list",
            "has(list, item)": "Check if list contains item",
            "count(list)": "Get count of items in list",
            "any(list)": "Check if any item in list is true",
            "all(list)": "Check if all items in list are true",
            
            # Math functions
            "abs(number)": "Get absolute value",
            "round(number)": "Round to nearest integer",
            "min(numbers)": "Get minimum value",
            "max(numbers)": "Get maximum value",
            "sum(numbers)": "Sum all numbers",
            "avg(numbers)": "Calculate average",
            "random()": "Get random number 0-1",
            
            # Date functions
            "now()": "Get current date and time",
            "today()": "Get current date",
            "age(birth_date)": "Calculate age from birth date",
            "days_since(date)": "Days since given date"
        }