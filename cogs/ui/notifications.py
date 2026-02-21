import discord
from discord import ui
from datetime import datetime, time
from typing import Optional

from database.base import async_session_factory
from database.repository import GoalRepository
from utils.i18n import get_text


def get_readable_days(locale: discord.Locale | None, days: list[int]) -> str:
    """Converts a list of integers [0, 2] to a string based on locale."""
    days_map = get_text(locale, "notify.days_map")
    return ", ".join([days_map[d][1] for d in sorted(days)])


async def get_reminder_setup_data(
    user_id: int, guild_id: int, goal_name: str, locale: discord.Locale | None, guild_name: str | None = None
) -> tuple[str, ui.View]:
    """Gets data from the database and returns a tuple: (message content, UI view)."""
    async with async_session_factory() as session:
        repo = GoalRepository(session)
        goal = await repo.get_goal_by_name(guild_id, goal_name)

        if not goal:
            suffix = f" on server **{guild_name}**" if guild_name else ""
            return f"Goal **{goal_name}** does not exist{suffix}.", discord.utils.MISSING

        reminder = await repo.get_reminder(goal.id, user_id)
        initial_days = reminder.days_of_week if reminder else []
        initial_time = reminder.time if reminder else None

    view = ReminderView(guild_id, goal_name, locale, initial_days, initial_time)

    msg_content = f"Please configure reminders for **{goal_name}**"
    msg_content += f" (Server: **{guild_name}**):" if guild_name else ":"

    return msg_content, view


# --- MODAL ---
class TimeModal(ui.Modal, title="Set Reminder Time"):
    time_input = ui.TextInput(label="Time (HH:MM)", placeholder="e.g. 08:00 or 21:37", min_length=5, max_length=5)

    def __init__(self, guild_id: int, goal_name: str, selected_days: list[int], default_time: Optional[time] = None):
        super().__init__()
        self.guild_id = guild_id
        self.goal_name = goal_name
        self.selected_days = selected_days
        if default_time:
            self.time_input.default = default_time.strftime("%H:%M")

    async def on_submit(self, interaction: discord.Interaction):
        time_str = self.time_input.value.strip().replace(".", ":")

        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            await interaction.response.send_message(
                "Invalid time format. Please use HH:MM (e.g. 14:30).", ephemeral=True
            )
            return

        await interaction.response.defer()

        async with async_session_factory() as session:
            async with session.begin():
                repo = GoalRepository(session)
                goal = await repo.get_goal_by_name(self.guild_id, self.goal_name)
                if not goal:
                    await interaction.edit_original_response(
                        content=f"Goal **{self.goal_name}** does not exist.", view=None
                    )
                    return

                await repo.set_reminder(
                    goal_id=goal.id, user_id=interaction.user.id, days=self.selected_days, reminder_time=parsed_time
                )

        readable_days = get_readable_days(interaction.locale, self.selected_days)
        await interaction.edit_original_response(
            content=f"Reminder set for **{self.goal_name}**!\n📅 Days: **{readable_days}**\n🕒 Time: **{time_str}**",
            view=None,
        )


# --- SELECT ---
class DaysSelect(ui.Select):
    def __init__(self, locale: discord.Locale | None, initial_days: list[int]):
        self.default_values = [str(day) for day in initial_days]
        days_map = get_text(locale, "notify.days_map")

        if initial_days:
            current_days_str = get_readable_days(locale, initial_days)
            placeholder_text = get_text(locale, "notify.days_select.placeholder_current", days=current_days_str)
        else:
            placeholder_text = get_text(locale, "notify.days_select.placeholder_empty")

        options = []
        for idx, day_info in enumerate(days_map):
            full_name = day_info[0]
            options.append(discord.SelectOption(label=full_name, value=str(idx)))

        super().__init__(placeholder=placeholder_text, min_values=1, max_values=7, options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


# --- BUTTONS ---
class ConfirmButton(ui.Button):
    def __init__(self, guild_id: int, goal_name: str, select_component: DaysSelect, initial_time: Optional[time]):
        super().__init__(label="Next: Set Time", style=discord.ButtonStyle.primary, emoji="🕒", row=1)
        self.guild_id = guild_id
        self.goal_name = goal_name
        self.select_component = select_component
        self.initial_time = initial_time

    async def callback(self, interaction: discord.Interaction):
        current_values = self.select_component.values
        if not current_values:
            current_values = self.select_component.default_values

        if not current_values:
            await interaction.response.send_message("Please select at least one day.", ephemeral=True)
            return

        selected_days = [int(val) for val in current_values]
        modal = TimeModal(self.guild_id, self.goal_name, selected_days, default_time=self.initial_time)
        await interaction.response.send_modal(modal)


class DeleteButton(ui.Button):
    def __init__(self, guild_id: int, goal_name: str, has_reminder: bool):
        super().__init__(
            label="Turn off Reminders", style=discord.ButtonStyle.danger, emoji="🔕", row=1, disabled=not has_reminder
        )
        self.guild_id = guild_id
        self.goal_name = goal_name

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with async_session_factory() as session:
            async with session.begin():
                repo = GoalRepository(session)
                goal = await repo.get_goal_by_name(self.guild_id, self.goal_name)

                if goal:
                    deleted = await repo.delete_reminder(goal.id, interaction.user.id)
                    if deleted:
                        await interaction.edit_original_response(
                            content=f"Reminders for **{self.goal_name}** have been turned off.", view=None
                        )
                    else:
                        await interaction.edit_original_response(
                            content=f"You didn't have any reminders set for **{self.goal_name}**.", view=None
                        )
                else:
                    await interaction.edit_original_response(content="Goal not found.", view=None)


# --- VIEW ---
class ReminderView(ui.View):
    def __init__(
        self,
        guild_id: int,
        goal_name: str,
        locale: discord.Locale | None,
        initial_days: list[int] = [],
        initial_time: Optional[time] = None,
    ):
        super().__init__()
        has_reminder = len(initial_days) > 0

        self.select = DaysSelect(locale, initial_days)
        self.button = ConfirmButton(guild_id, goal_name, self.select, initial_time)
        self.delete_btn = DeleteButton(guild_id, goal_name, has_reminder)

        self.add_item(self.select)
        self.add_item(self.button)
        self.add_item(self.delete_btn)


# --- GUILD SELECT (For DM) ---
class GuildSelect(ui.Select):
    def __init__(self, valid_guilds: list[tuple[int, str]], goal_name: str):
        self.goal_name = goal_name

        DISCORD_SELECT_OPTIONS_MAX = 25
        options = [
            discord.SelectOption(label=g_name, value=str(g_id))
            for g_id, g_name in valid_guilds[:DISCORD_SELECT_OPTIONS_MAX]
        ]
        super().__init__(placeholder="Select a server...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = int(self.values[0])
        guild_name = next((opt.label for opt in self.options if opt.value == str(guild_id)), None)

        msg_content, view = await get_reminder_setup_data(
            interaction.user.id, guild_id, self.goal_name, interaction.locale, guild_name
        )
        await interaction.edit_original_response(content=msg_content, view=view)


class GuildSelectView(ui.View):
    def __init__(self, valid_guilds: list[tuple[int, str]], goal_name: str):
        super().__init__()
        self.add_item(GuildSelect(valid_guilds, goal_name))
