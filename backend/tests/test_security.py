"""Tests for bot security validation"""
import pytest
from app.bot_security import BotSecurityValidator, SecurityLogger


class TestBotSecurityValidator:
    """Test security validation of bot code"""
    
    def test_valid_bot_code(self):
        """Test that valid bot code passes validation"""
        validator = BotSecurityValidator()
        code = """
import random
import typing

class MyBot:
    def __init__(self, my_color: int, opp_color: int):
        self.my_color = my_color
        self.opp_color = opp_color
    
    def select_move(self, board: list[list[int]]) -> tuple[int, int]:
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert is_valid
        assert len(violations) == 0
    
    def test_dangerous_import_os(self):
        """Test that importing os is blocked"""
        validator = BotSecurityValidator()
        code = """
import os

class MyBot:
    def select_move(self, board):
        os.system("echo hacked")
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert len(violations) > 0
        assert any('os' in str(v).lower() for v in violations)
    
    def test_dangerous_import_subprocess(self):
        """Test that importing subprocess is blocked"""
        validator = BotSecurityValidator()
        code = """
import subprocess

class MyBot:
    def select_move(self, board):
        subprocess.run(['ls'])
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('subprocess' in str(v).lower() for v in violations)
    
    def test_dangerous_import_requests(self):
        """Test that importing requests is blocked"""
        validator = BotSecurityValidator()
        code = """
import requests

class MyBot:
    def select_move(self, board):
        requests.get('http://evil.com')
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('requests' in str(v).lower() for v in violations)
    
    def test_disallowed_import(self):
        """Test that non-allowed imports are blocked"""
        validator = BotSecurityValidator()
        code = """
import numpy

class MyBot:
    def select_move(self, board):
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('numpy' in str(v).lower() for v in violations)
    
    def test_allowed_imports(self):
        """Test that allowed imports work"""
        validator = BotSecurityValidator()
        code = """
import random
import typing
import time
import math
import copy
import collections
from itertools import product
from functools import lru_cache

class MyBot:
    def select_move(self, board):
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert is_valid
        assert len(violations) == 0
    
    def test_eval_function_blocked(self):
        """Test that eval() is blocked"""
        validator = BotSecurityValidator()
        code = """
class MyBot:
    def select_move(self, board):
        result = eval("1 + 1")
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('eval' in str(v).lower() for v in violations)
    
    def test_exec_function_blocked(self):
        """Test that exec() is blocked"""
        validator = BotSecurityValidator()
        code = """
class MyBot:
    def select_move(self, board):
        exec("print('hacked')")
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('exec' in str(v).lower() for v in violations)
    
    def test_open_function_blocked(self):
        """Test that open() is blocked"""
        validator = BotSecurityValidator()
        code = """
class MyBot:
    def select_move(self, board):
        with open('/etc/passwd') as f:
            data = f.read()
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('open' in str(v).lower() or 'file' in str(v).lower() for v in violations)
    
    def test_dangerous_attribute_access(self):
        """Test that dangerous attributes are blocked"""
        validator = BotSecurityValidator()
        code = """
class MyBot:
    def select_move(self, board):
        x = self.__class__.__bases__
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('__bases__' in str(v) or '__class__' in str(v) for v in violations)
    
    def test_import_builtin_blocked(self):
        """Test that __import__ is blocked"""
        validator = BotSecurityValidator()
        code = """
class MyBot:
    def select_move(self, board):
        os = __import__('os')
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('__import__' in str(v).lower() for v in violations)
    
    def test_syntax_error_detected(self):
        """Test that syntax errors are detected"""
        validator = BotSecurityValidator()
        code = """
