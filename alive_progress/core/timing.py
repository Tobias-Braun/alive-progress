# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
import math

_99_HOURS_IN_SECONDS = 60 * 60 * 99


def to_elapsed_text(seconds, precise):
    seconds = round(seconds, 1 if precise else 0)
    if seconds < 60.:
        return '{:{}f}s'.format(seconds, .1 if precise else .0)

    minutes, seconds = divmod(seconds, 60.)
    if minutes < 60.:
        return '{:.0f}:{:0{}f}'.format(minutes, seconds, 4.1 if precise else 2.0)

    hours, minutes = divmod(minutes, 60.)
    return '{:.0f}:{:02.0f}:{:0{}f}'.format(hours, minutes, seconds, 4.1 if precise else 2.0)


def to_eta_text(eta):
    if eta is None or eta < 0. or eta >= _99_HOURS_IN_SECONDS:
        return '-'
    return to_elapsed_text(eta, False)


def simple_eta(logic_total, pos, rate):
    return min((logic_total - pos) / rate, _99_HOURS_IN_SECONDS)


def gen_simple_exponential_smoothing_eta(alfa, logic_total):
    """Implements a generator with a simple exponential smoothing of the
    eta time series.
    Given alfa and y_hat (t-1), we can calculate the next y_hat:
        y_hat = alfa * y + (1 - alfa) * y_hat
        y_hat = alfa * y + y_hat - alfa * y_hat
        y_hat = y_hat + alfa * (y - y_hat)

    Args:
        alfa (float): the smoothing coefficient
        logic_total (float):

    Returns:

    """
    pos = elapsed = None
    while not elapsed:
        pos, elapsed = yield
    y_hat = simple_eta(logic_total, pos, elapsed)
    lastPos, lastElapsed = pos, elapsed
    current_rate = pos / elapsed
    while True:
        temp, elapsed = yield y_hat
        if temp == pos:  # reduce numbers bouncing around.
            continue
        pos = temp
        diffPos, diffElapsed = pos - lastPos, elapsed - lastElapsed
        current_rate += alfa * (diffPos / diffElapsed - current_rate)
        y = simple_eta(logic_total, pos, temp / elapsed)
        y_hat += alfa * (y - y_hat)
        lastPos, lastElapsed = pos, elapsed


def gen_exponential_discounted_eta(alfa, logic_total):
    """
    none
    """
    pos = elapsed = None
    while not elapsed:
        pos, elapsed = yield
    y_hat = simple_eta(logic_total, pos, elapsed)
    lastPos, lastElapsed = pos, elapsed
    current_rate = pos / elapsed
    while True:
        temp, elapsed = yield y_hat, current_rate
        if temp == pos:  # reduce numbers bouncing around.
            continue
        pos = temp
        diffPos, diffElapsed = pos - lastPos, elapsed - lastElapsed
        current_rate += alfa * (diffPos / diffElapsed - current_rate)
        y = simple_eta(logic_total, pos, current_rate)
        y_hat += alfa * (y - y_hat)
        lastPos, lastElapsed = pos, elapsed
