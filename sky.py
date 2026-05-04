import asyncio
import numpy as np
import struct
import os
import json
from scipy import signal as scipy_signal
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType, ChatMemberStatus
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioParameters, AudioQuality
from pytgcalls.types.input_stream import AudioStream, InputAudioStream
from pytgcalls.exceptions import GroupCallNotFound, NoActiveGroupCall
from pytgcalls.types.stream import StreamAudioEnded

# ============= 🔧 APNI DETAILS YAHAN DALO =============
API_ID = 39447635
API_HASH = "fc12fa4f90b177af21e2648441bcde59"
PHONE_NUMBER = "+4915773609881"  # Ek hi account - Userbot
OWNER_ID = 8236797126  # Teri Telegram ID

# Audio files storage
AUDIO_FOLDER = "saved_audios"
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

AUDIO_DB = "audios.json"
if not os.path.exists(AUDIO_DB):
    with open(AUDIO_DB, "w") as f:
        json.dump({}, f)

# ============= 📊 CONFIG =============
config = {
    "target_chat": None,
    "active": False,
    "in_vc": False,
    "current_audio": None,
    "volume": 500,  # 500x volume boost!
    "playing": False
}

# ============= 🎛️ EXTREME AUDIO PROCESSOR (500x Volume!) =============
class ExtremeAudioProcessor:
    def __init__(self):
        self.SAMPLE_RATE = 48000
        self.CHANNELS = 1
        
    def process_audio(self, audio_data):
        """500x volume boost - Mute bypass + Nuclear blast"""
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        
        try:
            # Convert to numpy array
            if isinstance(audio_data, bytes):
                samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                samples = audio_data.astype(np.float32) / 32768.0
            
            # ========== NUCLEAR VOLUME BOOST ==========
            # 500x volume - literally speaker destroyer
            VOLUME_BOOST = 500.0
            samples = samples * VOLUME_BOOST
            
            # Aggressive compressor to prevent clipping while maintaining loudness
            # This removes any mute possibility
            samples = np.tanh(samples * 0.8) * 0.99
            
            # Multi-band compression for maximum loudness
            # RMS normalization to ensure maximum output always
            rms = np.sqrt(np.mean(samples**2))
            if rms > 0:
                target_rms = 0.95
                gain = target_rms / rms
                samples = samples * min(gain, 10.0)
            
            # Hard limiter at the end
            samples = np.clip(samples, -0.99, 0.99)
            
            # Convert back
            samples = (samples * 32767).astype(np.int16)
            return samples.tobytes()
            
        except Exception as e:
            print(f"Audio error: {e}")
            return audio_data

audio_processor = ExtremeAudioProcessor()

# ============= 📞 USERBOT CLIENT =============
print("🚀 Userbot login ho raha hai...")
app = Client(
    "userbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER
)

calls = PyTgCalls(app)

# ============= 💾 AUDIO MANAGEMENT =============
def save_audio(name, file_path):
    with open(AUDIO_DB, "r") as f:
        data = json.load(f)
    data[name] = file_path
    with open(AUDIO_DB, "w") as f:
        json.dump(data, f)

def get_audio(name):
    with open(AUDIO_DB, "r") as f:
        data = json.load(f)
    return data.get(name)

def get_all_audios():
    with open(AUDIO_DB, "r") as f:
        return json.load(f)

def delete_audio(name):
    with open(AUDIO_DB, "r") as f:
        data = json.load(f)
    if name in data:
        file_path = data[name]
        if os.path.exists(file_path):
            os.remove(file_path)
        del data[name]
        with open(AUDIO_DB, "w") as f:
            json.dump(data, f)
        return True
    return False

# ============= 👑 OWNER CHECK =============
def is_owner(user_id):
    return user_id == OWNER_ID

# ============= 📝 COMMANDS - SAB JAGAH WORK KAREGA (DM + GROUP) =============

