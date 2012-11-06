# coding=utf-8
from flufl.enum import Enum

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

class Status(Enum):
    """Enum representing the status of a :class:`~engineer.models.Post`."""
    draft = 0 #: Post is a draft.
    published = 1 #: Post is published.
    review = 2 #: Post is in review.

    def __reduce__(self):
        return 'Status'
