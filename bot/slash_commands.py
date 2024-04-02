from typing import Optional, List, Dict

from discord import SlashCommand, ApplicationContext

import websoc
from course import Course, Status, CourseCache
from datatypes import SectionCode
from logger import obfuscate, logger
from subscription import Subscription, SubscriptionManager


async def subscribe_command(ctx: ApplicationContext, section_code: SectionCode):
    session_id = obfuscate(None)

    await ctx.response.defer(ephemeral=True)
    logger.info(f"[Subscribe {session_id}] User {obfuscate(ctx.user.name)} requested to subscribe to {section_code}")

    # Defer for API request
    result: Optional[Dict[Course, Status]] = websoc.get_course_statuses([section_code])

    # Class does not exist
    if result is None or len(result) == 0:
        logger.info(f"[Subscribe {session_id}] Could not find {section_code}")
        await ctx.followup.send(
            f"Failed to sign up for {section_code}."
            f" Perhaps the class isn't offered this quarter?",
            ephemeral=True,
        )
        return

    course, status = next(iter(result.items()))
    CourseCache.get_instance().update(course, status)
    logger.info(f"[Subscribe {session_id}] Retrieved {course} with status {status}")

    # Success
    await ctx.followup.send(
        f"Subscribed to changes to {course}. Currently, the class is {status.name}."
        f" I will notify you when the enrollment status changes.",
        ephemeral=True,
    )

    # Register the subscription
    subscription = Subscription(ctx.user.id, course)
    SubscriptionManager.get_instance().subscribe(subscription)
    logger.info(f"[Subscribe {session_id}] Subscribed to {section_code}")


async def unsubscribe_command(ctx: ApplicationContext, section_code: SectionCode):
    session_id = obfuscate(None)

    logger.info(f"[Unsubscribe {session_id}] User {obfuscate(ctx.user.name)} requested to "
                f"unsubscribe from {section_code}")

    subscription = Subscription(ctx.user.id, Course(section_code))
    success = SubscriptionManager.get_instance().unsubscribe(subscription)
    if success:
        logger.info(f"[Unsubscribe {session_id}] Successfully unsubscribed from {section_code}")
        await ctx.respond(
            f"Unsubscribed from {section_code}.",
            ephemeral=True,
        )

    else:
        logger.warning(f"[Unsubscribe {session_id}] User is NOT subscribed to {section_code}")
        await ctx.respond(
            f"You aren't subscribed to {section_code}.",
            ephemeral=True,
        )


async def list_command(ctx: ApplicationContext):
    session_id = obfuscate(None)

    subscriptions = list(SubscriptionManager.get_instance().get_subscription_for_user(ctx.user.id))
    logger.info(f"[List {session_id}] User {obfuscate(ctx.user.name)} requested their subscriptions")
    if len(subscriptions) == 0:
        logger.info(f"[List {session_id}] User has no subscriptions")
        await ctx.respond(
            f"You aren't subscribed to anything yet.",
            ephemeral=True,
        )
        return

    logger.info(f"[List {session_id}] User has {len(subscriptions)} subscriptions: {subscriptions}")

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