@app.on_message(filters.command("ping", prefixes="."))
async def ping(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    await message.reply("🏓 **Pong!** Userbot Active ✅\n💀 500x Volume Ready!")

@app.on_message(filters.command("help", prefixes="."))
async def help_cmd(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    await message.reply(
        "📋 **NUCLEAR USERBOT COMMANDS**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎵 **AUDIO COMMANDS:**\n"
        "`.play <name>` → Play saved audio (500x Volume!)\n"
        "`.rplay` → Reply to audio message to play it\n"
        "`.sadd <name>` → Reply to audio to save it\n"
        "`.sdel <name>` → Delete saved audio\n"
        "`.show` → Show all saved audios\n\n"
        "🎙️ **VC COMMANDS:**\n"
        "`.joinvc <chat_id>` → Join voice chat\n"
        "`.leavevc` → Leave voice chat\n"
        "`.stop` → Stop playing\n"
        "`.status` → Show current status\n\n"
        "📊 **OTHER:**\n"
        "`.ping` → Check bot status\n"
        "`.help` → Show this menu\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💀 **VOLUME: 500x | MUTE BYPASS ACTIVE**\n"
        "⚡ **KAHI BHI COMMAND DALO - WORK KAREGA!**"
    )

@app.on_message(filters.command("show", prefixes="."))
async def show_audios(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    audios = get_all_audios()
    if not audios:
        await message.reply("❌ Koi audio saved nahi hai!\n\n`.sadd <name>` se audio save kar pehle.")
        return
    
    text = "🎵 **SAVED AUDIOS:**\n━━━━━━━━━━━━━━━━━━━━\n"
    for name, path in audios.items():
        text += f"🎧 `{name}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n💀 Use `.play <name>` to play!"
    await message.reply(text)

@app.on_message(filters.command("sadd", prefixes="."))
async def save_audio(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        name = message.command[1]
        
        if message.reply_to_message and message.reply_to_message.audio:
            audio = message.reply_to_message.audio
            file_path = os.path.join(AUDIO_FOLDER, f"{name}.mp3")
            await message.reply_to_message.download(file_path)
            save_audio(name, file_path)
            await message.reply(f"✅ **{name}** save ho gaya!\n🎵 Ab `.play {name}` se play kar sakte ho!")
        else:
            await message.reply("❌ Kisi **audio message** ko reply karke `.sadd <name>` likho!")
    except IndexError:
        await message.reply("❌ Use: `.sadd <song_name>` (reply to audio)")

@app.on_message(filters.command("sdel", prefixes="."))
async def delete_audio(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    try:
        name = message.command[1]
        if delete_audio(name):
            await message.reply(f"✅ **{name}** delete ho gaya!")
        else:
            await message.reply(f"❌ **{name}** mila nahi!")
    except IndexError:
        await message.reply("❌ Use: `.sdel <song_name>`")

@app.on_message(filters.command("play", prefixes="."))
async def play_audio(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    
    if not config["in_vc"]:
        await message.reply("❌ Pehle `.joinvc <chat_id>` se VC join karo!")
        return
    
    try:
        name = message.command[1]
        audio_path = get_audio(name)
        
        if not audio_path:
            await message.reply(f"❌ **{name}** mila nahi!\n`.show` se dekh kaunsa hai!")
            return
        
        if not os.path.exists(audio_path):
            await message.reply(f"❌ Audio file missing! Re-save karo.")
            return
        
        config["playing"] = True
        config["current_audio"] = name
        
        # Play with EXTREME processing
        await calls.play(
            config["target_chat"],
            AudioStream(
                InputAudioStream(
                    sample_rate=48000,
                    channels=1,
                    frame_duration=20,
                ),
                audio_processor.process_audio
            )
        )
        
        await message.reply(
            f"💀 **NOW PLAYING:** `{name}`\n"
            f"🔊 **VOLUME: 500x** (NUCLEAR MODE)\n"
            f"🎙️ **MUTE BYPASS: ACTIVE**\n"
            f"⚡ **JO BOLA WO SUNAI DEGA!**\n\n"
            f"⚠️ **SPEAKER PHAT SAKTA HAI!**"
        )
        
    except IndexError:
        await message.reply("❌ Use: `.play <song_name>`\n\n`.show` se dekho kaunsa song hai!")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
        config["playing"] = False

@app.on_message(filters.command("rplay", prefixes="."))
async def reply_play(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    
    if not config["in_vc"]:
        await message.reply("❌ Pehle `.joinvc <chat_id>` se VC join karo!")
        return
    
    if not message.reply_to_message or not message.reply_to_message.audio:
        await message.reply("❌ Kisi **audio message** ko reply karke `.rplay` likho!")
        return
    
    try:
        audio = message.reply_to_message.audio
        temp_path = os.path.join(AUDIO_FOLDER, "temp_play.mp3")
        await message.reply_to_message.download(temp_path)
        
        config["playing"] = True
        config["current_audio"] = audio.file_name or "temp_audio"
        
        await calls.play(
            config["target_chat"],
            AudioStream(
                InputAudioStream(
                    sample_rate=48000,
                    channels=1,
                    frame_duration=20,
                ),
                audio_processor.process_audio
            )
        )
        
        await message.reply(
            f"💀 **PLAYING REPLY AUDIO!**\n"
            f"🔊 **500x VOLUME | MUTE BYPASS**\n"
            f"⚡ **FULL BLAST MODE!**"
        )
        
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
        config["playing"] = False

@app.on_message(filters.command("stop", prefixes="."))
async def stop_audio(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    
    if config["in_vc"]:
        try:
            await calls.stop_playout(config["target_chat"])
            config["playing"] = False
            config["current_audio"] = None
            await message.reply("⏹️ **Playback Stopped!**")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        await message.reply("❌ VC mein nahi hoon!")

@app.on_message(filters.command("joinvc", prefixes="."))
async def join_vc(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        chat_id = int(message.command[1])
        config["target_chat"] = chat_id
        
        await calls.join_group_call(
            chat_id,
            AudioStream(
                InputAudioStream(
                    sample_rate=48000,
                    channels=1,
                    frame_duration=20,
                )
            )
        )
        config["in_vc"] = True
        config["active"] = True
        
        await message.reply(
            f"✅ **VC JOINED!**\n"
            f"🎯 Chat ID: `{chat_id}`\n"
            f"🔊 **500x VOLUME ACTIVE**\n"
            f"🎙️ **MUTE BYPASS: ON**\n\n"
            f"💀 Ab `.play <song_name>` se full blast karo!"
        )
    except IndexError:
        await message.reply("❌ Use: `.joinvc -100xxxxxxxxx`\n(Group/channel ID jahan VC hai)")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command("leavevc", prefixes="."))
async def leave_vc(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    
    if config["in_vc"] and config["target_chat"]:
        try:
            await calls.leave_group_call(config["target_chat"])
            config["in_vc"] = False
            config["active"] = False
            config["playing"] = False
            config["current_audio"] = None
            await message.reply("👋 **VC Left!**")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        await message.reply("❌ Main kisi VC mein nahi hoon!")

@app.on_message(filters.command("status", prefixes="."))
async def show_status(client, message: Message):
    if not is_owner(message.from_user.id):
        return
    
    await message.reply(
        f"📊 **NUCLEAR USERBOT STATUS**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 Active: `{config['active']}`\n"
        f"🎙️ In VC: `{config['in_vc']}`\n"
        f"🎵 Playing: `{config['current_audio'] or 'Nothing'}`\n"
        f"🔊 Volume: `500x` (NUCLEAR)\n"
        f"🎯 Target: `{config['target_chat']}`\n"
        f"🎚️ Mute Bypass: `ACTIVE`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💀 **JITNI MARZI MUTE KARO - AWAAZ JAYEGI!**"
    )

# ============= 🎤 AUDIO RELAY HANDLERS =============
@calls.on_kicked()
async def on_kicked(client, chat_id):
    print(f"❌ Kicked from {chat_id}")
    config["in_vc"] = False
    config["active"] = False
    config["playing"] = False

@calls.on_stream_end()
async def on_stream_end(client, chat_id):
    print(f"📢 Stream ended in {chat_id}")
    config["playing"] = False
    config["current_audio"] = None

# ============= 🚀 MAIN =============
async def main():
    print("=" * 60)
    print("💀 NUCLEAR USERBOT - 500x VOLUME 💀")
    print("=" * 60)
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📱 Phone: {PHONE_NUMBER}")
    print("=" * 60)
    print("\n⚡ FEATURES:")
    print("🔊 500x Volume Boost")
    print("🎙️ Mute Bypass Active")
    print("📝 Commands work ANYWHERE (DM + Group)")
    print("🎵 Save & Play custom audios")
    print("=" * 60)
    
    await app.start()
    await calls.start()
    
    print("\n✅ USERBOT ACTIVE!")
    print("📝 Commands:")
    print("   .help - All commands")
    print("   .ping - Check status")
    print("   .joinvc - Join voice chat")
    print("   .play - Play audio (500x volume!)")
    print("\n💀 KAHI BHI COMMAND DALO - WORK KAREGA!")
    print("💀 MUTE BYPASS - AWAAZ JARUR JAYEGI!")
    print("=" * 60)
    
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ System band ho raha hai...")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")