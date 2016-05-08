import pytest
from ftw import testrunner

@pytest.fixture
def modsec_logger_obj():
    """
    Modsec logger object to access in the verifier
    @TODO
    """
    return 0

def test_modsecurityv2(modsec_logger_obj, meta, test):
    """
    Modsec specific test
    """
    runner = testrunner.TestRunner() 
    for stage in test.stages:
        runner.run_stage(stage)
