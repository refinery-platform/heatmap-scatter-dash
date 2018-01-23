import cProfile
import pstats
import contextlib


@contextlib.contextmanager
def active_profiler():
    # Inspired by https://gist.github.com/davesque/6644474
    p = cProfile.Profile()

    p.enable()
    yield
    p.disable()

    stats = pstats.Stats(p).sort_stats('cumulative')
    stats.print_stats(r'context/app')


@contextlib.contextmanager
def null_profiler():
    yield
