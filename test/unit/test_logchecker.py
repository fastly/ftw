from ftw.ftw import logchecker
import pytest

def test_logchecker():
    with pytest.raises(TypeError) as excinfo:
        checker = logchecker.LogChecker() 
