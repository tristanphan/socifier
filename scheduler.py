from discord import Interaction, Embed, ButtonStyle
from discord.ext import tasks
from discord.ui import View, Item, Button

from course import CourseCache, Course
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

    print("Updating...")

    subscriptions = SubscriptionManager.get_instance().get_subscriptions()
    section_codes = [s.course.code for s in subscriptions]
    statuses = get_course_statuses(section_codes)

    # Something went wrong
    if statuses is None:
        return

    for course, status in statuses.items():

        # Check if there was change in status
        previous_status = CourseCache.get_instance().lookup(course)
        if previous_status != status:

            # Notify subscribers
            for user_id in SubscriptionManager.get_instance().get_users_by_course(course):
                user = await DiscordBot.get_instance().fetch_user(user_id)

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
        subscription = Subscription(interaction.user.id, Course(self.course.code))

        success = SubscriptionManager.get_instance().unsubscribe(subscription)
        if success:
            await interaction.response.send_message(f"Unsubscribed from {self.course}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You are already unsubscribed.", ephemeral=True)
