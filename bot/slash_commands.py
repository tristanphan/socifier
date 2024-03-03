from typing import Optional, List, Dict

from discord import SlashCommand, ApplicationContext

import websoc
from course import Course, Status, CourseCache
from datatypes import SectionCode
from subscription import Subscription, SubscriptionManager


async def subscribe_command(ctx: ApplicationContext, section_code: SectionCode):
    await ctx.response.defer(ephemeral=True)

    # Defer for API request
    result: Optional[Dict[Course, Status]] = websoc.get_course_statuses([section_code])

    # Class does not exist
    if result is None or len(result) == 0:
        await ctx.followup.send(
            f"Failed to sign up for {section_code}."
            f" Perhaps the class isn't offered this quarter?",
            ephemeral=True,
        )
        return

    course, status = next(iter(result.items()))
    CourseCache.get_instance().update(course, status)

    # Success
    await ctx.followup.send(
        f"Subscribed to changes to {course}. Currently, the class is {status.name}."
        f" I will notify you when the enrollment status changes.",
        ephemeral=True,
    )

    # Register the subscription
    subscription = Subscription(ctx.user.id, course)
    SubscriptionManager.get_instance().subscribe(subscription)


async def unsubscribe_command(ctx: ApplicationContext, section_code: SectionCode):
    subscription = Subscription(ctx.user.id, Course(section_code))

    success = SubscriptionManager.get_instance().unsubscribe(subscription)
    if success:
        await ctx.respond(
            f"Unsubscribed from {section_code}.",
            ephemeral=True,
        )

    else:
        await ctx.respond(
            f"That subscription does not exist.",
            ephemeral=True,
        )


async def list_command(ctx: ApplicationContext):
    subscriptions = list(SubscriptionManager.get_instance().get_subscription_for_user(ctx.user.id))
    if len(subscriptions) == 0:
        await ctx.respond(
            f"You aren't subscribed to anything yet.",
            ephemeral=True,
        )
        return

    subscription_text = "\n".join(f"- {s.course.department} {s.course.number} ({s.course.code})" for s in subscriptions)
    await ctx.respond(
        f"You are subscribed to:\n{subscription_text}".strip(),
        ephemeral=True,
    )


commands: List[SlashCommand] = [
    SlashCommand(name="subscribe", func=subscribe_command),
    SlashCommand(name="unsubscribe", func=unsubscribe_command),
    SlashCommand(name="list", func=list_command),
]
