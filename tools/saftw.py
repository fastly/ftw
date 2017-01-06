#!/usr/bin/python
#
from ftw import ruleset, util, testrunner, http
import getopt
import os
import sys
import time
import re

class cmdopt(object):
    rule_path = None
    recurse = 0
    journal = None
    logfile = None
    timeout = 1
    replayjournal = 0
    debug = 0
    plugin = None
    rulematch = 0
    overload = {} 
    nocache = 0

def usage():
    print "Produce journal:"
    print "saftw -p <plugin> -j <journal file> -r <ftw rule/dir>"
    print "Process journal:"
    print "saftw -p <plugin> -J -l <logfile> -j <journal file>"
    sys.exit(1)

class waf_plugin(object):
    def load(self, name):
        if name == "varnish":
            return varnish_waf()
        if name == "modsec":
            return modsec_waf()
        raise

    def get_log_tag(self, now, title):
        raise NotImplementedError

    def match(self, rule, ln):
        raise NotImplementedError

class modsec_waf(waf_plugin):
    name = "modsec"

    def __init__(self):
        try:
            self.prog = re.compile('^.* \[id "(\d+)"')
        except:
            print "failed to compile regexp"
            sys.exit(1)
        super(modsec_waf, self).__init__()

    def get_log_tag(self, now, title):
        t = time.gmtime(now)
        ts = time.strftime("%a %b %d %H:%M:%S", t)
        '''
            NB: we need to return a list here on the off
            chance we are on a boundary
        '''
        return ts

    def match(self, rule, ln):
        m = self.prog.match(ln)
        if m == None:
            return False
        if int(m.group(1)) == rule:
            return True
        return False

class varnish_waf(waf_plugin):
    name = "varnish"

    def __init__(self):
        try:
            self.prog = re.compile(r'^.*rule id \"(\d+)\"')
        except:
            print "failed to compile regular expression"
            sys.exit(1)
        super(varnish_waf, self).__init__()

    def get_log_tag(self, now, title):
        ret = "{}_{}".format(now, title)
        return ret

    def get_rule(self, ln):
        fe = ln.split(",")
        try:
            rule = fe[15]
        except IndexError:
            rule = None
        return rule

    def match(self, rule, ln):
        m = self.get_rule(ln)
        if m == None:
            return False
        if int(m) == rule:
            return True
        return False

class journal(object):
    def __init__(self, path):
        try:
            self.jfp = open(path, 'w')
        except IOError as e:
            print "failed to open journal: {}".format(e.strerror)
            raise
        hdr = "# timestamp, test title, log tag, invert match, ruleid, http response\n"
        try:
            self.jfp.write(hdr)
        except IOError as e:
            print "failed to write out jornal header"
            raise

    def add_entry(self, now, test_title, logtag, inv, resp):
        if resp == None:
            status = "NONE"
        else:
            status = resp.status
        fe = test_title.split('-')
        record = "{},{},{},{},{},{}\n".format(now, test_title, logtag, inv, fe[0], status)
        try:
            self.jfp.write(record)
        except IOError as e:
            print "failed to write journal entry: {}".format(e.strerror)
            exit(1)

    def commit(self):
        try:
            self.jfp.close()
        except:
            print "failed to commit (close) journal"
            sys.exit(1)

def searchvarlog(logtag, co):
    try:
        vl = open(co.logfile, "r")
    except IOError as e:
        print "failed to open logfile: {}".format(e.strerror)
        sys.exit(1)
    lines = []
    match = None
    for ln in vl.readlines():
        if logtag in ln:
            ln = ln.rstrip()
            lines.append(ln)
    vl.close()
    return lines

def print_result(rule, test_name, match):
    if match:
        print "{} {} PASSED".format(rule, test_name)
    else:
        print "{} {} FAILED".format(rule, test_name)

