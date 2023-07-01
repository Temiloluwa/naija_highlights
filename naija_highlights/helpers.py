import pytz
import re
import string
from datetime import datetime

def clean_words(words):
    """ clean word"""
    punctuation = "".join([i for i in\
                string.punctuation if i not in [".", "?", "-", "!"]])
    words = re.sub(r"&(amp)", "and", words)
    words = re.sub(r"[\xa0\n{}]".format(punctuation),"", words).strip(" ")
    return words


def clean_html(words: str) -> str:
    """ removes html """
    return re.sub(r"<.*?>", "", words)


def localize_time(dt: datetime) -> datetime:
    """ localize time to Lagos """
    if dt.tzinfo:
        return dt.replace(tzinfo=pytz.timezone('Africa/Lagos'))
    return pytz.timezone('Africa/Lagos').localize(dt)


def get_this_week() -> int:
    """ Return today's iso calendar week """
    _, this_week, _ = localize_time(datetime.today()).isocalendar()
    return this_week
