from typing import Any, Callable, ClassVar, Dict, Optional
from contextlib import ContextDecorator
from dataclasses import dataclass, field
import time


class TimerError(Exception):
    """Custom exception used to report errors in use of Timer class"""


@dataclass
class Timer(ContextDecorator):
    """Time code using a class, context manager, or decorator
    To use as a class use .start() and .stop()

    To use as context manager just use: with Timer(name='name_of timer')

    To use as a decorator: just add above definitions: @Timer() or @Timer(name="name_of_timer") etc

    Arguments:
        name : str
            Optional - name for the timer, stored in a dict of timers so can reference them later
        silent : bool
            Optional - Default is False.  If True then no output from the output callable will not be output.
        output : Callable
            Optional - Callable object. Default is print. But could use a file object to be written to etc.
        logger : logging
            Optional - Pass a logging logger with logging level  e.g. logger.info

    """

    timers: ClassVar[Dict[str, float]] = dict()
    name: Optional[str] = None
    silent: Optional[bool] = False
    text: str = "Time taken: {:0.4f} seconds"
    output: Optional[Callable[[str], None]] = print
    logger: Any = None
    _start_time: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Add timer to dict of timers"""
        if self.name:
            self.timers.setdefault(self.name, 0)

    def start(self) -> None:
        """Start a timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and return the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        time_taken = time.perf_counter() - self._start_time

        self.clear_timer_for_next_use()

        self.report_time(time_taken)

        return time_taken

    def clear_timer_for_next_use(self):
        self._start_time = None

    def report_time(self, time_taken):
        if not self.silent:
            self.output(self.text.format(time_taken))
        if self.logger:
            self.logger(self.text.format(time_taken))
        if self.name:
            self.timers[self.name] += time_taken

    def __enter__(self) -> "Timer":
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Stop the context manager timer"""
        self.stop()
