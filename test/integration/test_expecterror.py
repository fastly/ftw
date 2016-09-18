from ftw import ruleset, testrunner, http, errors
import pytest
import re
import random
import threading

def test_expecterror(ruleset, test):
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage)
