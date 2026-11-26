import os

import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ALLOWED_USER_IDS = {
    int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").split(",") if x.strip()
}

GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GH_REPO = os.environ.get("GITHUB_REPO", "")  # owner/repo
GH_WORKFLOW = os.environ.get("GITHUB_WORKFLOW", "build.yml")
GH_REF = os.environ.get("GITHUB_REF", "main")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def allowed(interaction: discord.Interaction) -> bool:
    return interaction.user.id in ALLOWED_USER_IDS


@tree.command(name="ping", description="فحص أن البوت يعمل")
async def ping(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    await interaction.response.send_message(f"🏓 البوت يعمل ({latency}ms)", ephemeral=True)


@tree.command(name="build", description="تشغيل workflow على GitHub (بناء/اختبار)")
async def build(interaction: discord.Interaction):
    if not allowed(interaction):
        return await interaction.response.send_message(
            "غير مصرح لك باستخدام هذا الأمر.", ephemeral=True
        )
    if not (GH_TOKEN and GH_REPO):
        return await interaction.response.send_message(
            "لم يتم ضبط GITHUB_TOKEN وGITHUB_REPO.", ephemeral=True
        )
    await interaction.response.defer(ephemeral=True)
    url = f"https://api.github.com/repos/{GH_REPO}/actions/workflows/{GH_WORKFLOW}/dispatches"
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json={"ref": GH_REF}) as resp:
            if resp.status == 204:
                msg = f"🚀 تم تشغيل `{GH_WORKFLOW}` على `{GH_REPO}`."
            else:
                msg = f"❌ GitHub رد بالحالة {resp.status}: {await resp.text()}"
    await interaction.followup.send(msg, ephemeral=True)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


client.run(DISCORD_TOKEN)