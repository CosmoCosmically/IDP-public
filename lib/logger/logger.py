####################################################################################################
#
# Types related to the line sensors.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports
from utime import ticks_diff, ticks_ms  # type: ignore

# Local imports
from config import DEBUG, USB_DEBUG, LOG_LEVELS, LOG_LEVEL, LOG_FILE, MAX_LOG_SIZE


if DEBUG or USB_DEBUG:
    # Full logger
    class Logger:
        """
        File-backed logger with optional USB output and size truncation.
        """
        def __init__(self):
            self.f = open(LOG_FILE, "wb")
            self.size = 0
            self.start = ticks_ms()

        def log(self, msg, *args, level=LOG_LEVELS.DEBUG):
            """
            Log a formatted message if above configured log level.
            """
            if level < LOG_LEVEL:
                return
            msg = msg.format(*args)
            log_line = "{} {}\n".format(ticks_diff(ticks_ms(), self.start), msg)
            if USB_DEBUG:
                print(log_line)
                log_line_b = log_line.encode("ascii", "replace")
                self.size += len(log_line_b)
                try:
                    if self.size > MAX_LOG_SIZE:
                        # Truncate file
                        self.f.close()
                        self.f = open(LOG_FILE, "wb")
                        self.f.write(log_line_b)
                        self.size = len(log_line_b)
                    else:
                        self.f.write(log_line_b)
                except Exception:
                    # Never let logging kill the robot
                    pass

        def close(self):
            """
            Close the log file handle.
            """
            self.f.close()

    logger = Logger()
else:
    # Minimal prototype
    class LoggerProto:
        """
        Minimal no-op logger used when debugging is disabled.
        """
        def log(self, *args, **kwargs):
            return

        def close(self):
            return

    logger = LoggerProto()
