import os

import aiohttp
import discord
from azure.identity.aio import ClientSecretCredential
from azure.mgmt.compute.aio import ComputeManagementClient
from azure.mgmt.network.aio import NetworkManagementClient
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ALLOWED_USER_IDS = {int(x) for x in os.environ["ALLOWED_USER_IDS"].split(",") if x.strip()}

AZ_TENANT_ID = os.environ["AZURE_TENANT_ID"]
AZ_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
AZ_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
AZ_SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
AZ_RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
AZ_VM_NAME = os.environ["AZURE_VM_NAME"]
AZ_PUBLIC_IP_NAME = os.environ["AZURE_PUBLIC_IP_NAME"]

GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GH_REPO = os.environ.get("GITHUB_REPO", "")          # owner/repo
GH_WORKFLOW = os.environ.get("GITHUB_WORKFLOW", "build.yml")
GH_REF = os.environ.get("GITHUB_REF", "main")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def azure_clients():
    cred = ClientSecretCredential(AZ_TENANT_ID, AZ_CLIENT_ID, AZ_CLIENT_SECRET)
    return (
        cred,
        ComputeManagementClient(cred, AZ_SUBSCRIPTION_ID),
        NetworkManagementClient(cred, AZ_SUBSCRIPTION_ID),
    )


async def close_all(*items):
    for item in items:
        await item.close()


def allowed(interaction: discord.Interaction) -> bool:
    return interaction.user.id in ALLOWED_USER_IDS


async def deny(interaction: discord.Interaction):
    await interaction.response.send_message("غير مصرح لك باستخدام هذا الأمر.", ephemeral=True)


async def get_power_state(compute) -> str:
    view = await compute.virtual_machines.instance_view(AZ_RESOURCE_GROUP, AZ_VM_NAME)
    for status in view.statuses or []:
        if status.code and status.code.startswith("PowerState/"):
            return status.code.split("/", 1)[1]
    return "unknown"


async def get_public_ip(network) -> str:
    ip = await network.public_ip_addresses.get(AZ_RESOURCE_GROUP, AZ_PUBLIC_IP_NAME)
    return ip.ip_address or "غير متاح (الجهاز متوقف)"


@tree.command(name="start", description="تشغيل جهاز Windows")
async def start(interaction: discord.Interaction):
    if not allowed(interaction):
        return await deny(interaction)
    await interaction.response.defer(ephemeral=True)
    cred, compute, network = azure_clients()
    try:
        poller = await compute.virtual_machines.begin_start(AZ_RESOURCE_GROUP, AZ_VM_NAME)
        await poller.result()
        ip = await get_public_ip(network)
        await interaction.followup.send(
            f"✅ الجهاز يعمل.\nالعنوان: `{ip}`\nافتح تطبيق Windows App وأضف هذا العنوان.",
            ephemeral=True,
        )
    except Exception as exc:
        await interaction.followup.send(f"❌ فشل التشغيل: {exc}", ephemeral=True)
    finally:
        await close_all(compute, network, cred)


@tree.command(name="stop", description="إيقاف الجهاز (Deallocate) لتوقف الفوترة")
async def stop(interaction: discord.Interaction):
    if not allowed(interaction):
        return await deny(interaction)
    await interaction.response.defer(ephemeral=True)
    cred, compute, network = azure_clients()
    try:
        poller = await compute.virtual_machines.begin_deallocate(AZ_RESOURCE_GROUP, AZ_VM_NAME)
        await poller.result()
        await interaction.followup.send("🛑 تم إيقاف الجهاز وتحرير الموارد.", ephemeral=True)
    except Exception as exc:
        await interaction.followup.send(f"❌ فشل الإيقاف: {exc}", ephemeral=True)
    finally:
        await close_all(compute, network, cred)


@tree.command(name="status", description="حالة الجهاز")
async def status(interaction: discord.Interaction):
    if not allowed(interaction):
        return await deny(interaction)
    await interaction.response.defer(ephemeral=True)
    cred, compute, network = azure_clients()
    try:
        state = await get_power_state(compute)
        await interaction.followup.send(f"الحالة: `{state}`", ephemeral=True)
    except Exception as exc:
        await interaction.followup.send(f"❌ خطأ: {exc}", ephemeral=True)
    finally:
        await close_all(compute, network, cred)


@tree.command(name="ip", description="عنوان الاتصال الحالي")
async def ip_cmd(interaction: discord.Interaction):
    if not allowed(interaction):
        return await deny(interaction)
    await interaction.response.defer(ephemeral=True)
    cred, compute, network = azure_clients()
    try:
        ip = await get_public_ip(network)
        await interaction.followup.send(f"العنوان: `{ip}`", ephemeral=True)
    except Exception as exc:
        await interaction.followup.send(f"❌ خطأ: {exc}", ephemeral=True)
    finally:
        await close_all(compute, network, cred)


@tree.command(name="build", description="تشغيل workflow على GitHub (بناء/اختبار)")
async def build(interaction: discord.Interaction):
    if not allowed(interaction):
        return await deny(interaction)
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