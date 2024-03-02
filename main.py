import sys
from typing import Optional

import discord
from discord import ApplicationContext

from subscription import Subscription, SubscriptionManager
from websoc import get_status

bot = discord.Bot()


@bot.slash_command(name="subscribe")
async def subscribe_command(ctx: ApplicationContext, department: str, number: str):
    await ctx.response.defer()

    # requires defer
    result: Optional[str] = get_status(department, number)

    # Class does not exist
    if result is None:
        await ctx.followup.send(
            f"Failed to sign up for {department} {number}."
            f" Perhaps the class isn't offered this quarter?",
            ephemeral=True,
        )
        return

    # Success
    await ctx.followup.send(
        f"Subscribed to {department} {number}. Currently, the class is {result}."
        f" We will notify you when the status changes.",
        ephemeral=True,
    )

    # Register the subscription
    subscription = Subscription(ctx.user.id, department, number)
    SubscriptionManager.get_instance().subscribe(subscription)


@bot.slash_command(name="unsubscribe")
async def unsubscribe_command(ctx: ApplicationContext, department: str, number: str):
    subscription = Subscription(ctx.user.id, department, number)
    success = SubscriptionManager.get_instance().unsubscribe(subscription)
    if success:
        await ctx.respond(
            f"Unsubscribed to {department} {number}",
            ephemeral=True,
        )

    else:
        await ctx.respond(
            f"That subscription does not exist.",
            ephemeral=True,
        )


@bot.slash_command(name="list")
async def list_command(ctx: ApplicationContext):
    subscriptions = list(SubscriptionManager.get_instance().get_subscriptions_for_user(ctx.user.id))
    if len(subscriptions) == 0:
        await ctx.respond(
            f"You aren't subscribed to anything yet.",
            ephemeral=True,
        )
        return

    subscription_text = "\n".join(f"- {s.department} {s.number}" for s in subscriptions)
    print(subscription_text)
    await ctx.respond(
        f"You are subscribed to:\n{subscription_text}".strip(),
        ephemeral=True,
    )


@bot.event
async def on_ready():
    print("Ready")


bot.run(sys.argv[1])
