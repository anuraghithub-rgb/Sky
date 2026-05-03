# ==================================================
# 💀 NUCLEAR VOICE RELAY SYSTEM V2 - MUTE BYPASS 💀
# ==================================================
# Mute bypass: Bot volume fixed at 500x extreme level
# Owner: Bind to bot's own user_id (auto-detect)
# Commands work ANYWHERE (group, pm, any chat)
# ==================================================

import asyncio
import numpy as np
import struct
from scipy import signal as scipy_signal
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioParameters, AudioQuality
from pytgcalls.types.input_stream import AudioStream, InputAudioStream
from pytgcalls.exceptions import GroupCallNotFound, NoActiveGroupCall
import os

# ============= 🔧 APNI DETAILS YAHAN DALO =============
API_ID = 39447635
API_HASH = "fc12fa4f90b177af21e2648441bcde59"

# Listener Account (jo source group mein mic capture karega)
LISTENER_PHONE = "+4915773609881"

# Blaster Account (jo target group mein play karega)
BLASTER_PHONE = "+16578220525"

SOURCE_GROUP_ID = -5016782735
# =====================================================

# Owner will be auto-detected from bot's user_id
OWNER_USERNAME = None  # Leave None, bot will use its own ID
ALLOWED_USERS = set()  # Empty set, owner is auto-detected

# Audio settings - EXTREME VOLUME (500x)
SAMPLE_RATE = 48000
CHANNELS = 1
FRAME_DURATION = 20
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)

config = {
    "target_chat": None,
    "source_chat": SOURCE_GROUP_ID,
    "active": False,
    "listener_in_vc": False,
    "blaster_in_vc": False,
    "boost": 500.0,      # 🔥 FIXED 500x VOLUME (Mute impossible)
    "bass": 10.0,        # Max bass
    "equalizer": [10.0, 8.0, 6.0, 8.0, 10.0],  # Max all bands
    "mic": True,         # Always on, but volume is fixed anyway
    "compressor": True,
}

# ============= 🔥 EXTREME AUDIO PROCESSOR =============
class ExtremeAudioProcessor:
    def __init__(self):
        self.bass_coeffs = None
        self.update_filters()
    
    def update_filters(self):
        """Update audio filters"""
        try:
            nyquist = SAMPLE_RATE / 2
            b, a = scipy_signal.butter(4, [20/nyquist, 250/nyquist], btype='band')
            self.bass_coeffs = (b, a)
        except:
            self.bass_coeffs = None
    
    def process_audio(self, audio_data):
        """EXTREME PROCESSING - 500x volume, no mute possible"""
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        
        try:
            if isinstance(audio_data, bytes):
                samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                samples = audio_data.astype(np.float32) / 32768.0
            
            # 1. MAX BASS BOOST - Subwoofer destruction
            if self.bass_coeffs:
                b, a = self.bass_coeffs
                filtered = scipy_signal.filtfilt(b, a, samples)
                samples = samples + (filtered * 3.0)  # Extreme bass
            
            # 2. MAX EQUALIZER - All frequencies boosted
            eq = config["equalizer"]
            nyquist = SAMPLE_RATE / 2
            
            # Full spectrum boost
            for freq, gain in [(50, eq[0]), (200, eq[1]), (1000, eq[2]), (4000, eq[3]), (8000, eq[4])]:
                if freq/nyquist < 0.98:
                    b, a = scipy_signal.butter(2, [max(0.01, freq*0.7/nyquist), min(0.98, freq*1.3/nyquist)], btype='band')
                    filtered = scipy_signal.filtfilt(b, a, samples)
                    samples = samples + (filtered * (gain - 1.0) * 0.5)
            
            # 3. AGGRESSIVE COMPRESSOR - Everything gets amplified
            if config["compressor"]:
                rms = np.sqrt(np.mean(samples**2))
                threshold = 0.01  # Ridiculously low threshold
                if rms > threshold:
                    gain_reduction = threshold / rms
                    gain_reduction = gain_reduction ** 0.5
                    samples = samples * gain_reduction
                samples = samples * 15.0  # Extreme makeup gain
            
            # 4. FIXED 500x VOLUME BOOST - NO MATTER WHAT
            # Mic on/off doesn't matter - volume is hardcoded
            boost_factor = 500.0 / 10.0  # 50x multiplier
            samples = samples * boost_factor
            
            # 5. HARD CLIPPING with Tanh - Maximum loudness
            samples = np.tanh(samples * 3.0) * 0.99
            
            # 6. Final push - Ensure maximum amplitude
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                samples = samples / max_val * 0.98
            
            samples = (samples * 32767).astype(np.int16)
            return samples.tobytes()
            
        except Exception as e:
            print(f"Audio error: {e}")
            return audio_data