class MyBot
    def select_move(self, board):
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('syntax' in str(v).lower() for v in violations)
    
    def test_multiple_violations(self):
        """Test detection of multiple violations"""
        validator = BotSecurityValidator()
        code = """
import os
import sys
import subprocess

class MyBot:
    def select_move(self, board):
        eval("print('test')")
        os.system("ls")
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert len(violations) >= 4  # At least os, sys, subprocess, eval
    
    def test_delete_operation_blocked(self):
        """Test that delete operations are blocked"""
        validator = BotSecurityValidator()
        code = """
class MyBot:
    def select_move(self, board):
        x = 1
        del x
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('delete' in str(v).lower() for v in violations)
    
    def test_from_import_dangerous(self):
        """Test that dangerous from imports are blocked"""
        validator = BotSecurityValidator()
        code = """
from os import system

class MyBot:
    def select_move(self, board):
        system("ls")
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert not is_valid
        assert any('os' in str(v).lower() for v in violations)
    
    def test_from_import_allowed(self):
        """Test that allowed from imports work"""
        validator = BotSecurityValidator()
        code = """
from random import choice
from typing import List, Tuple

class MyBot:
    def select_move(self, board):
        return (0, 0)
"""
        is_valid, violations = validator.validate(code, "test_bot.py")
        assert is_valid
        assert len(violations) == 0


class TestSecurityLogger:
    """Test security logging functionality"""
    
    def test_log_security_event(self, tmp_path):
        """Test logging a security event"""
        # Use a temporary directory
        import os
        original_dir = SecurityLogger.QUARANTINE_DIR
        original_log = SecurityLogger.SECURITY_LOG_FILE
        
        try:
            # Set up temporary paths
            SecurityLogger.QUARANTINE_DIR = str(tmp_path / "quarantine")
            SecurityLogger.SECURITY_LOG_FILE = str(tmp_path / "quarantine" / "security_log.json")
            
            logger = SecurityLogger()
            
            from app.bot_security import SecurityViolation
            violations = [
                SecurityViolation("TEST", "Test violation", line_number=1)
            ]
            request_info = {
                "ip": "127.0.0.1",
                "user_agent": "test"
            }
            
            quarantine_path = logger.log_security_event(
                filename="test.py",
                violations=violations,
                request_info=request_info,
                file_content=b"test content"
            )
            
            # Check that file was quarantined
            assert os.path.exists(quarantine_path)
            
            # Check that log was created
            assert os.path.exists(SecurityLogger.SECURITY_LOG_FILE)
            
            # Check log contents
            logs = logger.get_security_log()
            assert len(logs) == 1
            assert logs[0]['filename'] == 'test.py'
            assert logs[0]['request_info']['ip'] == '127.0.0.1'
            
        finally:
            # Restore original paths
            SecurityLogger.QUARANTINE_DIR = original_dir
            SecurityLogger.SECURITY_LOG_FILE = original_log
    
    def test_get_security_log_limit(self, tmp_path):
        """Test limiting the number of log entries returned"""
        import os
        original_dir = SecurityLogger.QUARANTINE_DIR
        original_log = SecurityLogger.SECURITY_LOG_FILE
        
        try:
            # Set up temporary paths
            SecurityLogger.QUARANTINE_DIR = str(tmp_path / "quarantine")
            SecurityLogger.SECURITY_LOG_FILE = str(tmp_path / "quarantine" / "security_log.json")
            
            logger = SecurityLogger()
            
            from app.bot_security import SecurityViolation
            
            # Log multiple events
            for i in range(5):
                violations = [SecurityViolation("TEST", f"Test {i}")]
                request_info = {"ip": f"127.0.0.{i}"}
                logger.log_security_event(
                    filename=f"test{i}.py",
                    violations=violations,
                    request_info=request_info,
                    file_content=b"test"
                )
            
            # Get limited logs
            logs = logger.get_security_log(limit=3)
            assert len(logs) == 3
            
            # Get all logs
            all_logs = logger.get_security_log()
            assert len(all_logs) == 5
            
        finally:
            SecurityLogger.QUARANTINE_DIR = original_dir
            SecurityLogger.SECURITY_LOG_FILE = original_log
