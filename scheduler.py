import logging
from typing import Optional

from discord import Interaction, Embed, ButtonStyle, User
from discord.ext import tasks
from discord.ui import View, Item, Button

from course import CourseCache, Course, Status
from logger import obfuscate, logger
from subscription import SubscriptionManager, Subscription
from websoc import get_course_statuses

FREQUENCY = 300  # seconds
WEBREG_URL = "https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh"


@tasks.loop(seconds=FREQUENCY)
async def update():
    """
    Runs periodically, updates the status of all courses and notifies subscribers of changes
    """

    from bot import DiscordBot

    subscriptions = SubscriptionManager.get_instance().get_subscriptions()
    section_codes = sorted({s.course.code for s in subscriptions})
    if len(section_codes) == 0:
        logger.info("[Update] No subscriptions to fetch, no action to be done")
        return

    logger.info(f"[Update] Starting to {len(section_codes)} subscriptions, section codes: {section_codes}")
    statuses = get_course_statuses(section_codes)

    # Something went wrong
    if statuses is None:
        logging.error("[Update] Failed to get statuses")
        return

    for course, status in statuses.items():

        # Check if there was change in status
        previous_status: Optional[Status] = CourseCache.get_instance().lookup(course)
        if previous_status != status:

            logger.info(f"[Update] {course} moved from {previous_status} to {status}")

            # Notify subscribers
            for user_id in SubscriptionManager.get_instance().get_users_by_course(course):
                # Get all subscribed users
                user: User = await DiscordBot.get_instance().fetch_user(user_id)

                logger.info(f"[Update] Notifying user {obfuscate(user.name)} about {course}")

                embed = Embed(
                    title=f"{course} is now {status}!",
                    description=f"This class was previously {str(previous_status).lower()}.\n"
                                f"You're still subscribed to changes to this course.",
                    color=status.color()
                )

                await user.send(view=NotificationView(course), embed=embed)

            # Update cache
            CourseCache.get_instance().update(course, status)


class NotificationView(View):
    """
    Shows the unsubscribe button and a link to WebReg
    """

    def __init__(self, course: Course, *items: Item):
        super().__init__(*items)
        self.course = course

        # Unsubscribe button
        unsubscribe_button = Button(label="Unsubscribe", style=ButtonStyle.primary)
        unsubscribe_button.callback = self.unsubscribe_callback
        self.add_item(unsubscribe_button)

        # WebReg button
        webreg_button = Button(label="WebReg", url=WEBREG_URL)
        self.add_item(webreg_button)

    async def unsubscribe_callback(self, interaction: Interaction):
        session_id = obfuscate(None)

        logger.info(
            f"[Unsubscribe {session_id}-btn] User {obfuscate(interaction.user.name)} requested to "
            f"unsubscribe from {self.course}")
        subscription = Subscription(interaction.user.id, Course(self.course.code))

        success = SubscriptionManager.get_instance().unsubscribe(subscription)
        if success:
            logger.info(
                f"[Unsubscribe {session_id}-btn] Successfully unsubscribed from {self.course}")
            await interaction.response.send_message(f"Unsubscribed from {self.course}.", ephemeral=True)
        else:
            logger.info(f"[Unsubscribe {session_id}-btn] User is already NOT subscribed to {self.course}")
            await interaction.response.send_message(f"You aren't subscribed to {self.course}.", ephemeral=True)
