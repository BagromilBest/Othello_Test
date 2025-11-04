"""Security validation and sandboxing for uploaded bot files"""
import ast
import os
import json
from datetime import datetime, UTC
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path


class SecurityViolation:
    """Represents a security violation found in uploaded code"""
    
    def __init__(self, violation_type: str, description: str, line_number: Optional[int] = None, 
                 code_snippet: Optional[str] = None):
        self.violation_type = violation_type
        self.description = description
        self.line_number = line_number
        self.code_snippet = code_snippet
    
    def __repr__(self):
        if self.line_number:
            return f"{self.violation_type} at line {self.line_number}: {self.description}"
        return f"{self.violation_type}: {self.description}"
    
    def to_dict(self):
        return {
            "type": self.violation_type,
            "description": self.description,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet
        }


class BotSecurityValidator:
    """Validates bot code for security issues"""
    
    # Allowed imports for Reversi bots
    ALLOWED_IMPORTS = {
        'random', 'typing', 'time', 'math', 'copy', 'collections',
        'itertools', 'functools', 'dataclasses', 'enum', 'abc'
    }
    
    # Dangerous imports that should be blocked
    DANGEROUS_IMPORTS = {
        'os', 'sys', 'subprocess', 'shutil', 'glob', 'pathlib',
        'requests', 'urllib', 'http', 'socket', 'socketserver',
        'pickle', 'shelve', 'marshal', 'tempfile', 'io',
        'importlib', 'runpy', '__import__', 'eval', 'exec',
        'compile', 'open', 'input', 'file', 'execfile',
        'ctypes', 'multiprocessing', 'threading', 'asyncio',
        'webbrowser', 'platform', 'site', 'pty', 'pwd', 'grp',
        'resource', 'signal', 'codecs', 'builtins', '__builtin__'
    }
    
    # Dangerous built-in functions
    DANGEROUS_BUILTINS = {
        'eval', 'exec', 'compile', '__import__', 'open', 'input',
        'execfile', 'file', 'reload', 'vars', 'dir', 'globals', 'locals',
        'delattr', 'setattr', 'getattr', 'hasattr'
    }
    
    # Dangerous attributes that can be used for introspection/modification
    DANGEROUS_ATTRIBUTES = {
        '__dict__', '__class__', '__bases__', '__subclasses__',
        '__globals__', '__code__', '__builtins__', '__import__',
        '__loader__', '__spec__', '__path__', '__file__'
    }
    
    def __init__(self):
        self.violations: List[SecurityViolation] = []
    
    def validate(self, code: str, filename: str) -> Tuple[bool, List[SecurityViolation]]:
        """
        Validate Python code for security issues.
        
        Args:
            code: Python source code as string
            filename: Name of the file (for error messages)
            
        Returns:
            Tuple of (is_valid, violations)
            is_valid: True if code passes all security checks
            violations: List of SecurityViolation objects found
        """
        self.violations = []
        
        # Parse the code
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            self.violations.append(SecurityViolation(
                "SYNTAX_ERROR",
                f"Invalid Python syntax: {str(e)}",
                line_number=e.lineno
            ))
            return False, self.violations
        
        # Analyze the AST
        self._check_imports(tree, code)
        self._check_function_calls(tree, code)
        self._check_attributes(tree, code)
        self._check_dangerous_patterns(tree, code)
        
        is_valid = len(self.violations) == 0
        return is_valid, self.violations
    
    def _check_imports(self, tree: ast.AST, code: str):
        """Check for dangerous or disallowed imports"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in self.DANGEROUS_IMPORTS:
                        self.violations.append(SecurityViolation(
                            "DANGEROUS_IMPORT",
                            f"Import of dangerous module '{alias.name}' is not allowed",
                            line_number=node.lineno,
                            code_snippet=self._get_line(code, node.lineno)
                        ))
                    elif module_name not in self.ALLOWED_IMPORTS:
                        self.violations.append(SecurityViolation(
                            "DISALLOWED_IMPORT",
                            f"Import of module '{alias.name}' is not in the allowed list. "
                            f"Allowed modules: {', '.join(sorted(self.ALLOWED_IMPORTS))}",
                            line_number=node.lineno,
                            code_snippet=self._get_line(code, node.lineno)
                        ))
            
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module.split('.')[0] if node.module else ''
                if module_name in self.DANGEROUS_IMPORTS:
                    self.violations.append(SecurityViolation(
                        "DANGEROUS_IMPORT",
                        f"Import from dangerous module '{node.module}' is not allowed",
                        line_number=node.lineno,
                        code_snippet=self._get_line(code, node.lineno)
                    ))
                elif module_name and module_name not in self.ALLOWED_IMPORTS:
                    self.violations.append(SecurityViolation(
                        "DISALLOWED_IMPORT",
                        f"Import from module '{node.module}' is not in the allowed list. "
                        f"Allowed modules: {', '.join(sorted(self.ALLOWED_IMPORTS))}",
                        line_number=node.lineno,
                        code_snippet=self._get_line(code, node.lineno)
                    ))
    
    def _check_function_calls(self, tree: ast.AST, code: str):
        """Check for dangerous function calls"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                
                # Handle direct function calls like eval()
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                
                if func_name and func_name in self.DANGEROUS_BUILTINS:
                    self.violations.append(SecurityViolation(
                        "DANGEROUS_FUNCTION",
                        f"Call to dangerous built-in function '{func_name}' is not allowed",
                        line_number=node.lineno,
                        code_snippet=self._get_line(code, node.lineno)
                    ))
    
    def _check_attributes(self, tree: ast.AST, code: str):
        """Check for access to dangerous attributes"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr in self.DANGEROUS_ATTRIBUTES:
                    self.violations.append(SecurityViolation(
                        "DANGEROUS_ATTRIBUTE",
                        f"Access to dangerous attribute '{node.attr}' is not allowed",
                        line_number=node.lineno,
                        code_snippet=self._get_line(code, node.lineno)
                    ))
    
    def _check_dangerous_patterns(self, tree: ast.AST, code: str):
        """Check for other dangerous patterns"""
        for node in ast.walk(tree):
            # Check for file operations (even without importing)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'open':
                        self.violations.append(SecurityViolation(
                            "FILE_OPERATION",
                            "File operations are not allowed in bot code",
                            line_number=node.lineno,
                            code_snippet=self._get_line(code, node.lineno)
                        ))
            
            # Check for attempts to delete attributes
            if isinstance(node, ast.Delete):
                self.violations.append(SecurityViolation(
                    "DANGEROUS_OPERATION",
                    "Delete operations are not allowed",
                    line_number=node.lineno,
                    code_snippet=self._get_line(code, node.lineno)
                ))
    
    def _get_line(self, code: str, line_number: int) -> str:
        """Get a specific line from the code"""
        try:
            lines = code.split('\n')
            if 0 < line_number <= len(lines):
                return lines[line_number - 1].strip()
        except:
            pass
        return ""


class SecurityLogger:
    """Logs security events for review"""
    
    QUARANTINE_DIR = "quarantine"
    SECURITY_LOG_FILE = "quarantine/security_log.json"
    
    def __init__(self):
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.QUARANTINE_DIR, exist_ok=True)
    
    def log_security_event(self, filename: str, violations: List[SecurityViolation], 
                          request_info: Dict[str, Any], file_content: bytes):
        """
        Log a security event and quarantine the file.
        
        Args:
            filename: Name of the uploaded file
            violations: List of security violations found
            request_info: Information about the request (IP, user agent, etc.)
            file_content: Content of the flagged file
        """
        # Ensure directories exist (in case paths were changed for testing)
        self._ensure_directories()
        
        timestamp = datetime.now(UTC).isoformat()
        
        # Save the flagged file to quarantine
        quarantine_filename = f"{timestamp.replace(':', '-')}_{filename}"
        quarantine_path = os.path.join(self.QUARANTINE_DIR, quarantine_filename)
        
        with open(quarantine_path, 'wb') as f:
            f.write(file_content)
        
        # Prepare log entry
        log_entry = {
            "timestamp": timestamp,
            "filename": filename,
            "quarantine_path": quarantine_path,
            "violations": [v.to_dict() for v in violations],
            "request_info": request_info
        }
        
        # Append to log file
        log_entries = []
        if os.path.exists(self.SECURITY_LOG_FILE):
            try:
                with open(self.SECURITY_LOG_FILE, 'r') as f:
                    log_entries = json.load(f)
            except:
                log_entries = []
        
        log_entries.append(log_entry)
        
        with open(self.SECURITY_LOG_FILE, 'w') as f:
            json.dump(log_entries, f, indent=2)
        
        return quarantine_path
    
    def get_security_log(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get security log entries.
        
        Args:
            limit: Maximum number of entries to return (most recent first)
            
        Returns:
            List of log entries
        """
        if not os.path.exists(self.SECURITY_LOG_FILE):
            return []
        
        try:
            with open(self.SECURITY_LOG_FILE, 'r') as f:
                log_entries = json.load(f)
            
            # Sort by timestamp, most recent first
            log_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            if limit:
                return log_entries[:limit]
            return log_entries
        except:
            return []


# Global instances
security_validator = BotSecurityValidator()
security_logger = SecurityLogger()
