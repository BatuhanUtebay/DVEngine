"""JavaScript execution engine for DVGE scripting system."""

import json
import time
import threading
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path


class ScriptExecutionResult:
    """Result of script execution."""
    
    def __init__(self):
        self.success: bool = False
        self.result: Any = None
        self.error: Optional[str] = None
        self.execution_time_ms: float = 0
        self.output: List[str] = []
        self.console_logs: List[str] = []
        self.variables_set: Dict[str, Any] = {}
        self.memory_used: int = 0
        self.timeout_occurred: bool = False


class ScriptEngine:
    """JavaScript execution engine with safety and security features."""
    
    def __init__(self, variable_system=None):
        self.variable_system = variable_system
        
        # Execution settings
        self.default_timeout_ms = 5000
        self.max_memory_mb = 50
        self.max_execution_time_ms = 30000
        
        # Security settings
        self.sandbox_enabled = True
        self.allowed_modules = []
        self.blocked_functions = [
            'eval', 'Function', 'setTimeout', 'setInterval',
            'require', 'import', 'process', 'Buffer'
        ]
        
        # Built-in DVGE API functions
        self.dvge_api = {
            'setVariable': self._api_set_variable,
            'getVariable': self._api_get_variable,
            'setFlag': self._api_set_flag,
            'getFlag': self._api_get_flag,
            'log': self._api_log,
            'random': self._api_random,
            'randomInt': self._api_random_int,
            'randomChoice': self._api_random_choice,
            'formatText': self._api_format_text,
            'wait': self._api_wait,
            'showMessage': self._api_show_message
        }
        
        # Check if Node.js is available
        self.nodejs_available = self._check_nodejs()
        
        # Fallback: Use Python's limited JS execution
        if not self.nodejs_available:
            print("Warning: Node.js not found. JavaScript execution will be limited.")
    
    def _check_nodejs(self) -> bool:
        """Check if Node.js is available on the system."""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def execute_script(self, script_code: str, context: Dict[str, Any] = None, 
                      timeout_ms: Optional[int] = None) -> ScriptExecutionResult:
        """Execute JavaScript code with safety measures."""
        if context is None:
            context = {}
        
        timeout_ms = timeout_ms or self.default_timeout_ms
        result = ScriptExecutionResult()
        
        start_time = time.time()
        
        try:
            if self.nodejs_available:
                result = self._execute_with_nodejs(script_code, context, timeout_ms)
            else:
                result = self._execute_with_fallback(script_code, context, timeout_ms)
        
        except Exception as e:
            result.success = False
            result.error = f"Execution error: {str(e)}"
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _execute_with_nodejs(self, script_code: str, context: Dict[str, Any], 
                           timeout_ms: int) -> ScriptExecutionResult:
        """Execute JavaScript using Node.js."""
        result = ScriptExecutionResult()
        
        # Create temporary files for script and context
        with tempfile.TemporaryDirectory() as temp_dir:
            script_file = Path(temp_dir) / "script.js"
            context_file = Path(temp_dir) / "context.json"
            output_file = Path(temp_dir) / "output.json"
            
            # Prepare context
            safe_context = self._prepare_context(context)
            
            # Write context to file
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(safe_context, f)
            
            # Create wrapper script
            wrapper_script = self._create_wrapper_script(script_code, context_file, output_file)
            
            # Write script to file
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(wrapper_script)
            
            try:
                # Execute script
                process = subprocess.run(
                    ['node', str(script_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout_ms / 1000,
                    cwd=temp_dir
                )
                
                # Read results
                if output_file.exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        output_data = json.load(f)
                    
                    result.success = output_data.get('success', False)
                    result.result = output_data.get('result')
                    result.error = output_data.get('error')
                    result.console_logs = output_data.get('console_logs', [])
                    result.variables_set = output_data.get('variables_set', {})
                else:
                    result.success = False
                    result.error = "No output file generated"
                
                # Handle stderr
                if process.stderr:
                    if not result.error:
                        result.error = process.stderr
                    result.console_logs.append(f"stderr: {process.stderr}")
            
            except subprocess.TimeoutExpired:
                result.success = False
                result.error = "Script execution timed out"
                result.timeout_occurred = True
            
            except Exception as e:
                result.success = False
                result.error = f"Node.js execution error: {str(e)}"
        
        return result
    
    def _execute_with_fallback(self, script_code: str, context: Dict[str, Any], 
                             timeout_ms: int) -> ScriptExecutionResult:
        """Fallback execution using Python (limited JavaScript support)."""
        result = ScriptExecutionResult()
        
        try:
            # This is a very basic JavaScript-to-Python converter
            # It handles simple cases only
            
            # Create execution context
            exec_context = {
                '__builtins__': {},
                'console': {'log': lambda *args: result.console_logs.append(' '.join(map(str, args)))},
                'Math': {
                    'random': lambda: __import__('random').random(),
                    'floor': lambda x: int(x),
                    'ceil': lambda x: int(x) + (1 if x > int(x) else 0),
                    'round': round,
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'pow': pow
                },
                'JSON': {
                    'stringify': json.dumps,
                    'parse': json.loads
                },
                **self.dvge_api,
                **context
            }
            
            # Simple JavaScript to Python conversion
            python_code = self._convert_js_to_python(script_code)
            
            # Execute with timeout
            if timeout_ms > 0:
                # Use threading for timeout (simplified)
                exec_result = [None, None]  # [result, error]
                
                def execute():
                    try:
                        local_context = {}
                        exec(python_code, exec_context, local_context)
                        exec_result[0] = local_context.get('result', True)
                    except Exception as e:
                        exec_result[1] = str(e)
                
                thread = threading.Thread(target=execute)
                thread.start()
                thread.join(timeout=timeout_ms / 1000)
                
                if thread.is_alive():
                    result.success = False
                    result.error = "Script execution timed out"
                    result.timeout_occurred = True
                else:
                    if exec_result[1]:
                        result.success = False
                        result.error = exec_result[1]
                    else:
                        result.success = True
                        result.result = exec_result[0]
            else:
                # Execute without timeout
                local_context = {}
                exec(python_code, exec_context, local_context)
                result.success = True
                result.result = local_context.get('result', True)
        
        except Exception as e:
            result.success = False
            result.error = f"Fallback execution error: {str(e)}"
        
        return result
    
    def _prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for safe execution."""
        safe_context = {}
        
        # Add variables from variable system
        if self.variable_system:
            if hasattr(self.variable_system, 'variables'):
                safe_context.update(self.variable_system.variables)
            if hasattr(self.variable_system, 'flags'):
                safe_context.update(self.variable_system.flags)
        
        # Add provided context
        safe_context.update(context)
        
        # Ensure all values are JSON serializable
        for key, value in safe_context.items():
            try:
                json.dumps(value)
            except (TypeError, ValueError):
                safe_context[key] = str(value)
        
        return safe_context
    
    def _create_wrapper_script(self, user_script: str, context_file: str, 
                             output_file: str) -> str:
        """Create a wrapper script for safe execution."""
        # Convert Windows paths to use forward slashes for JavaScript
        context_file_js = context_file.replace('\\', '/')
        output_file_js = output_file.replace('\\', '/')
        
        return f'''
const fs = require('fs');
const path = require('path');

// Execution result
const result = {{
    success: false,
    result: null,
    error: null,
    console_logs: [],
    variables_set: {{}}
}};

// Override console.log to capture output
const originalLog = console.log;
console.log = function(...args) {{
    result.console_logs.push(args.map(arg => String(arg)).join(' '));
}};

// Load context
let context = {{}};
try {{
    const contextData = fs.readFileSync('{context_file_js}', 'utf8');
    context = JSON.parse(contextData);
}} catch (e) {{
    result.error = 'Failed to load context: ' + e.message;
}}

// DVGE API functions
const DVGE = {{
    setVariable: function(name, value) {{
        context[name] = value;
        result.variables_set[name] = value;
    }},
    getVariable: function(name) {{
        return context[name];
    }},
    setFlag: function(name, value) {{
        context[name] = Boolean(value);
        result.variables_set[name] = Boolean(value);
    }},
    getFlag: function(name) {{
        return Boolean(context[name]);
    }},
    log: function(...args) {{
        console.log(...args);
    }},
    random: function() {{
        return Math.random();
    }},
    randomInt: function(min, max) {{
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }},
    randomChoice: function(array) {{
        return array[Math.floor(Math.random() * array.length)];
    }},
    formatText: function(template, ...args) {{
        return template.replace(/\\{{(\\d+)\\}}/g, (match, index) => {{
            return args[parseInt(index)] || match;
        }});
    }}
}};

// Make context variables globally available
Object.assign(global, context);
global.DVGE = DVGE;

// Disable dangerous functions
global.eval = undefined;
global.Function = undefined;
global.require = function(module) {{
    throw new Error('require() is not allowed in sandbox');
}};

try {{
    // Execute user script
    const userResult = (function() {{
        {user_script}
    }})();
    
    result.success = true;
    result.result = userResult;
}} catch (e) {{
    result.success = false;
    result.error = e.message;
}}

// Write result to output file
try {{
    fs.writeFileSync('{output_file_js}', JSON.stringify(result, null, 2));
}} catch (e) {{
    console.error('Failed to write output:', e.message);
}}
'''
    
    def _convert_js_to_python(self, js_code: str) -> str:
        """Convert simple JavaScript to Python (very basic conversion)."""
        # This is a very simplified converter for basic cases
        python_code = js_code
        
        # Replace JavaScript keywords and syntax
        replacements = [
            ('var ', ''),
            ('let ', ''),
            ('const ', ''),
            ('function ', 'def '),
            ('true', 'True'),
            ('false', 'False'),
            ('null', 'None'),
            ('undefined', 'None'),
            ('===', '=='),
            ('!==', '!='),
            ('&&', ' and '),
            ('||', ' or '),
            ('!', ' not '),
        ]
        
        for js_pattern, py_replacement in replacements:
            python_code = python_code.replace(js_pattern, py_replacement)
        
        # Handle return statement (make it assign to result variable)
        lines = python_code.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('return '):
                # Replace return with assignment to result
                value = stripped[7:]  # Remove 'return '
                processed_lines.append(f"result = {value}")
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def validate_script(self, script_code: str) -> Dict[str, Any]:
        """Validate script syntax and check for security issues."""
        errors = []
        warnings = []
        
        # Check for blocked functions
        for blocked_func in self.blocked_functions:
            if blocked_func in script_code:
                errors.append(f"Blocked function '{blocked_func}' found in script")
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            (r'require\s*\(', "require() calls are not allowed"),
            (r'import\s+', "import statements are not allowed"),
            (r'process\.', "process object access is not allowed"),
            (r'fs\.', "filesystem access is not allowed"),
            (r'child_process', "child process spawning is not allowed"),
            (r'__.*__', "access to internal objects is not allowed")
        ]
        
        import re
        for pattern, message in dangerous_patterns:
            if re.search(pattern, script_code):
                errors.append(message)
        
        # Try basic syntax validation if Node.js is available
        if self.nodejs_available:
            try:
                # Create a simple syntax check script
                test_script = f'''
try {{
    // Wrap in function to check syntax
    (function() {{
        {script_code}
    }});
    console.log(JSON.stringify({{success: true}}));
}} catch (e) {{
    console.log(JSON.stringify({{success: false, error: e.message}}));
}}
'''
                result = subprocess.run(
                    ['node', '-e', test_script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.stdout:
                    try:
                        syntax_result = json.loads(result.stdout.strip())
                        if not syntax_result.get('success'):
                            errors.append(f"Syntax error: {syntax_result.get('error')}")
                    except json.JSONDecodeError:
                        warnings.append("Could not parse syntax check result")
            
            except Exception as e:
                warnings.append(f"Syntax validation failed: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    # DVGE API implementations
    def _api_set_variable(self, name: str, value: Any):
        """Set a variable in the variable system."""
        if self.variable_system and hasattr(self.variable_system, 'set_variable'):
            self.variable_system.set_variable(name, value)
    
    def _api_get_variable(self, name: str) -> Any:
        """Get a variable from the variable system."""
        if self.variable_system and hasattr(self.variable_system, 'get_variable'):
            return self.variable_system.get_variable(name)
        return None
    
    def _api_set_flag(self, name: str, value: bool):
        """Set a flag in the variable system."""
        if self.variable_system and hasattr(self.variable_system, 'set_flag'):
            self.variable_system.set_flag(name, bool(value))
    
    def _api_get_flag(self, name: str) -> bool:
        """Get a flag from the variable system."""
        if self.variable_system and hasattr(self.variable_system, 'get_flag'):
            return self.variable_system.get_flag(name)
        return False
    
    def _api_log(self, *args):
        """Log function for scripts."""
        print("SCRIPT LOG:", *args)
    
    def _api_random(self) -> float:
        """Generate random number 0-1."""
        import random
        return random.random()
    
    def _api_random_int(self, min_val: int, max_val: int) -> int:
        """Generate random integer in range."""
        import random
        return random.randint(min_val, max_val)
    
    def _api_random_choice(self, choices: List[Any]) -> Any:
        """Choose random item from list."""
        import random
        return random.choice(choices) if choices else None
    
    def _api_format_text(self, template: str, *args) -> str:
        """Format text template with arguments."""
        try:
            return template.format(*args)
        except:
            return template
    
    def _api_wait(self, seconds: float):
        """Wait for specified seconds (limited)."""
        import time
        # Limit wait time for security
        wait_time = min(seconds, 5.0)
        time.sleep(wait_time)
    
    def _api_show_message(self, message: str):
        """Show message to user (placeholder)."""
        print(f"MESSAGE: {message}")
    
    def get_api_documentation(self) -> Dict[str, str]:
        """Get documentation for available API functions."""
        return {
            "DVGE.setVariable(name, value)": "Set a story variable",
            "DVGE.getVariable(name)": "Get a story variable value",
            "DVGE.setFlag(name, value)": "Set a story flag (boolean)",
            "DVGE.getFlag(name)": "Get a story flag value",
            "DVGE.log(...args)": "Log messages for debugging",
            "DVGE.random()": "Get random number between 0 and 1",
            "DVGE.randomInt(min, max)": "Get random integer in range",
            "DVGE.randomChoice(array)": "Choose random item from array",
            "DVGE.formatText(template, ...args)": "Format text template with arguments"
        }