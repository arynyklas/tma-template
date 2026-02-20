from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class CheckAliveCBFilter(StrEnum):
    ALL = "all"
    DAYS_30 = "30"
    DAYS_7 = "7"
    DAYS_1 = "1"


class CheckAliveCBData(CallbackData, prefix="check_alive"):
    filter_: CheckAliveCBFilter


class StatsCBAction(StrEnum):
    TOP_REFERRERS = "top_referrers"
    CHECK_ALIVE = "check_alive"


class StatsCBData(CallbackData, prefix="stats"):
    action: StatsCBAction
