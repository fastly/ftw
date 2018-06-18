import argparse
from ftw import util, testrunner

def diag_print(test, rule_id):
    print 'Running test %s from rule file %s' % (test.test_title, rule_id)

def build_journal(journal_file, ruledir, ruledir_recurse, tablename, destaddr, headers):
    util.instantiate_database(journal_file)
    rulesets = util.get_rulesets(ruledir, ruledir_recurse)
    for rule in rulesets:
        for test in rule.tests:
            runner = testrunner.TestRunner() 
            runner.run_test_build_journal(test.ruleset_meta['name'], test, journal_file, tablename, destaddr, diag_print, headers)

def main():
    parser = argparse.ArgumentParser(description='Build FTW Journal database')
    parser.add_argument('--journal', default='journal.sqlite',
        help='Path to journal default')
    parser.add_argument('--ruledir', required=True, 
        help='Path to rule directory')
    parser.add_argument('--ruledir_recurse', action='store_true',
        help='Recursively search rule directories')
    parser.add_argument('--tablename', default='ftw',
        help='Table name in journal sqlite database')
    parser.add_argument('--destaddr', default=None,
        help='Destination host for the payloads')
    parser.add_argument('--destaddr_as_host', action='store_true',
        help='Use destination address as the Host header')
    args = parser.parse_args()
    destaddr = args.destaddr
    journal_file = args.journal
    ruledir = args.ruledir
    ruledir_recurse = args.ruledir_recurse
    tablename = args.tablename
    headers = {}
    if args.destaddr_as_host:
        headers['Host'] = destaddr = args.destaddr
    build_journal(journal_file, ruledir, ruledir_recurse, tablename, destaddr, headers)

if __name__ == '__main__':
    main()