def replay_journal(co):
    try:
        f = open(co.journal, 'r')
    except IOError as e:
        print "unable to open journal: {}".format(e.strerror)
        sys.exit(1)
    for ln in f.readlines():
        if ln[0] == '#' or ln[0] == '\r' or ln[0] == '\n':
            continue
        ln = ln.rstrip()
        fe = ln.split(",")
        try:
            invert = int(fe[3])
        except ValueError:
            print "invalid integer: {}".format(fe[3])
            sys.exit(1)
        try:
            rule = int(fe[4])
        except ValueError:
            print "invalid rule {}".format(fe[4])
            sys.exit(1)
        if co.debug > 0:
            print "processing test {}".format(fe[1])
        logs = searchvarlog(fe[2], co)
        match = False
        rules = []
        for log in logs:
            if co.rulematch == 1:
                rule = co.plugin.get_rule(log)
                rules.append(rule)
                continue
            match = co.plugin.match(rule, log)
            if match == True:
                if co.debug > 0:
                    print "matching log: {}".format(log)
                break
            else:
                if co.debug > 0:
                    print "un-related rules: {}".format(log)
        if co.rulematch == 1:
            rlist = ",".join(rules)
            print "{} {}".format(fe[1], rlist)
            continue
        if invert == 1:
            match = not match
        print_result(rule, fe[1], match)

def parse_overload(opt, cmd):
    f = opt.split("=")
    if len(f) != 2:
        print "invalid key/value specification"
        sys.exit(1)
    cmd.overload[f[0]] = f[1]

def do_overload(stage, co):
    if "port" in co.overload.keys():
        stage.input.port = int(co.overload["port"])
    if "dest_addr" in co.overload.keys():
        stage.input.dest_addr = co.overload["dest_addr"]
    if "Host" in co.overload.keys():
        stage.input.headers["Host"] = co.overload["Host"]

def main():
    co = cmdopt()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "no:mp:dJt:r:Rj:l:w")
    except getopt.GetoptError as e:
        usage()
    for o, a in opts:
        if o == "-m":
            co.rulematch = 1
        if o == "-d":
            co.debug = 1
        if o == "-t":
            co.timeout = int(a)
        if o == "-r":
            co.rule_path = a
        if o == "-J":
            co.replayjournal = 1
        if o == "-j":
            co.journal = a
        if o == "-R":
            co.recurse = 1
        if o == "-p":
            co.plugin = a
        if o == "-o":
            parse_overload(a, co)
        if o == "-l":
            co.logfile = a
        if o == "-n":
            co.nocache = 1
    if co.plugin == None:
        usage()
    try:
        ob = waf_plugin()
        waf_plug = ob.load(co.plugin)
    except Exception as e:
        print e
        print "Invalid plugin specifed"
        sys.exit(1)
    co.plugin = waf_plug
    if co.rule_path == None and co.replayjournal == 0:
        usage()
    if co.journal == None:
        usage()
    if co.replayjournal == 1:
        if co.logfile == None:
            print "must specify logfile"
            sys.exit(1)
        replay_journal(co)
        return 0
    try:
        jrnl = journal(co.journal)
    except IOError as e:
        print "failed to initialize journal: {}".format(e.strerror)
        sys.exit(1)
    testfiles = util.get_rulesets(co.rule_path, co.recurse)
    for tf in testfiles:
        for test in tf.tests:
            now = time.time()
            logtag = waf_plug.get_log_tag(now, test.test_title)
            runner = testrunner.TestRunner()
            for stage in test.stages:
                do_overload(stage, co)
                odict = stage.output.output_dict
                invert = 0
                if "no_log_contains" in odict.keys():
                    invert = 1
                headers = stage.input.headers
                if co.nocache == 1:
                    if not "Cache-Control" in headers.keys():
                        stage.input.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                if not "X-Request-Id" in headers.keys():
                    stage.input.headers["X-Request-Id"] = logtag
                try:
                    hua = http.HttpUA()
                except:
                    print "failed to initialize UA object"
                    sys.exit(1)
                try:
                    runner.run_stage(stage, None, hua)
                except Exception as e:
                    print e
                    pass
                if co.debug == 1:
                    print "Executed test {}".format(test.test_title)
                jrnl.add_entry(now, test.test_title, logtag, invert, hua.response_object)
    return 0
    
if __name__ == "__main__":
    main()
0

