"""
Afara — Streamlit demo
Home / Translation page: tap the mic, speak Yoruba into an animated
waveform capsule, then send the recording to a remote Hugging Face
Whisper Space and show the transcription.
"""

import streamlit as st
import base64
import sys
import traceback
import tempfile
import os
from GLOBAL_STYLES import GLOBAL_STYLES
from RECORDER import RECORDER_HTML
from AI_ORB import AI_ORB_HTML
from gradio_client import Client, handle_file

# ── Page setup ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Afara",
    page_icon="🌉",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Config ───────────────────────────────────────────────────────────────
# Replace with your actual Hugging Face Space repo id, e.g. "username/space-name"
HF_SPACE_ID = "your-username/whisper-yoruba-space"


# ── Global styling ───────────────────────────────────────────────────────
st.markdown(
    GLOBAL_STYLES,
    unsafe_allow_html=True,
)


# ── Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="afara-header">
        <p class="afara-logo">Afara</p>
        <p class="afara-tagline">Bridging the Gap Between Students and Indegeneous Ekiti Speakers</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tab state ────────────────────────────────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "translate"


def transcribe_with_hf_space(audio_path: str) -> str:
    """Send the recorded audio file to the remote HF Whisper Space and
    return the transcribed text."""
    client = Client(HF_SPACE_ID)
    result = client.predict(
        handle_file(audio_path),
        api_name="/predict",  # adjust to match the Space's actual endpoint name
    )
    return result


# ── Translate tab ────────────────────────────────────────────────────────
if st.session_state.active_tab == "translate":
    st.markdown(
        '<div class="afara-pill"><span>🎙️ Transcribe</span></div>',
        unsafe_allow_html=True,
    )

    # The recorder component below can't directly return values to Python
    # (it runs in a sandboxed iframe), so it writes the recorded audio, as
    # base64, into this hidden text_area via a same-origin DOM write.
    # Streamlit then picks up the change and reruns the script, same as
    # any other widget.
    audio_b64_value = st.text_area(
        "afara_audio_payload", key="audio_b64", label_visibility="collapsed"
    )

    st.iframe(RECORDER_HTML, height=190)

    if "last_processed_audio" not in st.session_state:
        st.session_state.last_processed_audio = ""

    @st.dialog("Translation")
    def show_result_modal(audio_path: str):
        with st.spinner("Transcribing..."):
            try:
                transcription = transcribe_with_hf_space(audio_path)
                st.markdown(
                    f"""
                    <div class="transcript-label">Yoruba Transcription</div>
                    <div class="transcript-text">{transcription}</div>
                    """,
                    unsafe_allow_html=True,
                )
            except Exception as e:
                print(f"[Afara] Transcription request failed: {e}", file=sys.stderr)
                traceback.print_exc()
                st.error(f"Couldn't reach the transcription service: {e}")
            finally:
                os.remove(audio_path)

    if audio_b64_value and audio_b64_value != st.session_state.last_processed_audio:
        st.session_state.last_processed_audio = audio_b64_value

        audio_bytes = base64.b64decode(audio_b64_value)
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        show_result_modal(tmp_path)

# ── AI tab: voice assistant orb ──────────────────────────────────────────
elif st.session_state.active_tab == "ai":
    st.markdown(
        '<div class="afara-pill"><span>🤖 Voice Assistant</span></div>',
        unsafe_allow_html=True,
    )
    st.iframe(AI_ORB_HTML, height=230)

# ── Learn tab (placeholder) ──────────────────────────────────────────────
elif st.session_state.active_tab == "learn":
    st.markdown(
        """
        <div class="coming-soon">
            <span class="material-symbols-outlined">school</span>
            <p style="margin-top:0.6rem; font-weight:600;">Learn Yoruba</p>
            <p style="font-size:0.85rem;">Coming soon</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Bottom nav bar ───────────────────────────────────────────────────────
nav = st.container(key="bottom_nav")
with nav:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            "Translate",
            icon=":material/translate:",
            key="nav_translate",
            type="primary" if st.session_state.active_tab == "translate" else "secondary",
            width="stretch",
            on_click=lambda: st.session_state.update(active_tab="translate"),
        )
    with col2:
        st.button(
            "AI",
            icon=":material/auto_awesome:",
            key="nav_ai",
            type="primary" if st.session_state.active_tab == "ai" else "secondary",
            width="stretch",
            on_click=lambda: st.session_state.update(active_tab="ai"),
        )
    with col3:
        st.button(
            "Learn",
            icon=":material/school:",
            key="nav_learn",
            type="primary" if st.session_state.active_tab == "learn" else "secondary",
            width="stretch",
            on_click=lambda: st.session_state.update(active_tab="learn"),
        )