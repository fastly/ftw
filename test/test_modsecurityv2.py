import pytest
from ftw.ftw import testrunner, errors

@pytest.fixture
def modsec_logger_obj():
    """
    Modsec logger object to access in the verifier
    @TODO
    """
    return None

def test_modsecurityv2(modsec_logger_obj, ruleset, test, destaddr):
    """
    Modsec specific test
    """
    runner = testrunner.TestRunner() 
    try:
        for stage in test.stages:
            if destaddr is not None:
                stage.input.dest_addr = destaddr
            runner.run_stage(stage, modsec_logger_obj)
    except errors.TestError as e:
        e.args[1]['meta'] = ruleset.meta
        pytest.fail('Failure! Message -> {0}, Context -> {1}'
                        .format(e.args[0],e.args[1]))
