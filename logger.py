class Logger(object):
    def __init__(self, log_function):
        self.log_function = log_function

    def debug(self, msg):
        self.log_function(msg)

    def info(self, msg):
        self.log_function(msg)

    def warning(self, msg):
        self.log_function(msg)

    def error(self, msg):
        self.log_function(msg)

    def critical(self, msg):
        self.log_function(msg)