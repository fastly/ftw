class TestError(Exception):
    def __init___(self, msg, context_args):
        Exception.__init__(self, "{0} {1}".format(msg, context_args))
