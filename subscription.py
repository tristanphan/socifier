import dataclasses
from typing import Dict, Iterable, Set

from course import Course
from datatypes import UserId


@dataclasses.dataclass(frozen=True)
class Subscription:
    user: UserId
    course: Course

    def copy_with(self, user=None, course=None):
        return Subscription(
            user or self.user,
            course or self.course,
        )


class SubscriptionManager:

    def __init__(self):
        # TODO load from disk lol

        # Maps users to their subscriptions
        # This schema is useful for per-user listing
        self._subscriptions: Dict[UserId, Set[Subscription]] = {}
        self._courses: Dict[Course, Set[Subscription]] = {}

    def subscribe(self, subscription: Subscription):
        """
        Subscribes the user to changes to a course status
        :param subscription: The user's subscription model
        :return:
        """

        # TODO save to disk lol
        self._subscriptions.setdefault(subscription.user, set()).add(subscription)
        self._courses.setdefault(subscription.course, set()).add(subscription)

    def unsubscribe(self, subscription: Subscription) -> bool:
        if subscription not in self._subscriptions.get(subscription.user, set()):
            return False

        # TODO save to disk lol
        self._subscriptions[subscription.user].remove(subscription)
        self._courses[subscription.course].remove(subscription)

        # Trim empty sets
        if len(self._subscriptions[subscription.user]) == 0:
            self._subscriptions.pop(subscription.user)
        if len(self._courses[subscription.course]) == 0:
            self._courses.pop(subscription.course)

        return True

    def get_subscriptions(self) -> Iterable[Subscription]:
        """
        :return: An iterable over all subscriptions
        """
        for subscriptions in list(self._subscriptions.values()):
            yield from set(subscriptions)

    def get_subscription_for_user(self, user: UserId) -> Iterable[Subscription]:
        """
        :param user: The user to get subscriptions for
        :return: An iterable over the user's subscriptions
        """
        yield from set(self._subscriptions.get(user, set()))

    def get_courses(self) -> Iterable[Course]:
        """
        :return: An iterable of unique courses that users are subscribed to
        """
        yield from set(subscription.course for subscription in self.get_subscriptions())

    def get_users_by_course(self, course: Course) -> Iterable[UserId]:
        """
        :param course: The course to search users by
        :return: An iterable over the users subscribed to the course
        """
        yield from {s.user for s in set(self._courses.get(course, set()))}

    _instance = None

    @classmethod
    def get_instance(cls) -> "SubscriptionManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
