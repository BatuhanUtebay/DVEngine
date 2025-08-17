"""Script node types for advanced scripting in DVGE."""

from typing import Dict, List, Any, Optional, Union
from .base_node import BaseNode


class ScriptNode(BaseNode):
    """Node that executes custom scripts."""
    
    def __init__(self, x=0, y=0, node_id="", **kwargs):
        super().__init__(x, y, node_id, **kwargs)
        
        # Script content and settings
        self.script_code: str = "// Enter your JavaScript code here\nreturn true;"
        self.script_language: str = "javascript"  # "javascript" or "python"
        self.script_description: str = "Custom script"
        
        # Execution settings
        self.timeout_ms: int = 5000  # 5 second timeout
        self.async_execution: bool = False
        self.cache_results: bool = False
        
        # Input/Output
        self.input_variables: List[str] = []  # Variables to pass to script
        self.output_variables: List[str] = []  # Variables to extract from script
        self.return_variable: str = "result"  # Variable name for return value
        
        # Flow control
        self.success_node: str = ""  # Node to go to on successful execution
        self.failure_node: str = ""  # Node to go to on script error
        self.next_node: str = ""     # Default next node
        
        # Error handling
        self.continue_on_error: bool = True
        self.error_message: str = "Script execution failed"
        
        # Debugging
        self.debug_mode: bool = False
        self.breakpoints: List[int] = []  # Line numbers for breakpoints
        
        self.color = "#4A90E2"  # Blue color for script nodes
    
    def get_height(self) -> int:
        """Calculate the height of the script node."""
        base_height = super().get_height()
        
        # Add height for script preview
        script_lines = len(self.script_code.split('\n'))
        preview_lines = min(script_lines, 5)  # Show max 5 lines in preview
        script_height = preview_lines * 20
        
        # Add height for input/output variables
        io_height = (len(self.input_variables) + len(self.output_variables)) * 15
        
        return base_height + script_height + io_height + 40
    
    def execute_script(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the script with given context. To be implemented by script engine."""
        # This will be implemented by the script execution engine
        return {"success": True, "result": None, "error": None}
    
    def get_script_preview(self, max_lines: int = 3) -> str:
        """Get a preview of the script code."""
        lines = self.script_code.split('\n')
        preview_lines = lines[:max_lines]
        
        if len(lines) > max_lines:
            preview_lines.append("...")
        
        return '\n'.join(preview_lines)
    
    def validate_script(self) -> Dict[str, Any]:
        """Validate the script syntax. To be implemented by script engine."""
        return {"valid": True, "errors": [], "warnings": []}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "script_code": self.script_code,
            "script_language": self.script_language,
            "script_description": self.script_description,
            "timeout_ms": self.timeout_ms,
            "async_execution": self.async_execution,
            "cache_results": self.cache_results,
            "input_variables": self.input_variables,
            "output_variables": self.output_variables,
            "return_variable": self.return_variable,
            "success_node": self.success_node,
            "failure_node": self.failure_node,
            "next_node": self.next_node,
            "continue_on_error": self.continue_on_error,
            "error_message": self.error_message,
            "debug_mode": self.debug_mode,
            "breakpoints": self.breakpoints
        })
        return data
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update node from dictionary data."""
        super().update_from_dict(data)
        self.script_code = data.get("script_code", self.script_code)
        self.script_language = data.get("script_language", self.script_language)
        self.script_description = data.get("script_description", self.script_description)
        self.timeout_ms = data.get("timeout_ms", self.timeout_ms)
        self.async_execution = data.get("async_execution", self.async_execution)
        self.cache_results = data.get("cache_results", self.cache_results)
        self.input_variables = data.get("input_variables", self.input_variables)
        self.output_variables = data.get("output_variables", self.output_variables)
        self.return_variable = data.get("return_variable", self.return_variable)
        self.success_node = data.get("success_node", self.success_node)
        self.failure_node = data.get("failure_node", self.failure_node)
        self.next_node = data.get("next_node", self.next_node)
        self.continue_on_error = data.get("continue_on_error", self.continue_on_error)
        self.error_message = data.get("error_message", self.error_message)
        self.debug_mode = data.get("debug_mode", self.debug_mode)
        self.breakpoints = data.get("breakpoints", self.breakpoints)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScriptNode':
        """Create from dictionary."""
        node = cls()
        node.update_from_dict(data)
        return node


class ConditionalNode(BaseNode):
    """Node with advanced conditional logic."""
    
    def __init__(self, x=0, y=0, node_id="", **kwargs):
        super().__init__(x, y, node_id, **kwargs)
        
        # Conditional expressions
        self.conditions: List[Dict[str, Any]] = []
        self.condition_logic: str = "AND"  # "AND", "OR", "CUSTOM"
        self.custom_logic_expression: str = ""  # For complex logic like "(A AND B) OR (C AND NOT D)"
        
        # Outcomes
        self.true_node: str = ""
        self.false_node: str = ""
        self.branches: List[Dict[str, Any]] = []  # Multiple conditional branches
        
        # Advanced features
        self.use_script_condition: bool = False
        self.script_condition: str = "// Return true or false\nreturn true;"
        self.evaluate_mode: str = "immediate"  # "immediate", "lazy", "cached"
        
        self.color = "#9B59B6"  # Purple color for conditional nodes
    
    def add_condition(self, variable: str, operator: str, value: Any, 
                     data_type: str = "string") -> None:
        """Add a condition to the list."""
        condition = {
            "variable": variable,
            "operator": operator,  # ==, !=, <, >, <=, >=, contains, starts_with, etc.
            "value": value,
            "data_type": data_type,  # string, number, boolean, list, object
            "negated": False
        }
        self.conditions.append(condition)
    
    def add_branch(self, condition_expression: str, target_node: str, 
                   description: str = "") -> None:
        """Add a conditional branch."""
        branch = {
            "condition": condition_expression,
            "target_node": target_node,
            "description": description
        }
        self.branches.append(branch)
    
    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate all conditions. To be implemented by condition evaluator."""
        # This will be implemented by the condition evaluation engine
        return True
    
    def get_height(self) -> int:
        """Calculate the height of the conditional node."""
        base_height = super().get_height()
        
        # Add height for conditions
        conditions_height = len(self.conditions) * 25
        
        # Add height for branches
        branches_height = len(self.branches) * 20
        
        return base_height + conditions_height + branches_height + 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "conditions": self.conditions,
            "condition_logic": self.condition_logic,
            "custom_logic_expression": self.custom_logic_expression,
            "true_node": self.true_node,
            "false_node": self.false_node,
            "branches": self.branches,
            "use_script_condition": self.use_script_condition,
            "script_condition": self.script_condition,
            "evaluate_mode": self.evaluate_mode
        })
        return data
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update node from dictionary data."""
        super().update_from_dict(data)
        self.conditions = data.get("conditions", self.conditions)
        self.condition_logic = data.get("condition_logic", self.condition_logic)
        self.custom_logic_expression = data.get("custom_logic_expression", self.custom_logic_expression)
        self.true_node = data.get("true_node", self.true_node)
        self.false_node = data.get("false_node", self.false_node)
        self.branches = data.get("branches", self.branches)
        self.use_script_condition = data.get("use_script_condition", self.use_script_condition)
        self.script_condition = data.get("script_condition", self.script_condition)
        self.evaluate_mode = data.get("evaluate_mode", self.evaluate_mode)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConditionalNode':
        """Create from dictionary."""
        node = cls()
        node.update_from_dict(data)
        return node


class FunctionNode(BaseNode):
    """Node that defines reusable functions."""
    
    def __init__(self, x=0, y=0, node_id="", **kwargs):
        super().__init__(x, y, node_id, **kwargs)
        
        # Function definition
        self.function_name: str = "myFunction"
        self.function_code: str = "// Define your function here\nfunction myFunction(param1, param2) {\n    return param1 + param2;\n}"
        self.function_description: str = "Custom function"
        
        # Parameters
        self.parameters: List[Dict[str, Any]] = []
        self.return_type: str = "any"  # any, string, number, boolean, object, array
        
        # Function settings
        self.global_function: bool = True  # Available throughout the story
        self.pure_function: bool = True    # No side effects
        self.memoize: bool = False        # Cache results for same inputs
        
        # Documentation
        self.examples: List[str] = []
        self.tags: List[str] = []
        
        self.color = "#E67E22"  # Orange color for function nodes
    
    def add_parameter(self, name: str, param_type: str = "any", 
                     default_value: Any = None, required: bool = True,
                     description: str = "") -> None:
        """Add a parameter to the function."""
        parameter = {
            "name": name,
            "type": param_type,
            "default_value": default_value,
            "required": required,
            "description": description
        }
        self.parameters.append(parameter)
    
    def get_function_signature(self) -> str:
        """Get the function signature string."""
        param_strings = []
        for param in self.parameters:
            param_str = param["name"]
            if not param["required"] and param["default_value"] is not None:
                param_str += f" = {param['default_value']}"
            param_strings.append(param_str)
        
        return f"{self.function_name}({', '.join(param_strings)})"
    
    def get_height(self) -> int:
        """Calculate the height of the function node."""
        base_height = super().get_height()
        
        # Add height for function code preview
        code_lines = len(self.function_code.split('\n'))
        preview_lines = min(code_lines, 4)
        code_height = preview_lines * 20
        
        # Add height for parameters
        params_height = len(self.parameters) * 20
        
        return base_height + code_height + params_height + 40
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "function_name": self.function_name,
            "function_code": self.function_code,
            "function_description": self.function_description,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "global_function": self.global_function,
            "pure_function": self.pure_function,
            "memoize": self.memoize,
            "examples": self.examples,
            "tags": self.tags
        })
        return data
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update node from dictionary data."""
        super().update_from_dict(data)
        self.function_name = data.get("function_name", self.function_name)
        self.function_code = data.get("function_code", self.function_code)
        self.function_description = data.get("function_description", self.function_description)
        self.parameters = data.get("parameters", self.parameters)
        self.return_type = data.get("return_type", self.return_type)
        self.global_function = data.get("global_function", self.global_function)
        self.pure_function = data.get("pure_function", self.pure_function)
        self.memoize = data.get("memoize", self.memoize)
        self.examples = data.get("examples", self.examples)
        self.tags = data.get("tags", self.tags)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionNode':
        """Create from dictionary."""
        node = cls()
        node.update_from_dict(data)
        return node


class APINode(BaseNode):
    """Node for external API integration."""
    
    def __init__(self, x=0, y=0, node_id="", **kwargs):
        super().__init__(x, y, node_id, **kwargs)
        
        # API configuration
        self.api_url: str = ""
        self.http_method: str = "GET"  # GET, POST, PUT, DELETE, PATCH
        self.headers: Dict[str, str] = {}
        self.query_params: Dict[str, str] = {}
        self.request_body: str = ""
        self.content_type: str = "application/json"
        
        # Authentication
        self.auth_type: str = "none"  # none, bearer, basic, api_key
        self.auth_config: Dict[str, str] = {}
        
        # Response handling
        self.response_variable: str = "api_response"
        self.success_status_codes: List[int] = [200, 201, 202]
        self.parse_json: bool = True
        self.extract_fields: Dict[str, str] = {}  # field_name -> variable_name
        
        # Error handling
        self.retry_attempts: int = 3
        self.retry_delay_ms: int = 1000
        self.timeout_ms: int = 10000
        self.success_node: str = ""
        self.failure_node: str = ""
        
        self.color = "#27AE60"  # Green color for API nodes
    
    def get_height(self) -> int:
        """Calculate the height of the API node."""
        base_height = super().get_height()
        
        # Add height for API details
        details_height = 80  # URL, method, etc.
        
        # Add height for headers and params
        config_height = (len(self.headers) + len(self.query_params)) * 15
        
        return base_height + details_height + config_height + 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "api_url": self.api_url,
            "http_method": self.http_method,
            "headers": self.headers,
            "query_params": self.query_params,
            "request_body": self.request_body,
            "content_type": self.content_type,
            "auth_type": self.auth_type,
            "auth_config": self.auth_config,
            "response_variable": self.response_variable,
            "success_status_codes": self.success_status_codes,
            "parse_json": self.parse_json,
            "extract_fields": self.extract_fields,
            "retry_attempts": self.retry_attempts,
            "retry_delay_ms": self.retry_delay_ms,
            "timeout_ms": self.timeout_ms,
            "success_node": self.success_node,
            "failure_node": self.failure_node
        })
        return data
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update node from dictionary data."""
        super().update_from_dict(data)
        self.api_url = data.get("api_url", self.api_url)
        self.http_method = data.get("http_method", self.http_method)
        self.headers = data.get("headers", self.headers)
        self.query_params = data.get("query_params", self.query_params)
        self.request_body = data.get("request_body", self.request_body)
        self.content_type = data.get("content_type", self.content_type)
        self.auth_type = data.get("auth_type", self.auth_type)
        self.auth_config = data.get("auth_config", self.auth_config)
        self.response_variable = data.get("response_variable", self.response_variable)
        self.success_status_codes = data.get("success_status_codes", self.success_status_codes)
        self.parse_json = data.get("parse_json", self.parse_json)
        self.extract_fields = data.get("extract_fields", self.extract_fields)
        self.retry_attempts = data.get("retry_attempts", self.retry_attempts)
        self.retry_delay_ms = data.get("retry_delay_ms", self.retry_delay_ms)
        self.timeout_ms = data.get("timeout_ms", self.timeout_ms)
        self.success_node = data.get("success_node", self.success_node)
        self.failure_node = data.get("failure_node", self.failure_node)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APINode':
        """Create from dictionary."""
        node = cls()
        node.update_from_dict(data)
        return node