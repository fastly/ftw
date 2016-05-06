import pytest

def get_rulesets(ruledir):
    """
    List of ruleset objects extracted from the yaml directory
    """
    from ftw import ruleset, util
    yaml_files = util.get_files(ruledir, 'yaml')
    extracted_files = util.extract_yaml(yaml_files)
    rulesets = []
    for extracted_yaml in extracted_files:
        rulesets.append(ruleset.Ruleset(extracted_yaml))
    return rulesets

def enrich_meta(meta, test):
    """
    Enrich metadata dictionary since metafunc.parametrize will only pass along
    the first variable
    """
    meta['rule_id'] = test.rule_id
    return (meta, test)

def get_testdata(meta, tests):
    """
    In order to do test-level parametrization (is this a word?), we have to
    bundle the test data into tuples so its broken out and distributed
    with accurate metadata
    """
    return map(lambda test: enrich_meta(meta, test), tests) 

def test_id(meta):
    """
    Dynamically names tests, useful for when we are running dozens to hundreds
    of tests
    """
    return '%s_ruleid_%s' % (meta['name'], meta['rule_id'])

def pytest_addoption(parser):
    """
    Adds command line options to py.test
    """
    parser.addoption('--ruledir', action='store', default='.',
        help='list of stringinputs to pass to test functions')

def pytest_generate_tests(metafunc):
    """
    Pre-test configurations, mostly used for parametrization
    """
    if metafunc.config.option.ruledir:
        rulesets = get_rulesets(metafunc.config.option.ruledir)
        if 'test' in metafunc.fixturenames and 'meta' in metafunc.fixturenames:
            for ruleset in rulesets:
                metafunc.parametrize(
                    'meta,test', 
                    get_testdata(ruleset.meta, ruleset.tests),
                    ids=test_id) 