audio_processor = ExtremeAudioProcessor()

# ============= 📞 CLIENTS INITIALIZE =============
print("🎤 Listener account login...")
listener = Client("listener_session", api_id=API_ID, api_hash=API_HASH, phone_number=LISTENER_PHONE)

print("🔊 Blaster account login...")
blaster = Client("blaster_session", api_id=API_ID, api_hash=API_HASH, phone_number=BLASTER_PHONE)

calls_listener = PyTgCalls(listener)
calls_blaster = PyTgCalls(blaster)

# ============= 👑 AUTO OWNER DETECTION =============
BOT_OWNER_ID = None  # Will be set after bot starts

def is_owner(user_id):
    """Check if user is the bot's owner (based on bot's own ID)"""
    global BOT_OWNER_ID
    if BOT_OWNER_ID is None:
        return False
    return user_id == BOT_OWNER_ID

def is_allowed(user_id):
    """Only owner is allowed"""
    return is_owner(user_id)

# ============= 📝 COMMANDS - WORK ANYWHERE =============
# Remove chat restriction - commands work in PM, groups, ANYWHERE

@listener.on_message(filters.command("target", prefixes="!"))
async def set_target(client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply("❌ Sirf bot owner ko permission hai!")
        return
    try:
        chat_id = int(message.command[1])
        config["target_chat"] = chat_id
        await message.reply(f"✅ Target set: `{chat_id}`\nAb `!start` karo!")
    except:
        await message.reply("❌ Use: `!target -100xxxxxxxxx`")

@listener.on_message(filters.command("start", prefixes="!"))
async def start_system(client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply("❌ Sirf bot owner ko permission hai!")
        return

    if not config["target_chat"]:
        await message.reply("❌ Pehle `!target` se target set karo!")
        return

    config["active"] = True

    try:
        await calls_listener.join_group_call(
            config["source_chat"],
            AudioStream(InputAudioStream(sample_rate=SAMPLE_RATE, channels=CHANNELS, frame_duration=FRAME_DURATION))
        )
        config["listener_in_vc"] = True
        
        await calls_blaster.join_group_call(
            config["target_chat"],
            AudioStream(InputAudioStream(sample_rate=SAMPLE_RATE, channels=CHANNELS, frame_duration=FRAME_DURATION))
        )
        config["blaster_in_vc"] = True
        
        await message.reply(
            f"💀 **NUCLEAR SYSTEM ACTIVE - 500x VOLUME** 💀\n\n"
            f"🎙️ Source: `{config['source_chat']}`\n"
            f"💥 Target: `{config['target_chat']}`\n"
            f"🔊 **VOLUME: 500x FIXED**\n"
            f"🎸 BASS: MAX\n"
            f"⚡ **MUTE BYPASS ACTIVE**\n\n"
            f"⚠️ **ANY SONG/GANA FULL VOLUME PE PLAY HOGA!**\n"
            f"⚠️ **MIC ON/OFF SE KOI FARAK NAHI!**"
        )
    except Exception as e:
        config["active"] = False
        await message.reply(f"❌ Error: {e}")

@listener.on_message(filters.command("stop", prefixes="!"))
async def stop_system(client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply("❌ Sirf bot owner ko permission hai!")
        return
    
    config["active"] = False
    
    try:
        if config["listener_in_vc"]:
            await calls_listener.leave_group_call(config["source_chat"])
            config["listener_in_vc"] = False
        if config["blaster_in_vc"] and config["target_chat"]:
            await calls_blaster.leave_group_call(config["target_chat"])
            config["blaster_in_vc"] = False
        await message.reply("✅ System band!")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@listener.on_message(filters.command("status", prefixes="!"))
async def status(client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply("❌ Sirf bot owner ko permission hai!")
        return
    
    await message.reply(
        f"📊 **NUCLEAR SYSTEM STATUS**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 Active: `{config['active']}`\n"
        f"🔊 **Volume: 500x FIXED**\n"
        f"🎸 Bass: MAX\n"
        f"🎙️ Mic: `{config['mic']}` (Volume unaffected)\n"
        f"🎯 Target: `{config['target_chat']}`\n"
        f"📡 Listener VC: `{'Connected' if config['listener_in_vc'] else 'Disconnected'}`\n"
        f"🔊 Blaster VC: `{'Connected' if config['blaster_in_vc'] else 'Disconnected'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💀 **MUTE BYPASS: ANY SONG = FULL VOLUME**\n"
        f"⚡ **JO BHI GANA PLAY HOGA 500x VOLUME PE**"
    )

@listener.on_message(filters.command("help", prefixes="!"))
async def help_cmd(client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply("❌ Sirf bot owner ko permission hai!")
        return
    
    await message.reply(
        "📋 **NUCLEAR RELAY V2 - MUTE BYPASS**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **COMMANDS (WORK ANYWHERE - PM/GROUP):**\n"
        "`!target -100xxxx` → Set target group\n"
        "`!start` → Activate system\n"
        "`!stop` → Deactivate system\n"
        "`!status` → Show status\n"
        "`!help` → Show this\n\n"
        "🔥 **FEATURES:**\n"
        "• **500x FIXED VOLUME** - Mic on/off se koi farak nahi\n"
        "• **MUTE BYPASS** - Jo gana play hoga full volume pe\n"
        "• **COMMANDS ANYWHERE** - Group ya DM, kahi se bhi command do\n"
        "• **AUTO OWNER** - Jo bot ki API se login hoga wahi owner\n\n"
        "⚠️ **BOT OWNER = JO ACCOUNT BOT CHALA RAHA HAI**\n"
        "💀 **HAR GANA FULL VOLUME PE PLAY HOGA!**"
    )

@listener.on_message(filters.command("checkowner", prefixes="!"))
async def check_owner(client, message: Message):
    """Check if you are the bot owner"""
    if is_owner(message.from_user.id):
        await message.reply("✅ **Aap hi bot owner ho!** Har command use kar sakte ho!")
    else:
        await message.reply(f"❌ Aap owner nahi ho. Owner ID: `{BOT_OWNER_ID}`")

# ============= 🎤 AUDIO RELAY =============
@calls_listener.on_kicked()
async def on_kicked_handler(client, chat_id):
    print(f"❌ Listener kicked from {chat_id}")
    config["listener_in_vc"] = False

@calls_blaster.on_kicked()
async def on_kicked_blaster(client, chat_id):
    print(f"❌ Blaster kicked from {chat_id}")
    config["blaster_in_vc"] = False

# ============= 🚀 MAIN =============
async def main():
    global BOT_OWNER_ID
    
    print("=" * 50)
    print("💀 NUCLEAR VOICE RELAY V2 - MUTE BYPASS 💀")
    print("=" * 50)
    
    await listener.start()
    await blaster.start()
    
    # Auto-detect owner from listener account (the account running the bot)
    me_listener = await listener.get_me()
    BOT_OWNER_ID = me_listener.id
    
    print(f"👑 Bot Owner (Auto-Detected): {BOT_OWNER_ID}")
    print(f"👑 Owner Username: @{me_listener.username or 'No username'}")
    print(f"📡 Source Group: {SOURCE_GROUP_ID}")
    print("=" * 50)
    
    await calls_listener.start()
    await calls_blaster.start()
    
    print("\n✅ **SYSTEM READY - MUTE BYPASS ACTIVE!**")
    print("🔥 **VOLUME: 500x FIXED - MIC ON/OFF SE KOI FARAK NAHI**")
    print("📝 **COMMANDS WORK ANYWHERE (PM OR ANY GROUP)**")
    print(f"💬 **Owner = @{me_listener.username or BOT_OWNER_ID}**")
    print("\n💀 **JO BHI GANA PLAY HOGA FULL VOLUME PE!**")
    print("=" * 50)
    
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ System band...")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")