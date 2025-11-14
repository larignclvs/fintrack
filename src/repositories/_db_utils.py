class DBProxy:
    """Minimal DBProxy shim for tests: forwards attribute access to the wrapped object.

    The real project had a more complex unwrapping to handle instrumentation wrappers.
    For unit tests we provide a simple transparent proxy.
    """
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, item):
        return getattr(self._obj, item)

    def __repr__(self):
        return f"DBProxy({self._obj!r})"
import types
from typing import Any


class DBProxy:
    """Proxy that resolves generator-like db objects into real Session instances on demand.

    This helps when instrumentation (mutmut) wraps dependencies and yields a generator
    object instead of the Session itself. The proxy will attempt to extract the session
    via next() and then forward attribute access to the real session object.
    """

    def __init__(self, db_obj: Any) -> None:
        self._orig = db_obj

    def _ensure(self) -> None:
        # If the original object is a generator-like object, try to extract a
        # real SQLAlchemy Session from nested generators. Mutmut instrumentation
        # can wrap values multiple times, so we attempt several unwrap steps.
        max_unwrap = 6
        unwrap_count = 0
        try:
            cur = self._orig
            while unwrap_count < max_unwrap and (
                isinstance(cur, types.GeneratorType) or hasattr(cur, "__next__")
            ):
                try:
                    cur = next(cur)
                except StopIteration:
                    break
                except Exception:
                    # if next() fails for some reason, stop unwrapping
                    break
                unwrap_count += 1

            # If the candidate looks like a DB session (has query/execute), use it
            if hasattr(cur, "query") or hasattr(cur, "execute"):
                self._orig = cur
        except Exception:
            # be conservative: keep original if anything goes wrong
            pass

    def __getattr__(self, name: str):
        self._ensure()
        return getattr(self._orig, name)
