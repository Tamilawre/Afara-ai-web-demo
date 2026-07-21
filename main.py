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
# from ASR import transcribe_audio
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
HF_SPACE_ID = "LawsonE/YorubaASR"

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
        api_name="/transcribe_audio",  # adjust to match the Space's actual endpoint name
    )
    return result


# ── Transcription dialog ─────────────────────────────────────────────────
# NOTE: this must be called on EVERY rerun while it should stay open.
# Streamlit only keeps a dialog open across reruns that originate from
# widgets *inside* the dialog itself; any full-script rerun triggered from
# outside it (e.g. the recorder iframe posting another value) will close
# the dialog unless the decorated function is invoked again that run.
#
# The transcription work happens INSIDE this function (guarded so it only
# runs once per recording) so the "Transcribing..." spinner shows live
# inside the modal, instead of on the page behind it.
@st.dialog("Translation")
def show_result_modal():
    if st.session_state.transcription_text is None and st.session_state.transcription_error is None:
        with st.spinner("Transcribing..."):
            try:
                st.session_state.transcription_text = transcribe_with_hf_space(
                    st.session_state.pending_audio_path
                )
            except Exception as e:
                print(f"[Afara] Transcription request failed: {e}", file=sys.stderr)
                traceback.print_exc()
                st.session_state.transcription_error = str(e)
            finally:
                if st.session_state.pending_audio_path and os.path.exists(
                    st.session_state.pending_audio_path
                ):
                    os.remove(st.session_state.pending_audio_path)
                st.session_state.pending_audio_path = None

    if st.session_state.transcription_error:
        st.error(
            f"Couldn't reach the transcription service: {st.session_state.transcription_error}"
        )
    else:
        st.markdown(
        f"""
        <style>
        .transcript-text {{
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            font-size: 1.05rem;
            line-height: 1.5;
        }}
        .transcript-label {{
            color: #ffffff !important;
            opacity: 0.75;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        </style>
        <div class="transcript-label">Yoruba Transcription</div>
        <div class="transcript-text">{st.session_state.transcription_text}</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Close"):
        st.session_state.show_transcription_dialog = False
        st.session_state.transcription_text = None
        st.session_state.transcription_error = None
        st.rerun()


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
    if "pending_audio_path" not in st.session_state:
        st.session_state.pending_audio_path = None
    if "transcription_text" not in st.session_state:
        st.session_state.transcription_text = None
    if "transcription_error" not in st.session_state:
        st.session_state.transcription_error = None
    if "show_transcription_dialog" not in st.session_state:
        st.session_state.show_transcription_dialog = False

    # New audio arrived: stash it and open the dialog. The actual
    # transcription happens inside show_result_modal() itself so the
    # spinner is visible in the modal from the moment it opens.
    if audio_b64_value and audio_b64_value != st.session_state.last_processed_audio:
        st.session_state.last_processed_audio = audio_b64_value

        audio_bytes = base64.b64decode(audio_b64_value)
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        st.session_state.pending_audio_path = tmp_path
        st.session_state.transcription_text = None
        st.session_state.transcription_error = None
        st.session_state.show_transcription_dialog = True

    # Re-invoke the dialog on every rerun as long as it should stay open —
    # this is the line that keeps it visible across unrelated reruns.
    if st.session_state.show_transcription_dialog:
        show_result_modal()

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