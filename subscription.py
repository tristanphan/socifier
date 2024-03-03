import dataclasses
from typing import Dict, Iterable, Set, Tuple

from datatypes import Department, UserId, Number, Class, Status


@dataclasses.dataclass(frozen=True)
class Subscription:
    user: UserId
    department: Department
    number: Number

    def get_class(self) -> Class:
        return self.department, self.number

    def copy_with(self, user=None, department=None, number=None):
        return Subscription(
            user or self.user,
            department or self.department,
            number or self.number,
        )


class SubscriptionManager:
    _instance = None

    def __init__(self):
        # TODO load from disk lol
        self._subscriptions: Dict[UserId, Set[Subscription]] = {}
        self._classes: Dict[Class, Set[Subscription]] = {}
        self._status_cache: Dict[Class, Status] = {}

    def subscribe(self, subscription: Subscription, status: Status):
        # TODO save to disk lol
        self._subscriptions.setdefault(subscription.user, set()).add(subscription)
        self._classes.setdefault(subscription.get_class(), set().add(subscription))
        self._status_cache[subscription.get_class()] = status

    def unsubscribe(self, subscription: Subscription) -> bool:
        if subscription not in self._subscriptions.get(subscription.user, set()):
            return False

        # TODO save to disk lol
        self._subscriptions[subscription.user].remove(subscription)
        self._classes[subscription.get_class()].remove(subscription)
        if len(self._subscriptions[subscription.user]) == 0:
            self._subscriptions.pop(subscription.user)
        if len(self._classes[subscription.get_class()]) == 0:
            self._classes.pop(subscription.get_class())
            self._status_cache.pop(subscription.get_class())

        return True

    def get_subscriptions(self) -> Iterable[Subscription]:
        for subscriptions in self._subscriptions.values():
            yield from subscriptions

    def get_subscription_for_user(self, user: UserId) -> Iterable[Subscription]:
        yield from self._subscriptions.get(user, set())

    def get_users_for_class(self, cls: Class) -> Iterable[UserId]:
        yield from self._classes.get(cls, set())

    def get_classes(self) -> Iterable[Tuple[Class, Status]]:
        for cls, status in self._classes.items():
            yield cls, status

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
