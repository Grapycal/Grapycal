# how to interrupt at anytime?

Spawn a non-main thread, call `signal.raise_signal(signal.SIGINT)`, then the main thread will immediately be interrupted by `KeyboardInterrupt`

# strategy

Put the task loop that should be able to be interrupted in the main thread.
see thread.py