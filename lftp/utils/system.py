import sys
import gevent
import signal


def on_interrupt(handler):
    """
    Registers a signal handler function
    The handler function should not expect any arguments, and should return an
    integer that is passed to ``sys.exit()``. Exceptions raised in the handler
    will be propagated without being trapped.
    """

    def wrapper(*args, **kwargs):
        ret = handler()
        sys.exit(ret)

    gevent.signal(signal.SIGINT, wrapper)
    gevent.signal(signal.SIGTERM, wrapper)
    gevent.signal(signal.SIGSEGV, wrapper)
