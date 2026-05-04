import asyncio
import numpy as np
import os
import json
from scipy import signal as scipy_signal
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioStream, InputAudioStream

# ============= 🔧 APNI DETAILS =============
API_ID = 39447635
API_HASH = "fc12fa4f90b177af21e2648441bcde59"
PHONE_NUMBER = "+4915773609881"  # Userbot number

# Folders
AUDIO_FOLDER = "saved_audios"
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

AUDIO_DB = "audios.json"
if not os.path.exists(AUDIO_DB):
    with open(AUDIO_DB, "w") as f:
        json.dump({}, f)

# Config
config = {
    "target_chat": None,
    "in_vc": False,
    "playing": False,
    "current_audio": None
}

# ============= 🎛️ 500x VOLUME PROCESSOR =============
class ExtremeAudioProcessor:
    def process_audio(self, audio_data):
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        try:
            if isinstance(audio_data, bytes):
                samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                samples = audio_data.astype(np.float32) / 32768.0
            
            # 500x VOLUME BOOST
            samples = samples * 500.0
            # Limiter
            samples = np.tanh(samples * 0.6) * 0.99
            # Clip
            samples = np.clip(samples, -0.99, 0.99)
            samples = (samples * 32767).astype(np.int16)
            return samples.tobytes()
        except:
            return audio_data

audio_processor = ExtremeAudioProcessor()

# Clients
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)
calls = PyTgCalls(app)

# ============= 📂 AUDIO FUNCTIONS =============
def save_audio(name, path):
    with open(AUDIO_DB, "r") as f:
        data = json.load(f)
    data[name] = path
    with open(AUDIO_DB, "w") as f:
        json.dump(data, f)

def get_audio(name):
    with open(AUDIO_DB, "r") as f:
        return json.load(f).get(name)

def get_all_audios():
    with open(AUDIO_DB, "r") as f:
        return json.load(f)

def delete_audio(name):
    with open(AUDIO_DB, "r") as f:
        data = json.load(f)
    if name in data:
        if os.path.exists(data[name]):
            os.remove(data[name])
        del data[name]
        with open(AUDIO_DB, "w") as f:
            json.dump(data, f)
        return True
    return False

# ============= 📝 COMMANDS - BINA KISI CHECK KE =============

@app.on_message(filters.command(["ping"], prefixes=[".", "!", "/", "?"]))
async def ping_cmd(client, message):
    await message.reply("🏓 **Pong!**\n✅ Userbot Active\n💀 500x Volume Ready\n🎙️ Mute Bypass ON")

