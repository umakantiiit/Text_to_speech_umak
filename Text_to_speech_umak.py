import streamlit as st
from google import genai
from google.genai import types
import wave
import os

# Voice type to prebuilt voice mapping\VOICE_MAPPING = {
    "Bright": "Zephyr",
    "Upbeat": "Puck",
    "Informative": "Charon",
    "Firm": "Kore",
    "Excitable": "Fenrir",
    "Youthful": "Leda",
    "Breezy": "Aoede",
    "Easy-going": "Callirrhoe",
    "Breathy": "Enceladus",
    "Clear": "Iapetus",
    "Smooth": "Algieba",
    "Gravelly": "Algenib",
    "Soft": "Achernar",
    "Even": "Schedar",
    "Mature": "Gacrux",
    "Forward": "Pulcherrima",
    "Friendly": "Achird",
    "Casual": "Zubenelgenubi",
    "Gentle": "Vindemiatrix",
    "Lively": "Sadachbia",
    "Knowledgeable": "Sadaltager",
    "Warm": "Sulafat"
}

# Initialize client
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("Google API key not found. Set GOOGLE_API_KEY in Streamlit secrets or env.")
    st.stop()
client = genai.Client(api_key=API_KEY)

# Helper to write wave file
@st.cache_data
def generate_wave(pcm_bytes: bytes, filename: str = "output.wav") -> str:
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_bytes)
    return filename

st.title("Text-to-Audio Converter")
mode = st.radio("Choose mode", ["Single speaker", "Multi speaker"])

if mode == "Single speaker":
    st.subheader("Single Speaker")
    text = st.text_area("Enter your text:")
    choice = st.selectbox("Select voice type", options=list(VOICE_MAPPING.keys()))
    if st.button("Generate Audio"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            voice_name = VOICE_MAPPING[choice]
            with st.spinner("Generating audio..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_name
                                )
                            )
                        )
                    )
                )
                pcm = response.candidates[0].content.parts[0].inline_data.data
                wav_file = generate_wave(pcm, "single.wav")
                audio_bytes = open(wav_file, "rb").read()
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    label="Download Audio",
                    data=audio_bytes,
                    file_name="single_speaker.wav",
                    mime="audio/wav"
                )

else:
    st.subheader("Multi Speaker")
    transcript = st.text_area("Enter multi-speaker transcript:", height=200)
    spk1_choice = st.selectbox("Speaker 1 voice type", options=list(VOICE_MAPPING.keys()), key="spk1")
    spk2_choice = st.selectbox("Speaker 2 voice type", options=list(VOICE_MAPPING.keys()), key="spk2")
    if st.button("Generate Multi-Speaker Audio"):
        if not transcript.strip():
            st.warning("Please enter the transcript.")
        else:
            v1 = VOICE_MAPPING[spk1_choice]
            v2 = VOICE_MAPPING[spk2_choice]
            with st.spinner("Generating multi-speaker audio..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=transcript,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                                speaker_voice_configs=[
                                    types.SpeakerVoiceConfig(
                                        speaker="Speaker 1",
                                        voice_config=types.VoiceConfig(
                                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                                voice_name=v1
                                            )
                                        )
                                    ),
                                    types.SpeakerVoiceConfig(
                                        speaker="Speaker 2",
                                        voice_config=types.VoiceConfig(
                                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                                voice_name=v2
                                            )
                                        )
                                    ),
                                ]
                            )
                        )
                    )
                )
                pcm = response.candidates[0].content.parts[0].inline_data.data
                wav_file = generate_wave(pcm, "multi.wav")
                audio_bytes = open(wav_file, "rb").read()
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    label="Download Multi-Speaker Audio",
                    data=audio_bytes,
                    file_name="multi_speaker.wav",
                    mime="audio/wav"
                )
