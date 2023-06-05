'''
https://stackoverflow.com/questions/14890997/redirect-stdout-to-a-file-only-for-a-specific-thread#:~:text=You%20cannot%20redirect%20stdout%20for,messes%20with%20all%20of%20them.
'''

from contextlib import contextmanager
import threading
import sys
import io
from typing import Any
from . import local

# Save all of the objects for use later.
orig___stdout__ = sys.__stdout__
orig___stderr__ = sys.__stderr__
orig_stdout = sys.stdout
orig_stderr = sys.stderr
thread_proxies = {}


# def redirect():
#     """
#     Enables the redirect for the current thread's output to a single io
#     object and returns the object.

#     :return: The StringIO object.
#     :rtype: ``io.StringIO``
#     """
#     # Get the current thread's identity.
#     ident = threading.currentThread().ident

#     # Enable the redirect and return the io object.
#     thread_proxies[ident] = io.StringIO()
#     return thread_proxies[ident]


# def stop_redirect():
#     """
#     Enables the redirect for the current thread's output to a single io
#     object and returns the object.

#     :return: The final string value.
#     :rtype: ``str``
#     """
#     # Get the current thread's identity.
#     ident = threading.currentThread().ident

#     # Only act on proxied threads.
#     if ident not in thread_proxies:
#         return

#     # Read the value, close/remove the buffer, and return the value.
#     retval = thread_proxies[ident].getvalue()
#     thread_proxies[ident].close()
#     del thread_proxies[ident]
#     return retval

@contextmanager
def redirect(stringio: Any):
    """
    Context manager for redirecting stdout to a single io object.
    """
    ident = threading.currentThread().ident

    thread_proxies[ident] = stringio
    try:
        yield
    finally:
        del thread_proxies[ident]

def _get_stream(original):
    """
    Returns the inner function for use in the LocalProxy object.

    :param original: The stream to be returned if thread is not proxied.
    :type original: ``file``
    :return: The inner function for use in the LocalProxy object.
    :rtype: ``function``
    """
    def proxy():
        """
        Returns the original stream if the current thread is not proxied,
        otherwise we return the proxied item.

        :return: The stream object for the current thread.
        :rtype: ``file``
        """
        # Get the current thread's identity.
        ident = threading.currentThread().ident

        # Return the proxy, otherwise return the original.
        return thread_proxies.get(ident, original)

    # Return the inner function.
    return proxy


def enable_proxy(redirect_error=True):
    """
    Overwrites __stdout__, __stderr__, stdout, and stderr with the proxied
    objects.
    """
    sys.__stdout__ = local.LocalProxy(_get_stream(sys.__stdout__))
    sys.stdout = local.LocalProxy(_get_stream(sys.stdout))

    if redirect_error:
        sys.__stderr__ = local.LocalProxy(_get_stream(sys.__stderr__))
        sys.stderr = local.LocalProxy(_get_stream(sys.stderr))


def disable_proxy():
    """
    Overwrites __stdout__, __stderr__, stdout, and stderr with the original
    objects.
    """
    sys.__stdout__ = orig___stdout__
    sys.__stderr__ = orig___stderr__
    sys.stdout = orig_stdout
    sys.stderr = orig_stderr