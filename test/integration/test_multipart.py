from ftw import ruleset, logchecker, testrunner
import pytest
import random
import threading

def test_multipart(ruleset, test):
    runner = testrunner.TestRunner()
    for stage in test.stages:
        runner.run_stage(stage)
