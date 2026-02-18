from sqlalchemy import BIGINT, INTEGER, String

from src.domain.user.vo import (
    Bio,
    FirstName,
    LanguageCode,
    LastName,
    ReferralCount,
    UserId,
    Username,
)

from .base import VOType


class UserIdType(VOType):
    impl = BIGINT
    vo_class = UserId
    vo_raw = int
    cache_ok = True


class FirstNameType(VOType):
    impl = String(64)
    vo_class = FirstName
    vo_raw = str
    cache_ok = True


class LastNameType(VOType):
    impl = String(64)
    vo_class = LastName
    vo_raw = str
    cache_ok = True


class UsernameType(VOType):
    impl = String(32)
    vo_class = Username
    vo_raw = str
    cache_ok = True


class BioType(VOType):
    impl = String(160)
    vo_class = Bio
    vo_raw = str
    cache_ok = True


class ReferralCountType(VOType):
    impl = INTEGER
    vo_class = ReferralCount
    vo_raw = int
    cache_ok = True


class LanguageCodeType(VOType):
    impl = String(5)
    vo_class = LanguageCode
    vo_raw = str
    cache_ok = True