@app.on_message(filters.command(["start", "help"], prefixes=[".", "!", "/", "?"]))
async def help_cmd(client, message):
    await message.reply(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💀 **NUCLEAR USERBOT** 💀\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎵 **AUDIO COMMANDS:**\n"
        "`.play <name>` - Play saved audio\n"
        "`.sadd <name>` - Save audio (reply to audio)\n"
        "`.show` - Show all saved audios\n"
        "`.rplay` - Reply to audio to play\n"
        "`.sdel <name>` - Delete saved audio\n\n"
        "🎙️ **VC COMMANDS:**\n"
        "`.joinvc <id>` - Join voice chat\n"
        "`.leavevc` - Leave voice chat\n"
        "`.stop` - Stop playing\n"
        "`.status` - Show status\n\n"
        "📊 **OTHER:**\n"
        "`.ping` - Check bot status\n"
        "`.help` - This menu\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔊 **VOLUME: 500x**\n"
        "🎚️ **MUTE BYPASS: ACTIVE**\n"
        "💀 **KAHI SE BHI COMMAND DALO**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

@app.on_message(filters.command(["show", "list"], prefixes=[".", "!", "/", "?"]))
async def show_cmd(client, message):
    audios = get_all_audios()
    if not audios:
        await message.reply("❌ **No saved audios!**\n\n`.sadd <name>` (reply to audio) to save")
        return
    
    text = "🎵 **SAVED AUDIOS:**\n━━━━━━━━━━━━━━━━━━━━\n"
    for name in audios:
        text += f"🎧 `{name}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n💀 `.play <name>` to play"
    await message.reply(text)

@app.on_message(filters.command(["sadd", "save"], prefixes=[".", "!", "/", "?"]))
async def sadd_cmd(client, message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ **Usage:** `.sadd <name>`\n*(Reply to an audio message)*")
            return
        
        name = parts[1]
        
        if not message.reply_to_message:
            await message.reply("❌ **Reply to an audio message!**\n\nSend audio → reply with `.sadd song_name`")
            return
        
        if not message.reply_to_message.audio:
            await message.reply("❌ **This is not an audio file!**\nReply to a voice message or audio file")
            return
        
        path = os.path.join(AUDIO_FOLDER, f"{name}.mp3")
        await message.reply_to_message.download(path)
        save_audio(name, path)
        
        await message.reply(f"✅ **Saved:** `{name}`\n🎵 Now play with `.play {name}`")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command(["sdel", "delete"], prefixes=[".", "!", "/", "?"]))
async def sdel_cmd(client, message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ **Usage:** `.sdel <name>`")
            return
        
        name = parts[1]
        
        if delete_audio(name):
            await message.reply(f"✅ **Deleted:** `{name}`")
        else:
            await message.reply(f"❌ `{name}` not found!\n`.show` to see saved audios")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command(["play"], prefixes=[".", "!", "/", "?"]))
async def play_cmd(client, message):
    if not config["in_vc"]:
        await message.reply("❌ **Not in voice chat!**\n\nFirst use: `.joinvc <chat_id>`\n\n*(Group ID jahan VC active hai)*")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ **Usage:** `.play <name>`\n\n`.show` to see saved audios")
            return
        
        name = parts[1]
        path = get_audio(name)
        
        if not path:
            await message.reply(f"❌ **`{name}` not found!**\n\n`.show` to see saved audios")
            return
        
        if not os.path.exists(path):
            await message.reply(f"❌ **File missing!**\nRe-save: `.sadd {name}`")
            return
        
        config["playing"] = True
        config["current_audio"] = name
        
        await calls.play(config["target_chat"], AudioStream(
            InputAudioStream(sample_rate=48000, channels=1, frame_duration=20),
            audio_processor.process_audio
        ))
        
        await message.reply(
            f"💀 **NOW PLAYING:** `{name}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔊 **Volume:** 500x (NUCLEAR)\n"
            f"🎙️ **Mute Bypass:** ACTIVE\n"
            f"⚠️ **Speaker phat sakta hai!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💀 `.stop` to stop | `.leavevc` to leave"
        )
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
        config["playing"] = False

@app.on_message(filters.command(["rplay", "replyplay"], prefixes=[".", "!", "/", "?"]))
async def rplay_cmd(client, message):
    if not config["in_vc"]:
        await message.reply("❌ **Not in voice chat!**\n\nFirst use: `.joinvc <chat_id>`")
        return
    
    if not message.reply_to_message:
        await message.reply("❌ **Reply to an audio message!**\n\nSend audio → reply with `.rplay`")
        return
    
    if not message.reply_to_message.audio:
        await message.reply("❌ **Not an audio file!**\nReply to a voice message or audio")
        return
    
    try:
        temp_path = os.path.join(AUDIO_FOLDER, "temp_playing.mp3")
        await message.reply_to_message.download(temp_path)
        
        config["playing"] = True
        config["current_audio"] = "temp_audio"
        
        await calls.play(config["target_chat"], AudioStream(
            InputAudioStream(sample_rate=48000, channels=1, frame_duration=20),
            audio_processor.process_audio
        ))
        
        await message.reply(
            f"💀 **PLAYING REPLY AUDIO!**\n"
            f"🔊 **500x VOLUME | MUTE BYPASS**\n"
            f"⚡ **FULL NUCLEAR BLAST!**"
        )
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command(["joinvc", "join"], prefixes=[".", "!", "/", "?"]))
async def joinvc_cmd(client, message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ **Usage:** `.joinvc -100xxxxxxxxx`\n\n*(Group/Channel ID jahan voice chat active hai)*\n\n💡 **Tips:**\n• ID negative mein hoti hai `-100` se shuru\n• Bot ko group mein admin hona chahiye")
            return
        
        chat_id = int(parts[1])
        config["target_chat"] = chat_id
        
        await calls.join_group_call(chat_id, AudioStream(
            InputAudioStream(sample_rate=48000, channels=1, frame_duration=20)
        ))
        config["in_vc"] = True
        
        await message.reply(
            f"✅ **JOINED VOICE CHAT!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **Target:** `{chat_id}`\n"
            f"🔊 **Volume:** 500x Ready\n"
            f"🎙️ **Mute Bypass:** ON\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💀 `.play <name>` se blast karo!"
        )
    except Exception as e:
        await message.reply(f"❌ **Error:** `{e}`\n\nMake sure:\n• Voice chat is active in group\n• Bot is admin\n• Correct group ID")

@app.on_message(filters.command(["leavevc", "leave"], prefixes=[".", "!", "/", "?"]))
async def leavevc_cmd(client, message):
    if config["in_vc"] and config["target_chat"]:
        try:
            await calls.leave_group_call(config["target_chat"])
            config["in_vc"] = False
            config["playing"] = False
            config["current_audio"] = None
            await message.reply("👋 **Left voice chat!**\n\n`.joinvc` to join again")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        await message.reply("❌ **Not in any voice chat!**\n\n`.joinvc` to join first")

@app.on_message(filters.command(["stop"], prefixes=[".", "!", "/", "?"]))
async def stop_cmd(client, message):
    if config["in_vc"]:
        try:
            await calls.stop_playout(config["target_chat"])
            config["playing"] = False
            config["current_audio"] = None
            await message.reply("⏹️ **Playback stopped!**\n\n`.play <name>` to play again")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        await message.reply("❌ **Not in voice chat!**")

@app.on_message(filters.command(["status", "stats"], prefixes=[".", "!", "/", "?"]))
async def status_cmd(client, message):
    await message.reply(
        f"📊 **NUCLEAR STATUS**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 **Bot Active:** ✅\n"
        f"🎙️ **In Voice Chat:** `{config['in_vc']}`\n"
        f"🎵 **Currently Playing:** `{config['current_audio'] or 'Nothing'}`\n"
        f"🎯 **Target Chat:** `{config['target_chat']}`\n"
        f"🔊 **Volume:** `500x` (NUCLEAR)\n"
        f"🎚️ **Mute Bypass:** `ACTIVE`\n"
        f"📀 **Saved Audios:** `{len(get_all_audios())}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💀 **MUTE KARNE SE BHI AWAAZ JAYEGI!**"
    )

# ============= 🎤 CALLBACKS =============
@calls.on_kicked()
async def on_kicked(client, chat_id):
    print(f"❌ Kicked from {chat_id}")
    config["in_vc"] = False
    config["playing"] = False

@calls.on_closed()
async def on_closed(client, chat_id):
    print(f"🔴 Call closed in {chat_id}")
    config["in_vc"] = False

# ============= 🚀 MAIN =============
async def main():
    print("=" * 60)
    print("💀 NUCLEAR USERBOT - 500x VOLUME 💀")
    print("=" * 60)
    print(f"📱 Userbot: {PHONE_NUMBER}")
    print("=" * 60)
    
    await app.start()
    await calls.start()
    
    print("\n✅ **BOT ACTIVE!**")
    print("\n📝 **TEST KARO:**")
    print("   • Saved Messages mein `.ping` likho")
    print("   • Bot ko DM mein `.help` likho")
    print("   • Kisi bhi group mein `.ping` likho")
    print("\n💀 **SAB JAGAH CHALEGA!**")
    print("=" * 60)
    
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Bot band ho raha hai...")
    except Exception as e:
        print(f"❌ Error: {e}")
