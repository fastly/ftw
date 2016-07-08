import abc


class LogChecker():
    """
    LogChecker is an abstract class that integrations with WAFs MUST implement.
    This class is used by the testrunner to test log lines against an expected
    regex
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.start = None
        self.end = None

    def set_times(self, start, end):
        self.start = start
        self.end = end

    @abc.abstractmethod
    def get_logs(self):
        """
        MUST be implemented, MUST return an array of strings
        These strings represent distinct log lines that were pulled from an
        outside logfile. The times are used by the testrunner to assist the
        implementers in pulling out the correct lines from the log file
        """
        pass
