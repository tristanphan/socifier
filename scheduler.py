from discord.ext import tasks

from bot import DiscordBot
from course import CourseCache
from subscription import SubscriptionManager
from websoc import get_course_statuses

FREQUENCY = 300  # seconds


@tasks.loop(seconds=FREQUENCY)
async def update():
    """
    Runs periodically, updates the status of all classes and notifies subscribers of changes
    """

    subscriptions = SubscriptionManager.get_instance().get_subscriptions()
    section_codes = [s.course.code for s in subscriptions]
    statuses = get_course_statuses(section_codes)

    # Something went wrong
    if statuses is None:
        return

    for course, status in statuses.items():

        # Check if there was change in status
        previous_status = CourseCache.get_instance().lookup(course)
        if previous_status != status or True:  # TODO remove

            # Notify subscribers
            for user in SubscriptionManager.get_instance().get_users_by_subscription():
                await DiscordBot.get_instance().get_user(user).send(f"{course} is {status}")

            # Update cache
            CourseCache.get_instance().update(course, status)
