"""
SPIKE's main.py will exit cleanly when it sees a KeyboardInterrupt.
This provides a means of breaking out of the SPIKE hub UI so that we
can access the REPL prompt.
"""
raise KeyboardInterrupt()
