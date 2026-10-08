# Null Device Redirector

A tiny context manager that redirects `sys.stdout` and `sys.stderr` to `os.devnull` and restores them on exit.

```python
import sys

from null_device_redirector import suppress_output

with suppress_output():
    print("goes nowhere")
    print("also nowhere", file=sys.stderr)

print("this prints again")
```

## Why

Command-line tools and library code sometimes write chatter to stdout/stderr that you do not want when invoking them from your own program. Redirecting streams with `contextlib.redirect_stdout(open(os.devnull, "w"))` per stream is repetitive and easy to get wrong on exception paths. This library gives you one object that handles both streams and guarantees restoration even when an exception propagates through the block.

## Edge you will hit

`suppress_output` swaps the `sys.stdout` and `sys.stderr` *module attributes*. If user code binds a local variable to `sys.stdout` before entering the block, that variable keeps writing to the original stream — redirection only affects code that reads `sys.stdout` at call time. This is a deliberate choice: trying to monkeypatch existing stream objects themselves is far more fragile than swapping the attributes, and the documented behaviour is predictable. If you need pre-bound references suppressed, rebind them after entering the block.

## Exports

- `suppress_output` — the context manager class described above.
