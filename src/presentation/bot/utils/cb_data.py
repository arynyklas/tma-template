from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class SettingsCBAction(StrEnum):
    MENU = "menu"
    LANGUAGE = "language"
    BACK = "back"


class SettingsCBData(CallbackData, prefix="settings"):
    action: SettingsCBAction


class LanguageCBCode(StrEnum):
    EN = "en"
    RU = "ru"


class LanguageCBData(CallbackData, prefix="lang"):
    code: LanguageCBCode


class OnboardingCBData(CallbackData, prefix="onboard"):
    code: LanguageCBCode
