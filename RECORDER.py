# ── Recorder component: mic button -> expanding waveform capsule ───────────
RECORDER_HTML = """
<div id="wrapper" class="mic-wrapper">
  <button id="micBtn" class="mic-btn" aria-label="Start recording" type="button">
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z"/>
      <path d="M19 11a1 1 0 0 0-2 0 5 5 0 0 1-10 0 1 1 0 0 0-2 0 7 7 0 0 0 6 6.92V20H9a1 1 0 0 0 0 2h6a1 1 0 0 0 0-2h-2v-2.08A7 7 0 0 0 19 11z"/>
    </svg>
  </button>
  <div id="capsule" class="capsule">
    <div id="bars" class="bars"></div>
  </div>
</div>
<div id="status" class="status">Tap to speak</div>

<style>
  html, body { margin: 0; padding: 0; background: transparent; overflow: visible; }
  * { box-sizing: border-box; font-family: 'Inter', sans-serif; }

  .mic-wrapper {
    position: relative;
    width: 320px;
    height: 120px;
    margin: 0 auto;
  }

  .mic-btn {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 96px; height: 96px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    background: linear-gradient(145deg, #2e7d32, #66bb6a);
    box-shadow: 0 10px 30px rgba(46, 125, 50, 0.35), inset 0 2px 4px rgba(255,255,255,0.25);
    display: flex; align-items: center; justify-content: center;
    z-index: 2;
    transition: opacity 0.3s ease, transform 0.3s ease;
  }
  .mic-btn svg { width: 38px; height: 38px; fill: white; }
  .mic-btn:hover { filter: brightness(1.05); }

  .capsule {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 0;
    height: 64px;
    border-radius: 32px;
    background: #ffffff;
    border: 1px solid #e2e8e2;
    box-shadow: 0 6px 24px rgba(0,0,0,0.08);
    overflow: hidden;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: width 0.35s cubic-bezier(.4,0,.2,1);
  }

  .bars {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 4px;
    width: 100%;
    height: 100%;
    padding: 0 18px;
    opacity: 0;
    transition: opacity 0.2s ease 0.15s;
  }
  .bar {
    flex: 1;
    min-width: 3px;
    max-width: 8px;
    height: 8px;
    border-radius: 4px;
    background: linear-gradient(180deg, #66bb6a, #2e7d32);
    transition: height 0.06s linear;
  }

  .mic-wrapper.recording .mic-btn {
    opacity: 0.12;
    transform: translate(-50%, -50%) scale(0.75);
  }
  .mic-wrapper.recording .capsule { width: 300px; }
  .mic-wrapper.recording .bars { opacity: 1; }

  .status {
    text-align: center;
    font-size: 0.95rem;
    font-weight: 500;
    color: #6b756b;
    margin-top: -0.4rem;
  }

  @media (max-width: 480px) {
    .mic-wrapper { width: 260px; }
    .mic-wrapper.recording .capsule { width: 240px; }
  }
</style>

<script>
(function() {
  const wrapper = document.getElementById('wrapper');
  const micBtn = document.getElementById('micBtn');
  const capsule = document.getElementById('capsule');
  const barsContainer = document.getElementById('bars');
  const statusEl = document.getElementById('status');

  const NUM_BARS = 20;
  const bars = [];
  for (let i = 0; i < NUM_BARS; i++) {
    const bar = document.createElement('div');
    bar.className = 'bar';
    barsContainer.appendChild(bar);
    bars.push(bar);
  }

  let audioCtx, analyser, source, mediaStream, mediaRecorder, chunks = [];
  let rafId = null;
  let recording = false;

  function setNativeValue(element, value) {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    element.focus();
    setter.call(element, value);
    element.dispatchEvent(new Event('input', { bubbles: true }));
    // st.text_area only sends its value to Python on blur (or Ctrl+Enter),
    // not on every input event — so we must blur it to force the commit.
    element.blur();
  }

  function sendToStreamlit(base64Audio) {
    console.log('[afara-debug] sendToStreamlit called, payload length:', base64Audio.length);
    try {
      const parentDoc = window.parent.document;
      console.log('[afara-debug] got parentDoc:', !!parentDoc);
      const ta = parentDoc.querySelector('textarea[aria-label="afara_audio_payload"]');
      console.log('[afara-debug] found textarea:', !!ta);
      if (ta) {
        setNativeValue(ta, base64Audio);
        console.log('[afara-debug] setNativeValue done, ta.value length now:', ta.value.length);
      }
    } catch (err) {
      console.error('[afara-debug] Could not bridge audio back to Streamlit:', err);
    }
  }

  function drawFrame() {
    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    const chunkSize = Math.floor(data.length / NUM_BARS) || 1;
    for (let i = 0; i < NUM_BARS; i++) {
      let sum = 0;
      for (let j = 0; j < chunkSize; j++) {
        sum += data[i * chunkSize + j] || 0;
      }
      const avg = sum / chunkSize;
      const pct = Math.max(8, (avg / 255) * 100);
      bars[i].style.height = pct + '%';
    }
    rafId = requestAnimationFrame(drawFrame);
  }

  function resetBars() {
    bars.forEach(b => b.style.height = '8px');
  }

  async function startRecording() {
    if (recording) return;
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      statusEl.textContent = 'Microphone access denied';
      return;
    }

    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    source = audioCtx.createMediaStreamSource(mediaStream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);

    chunks = [];
    mediaRecorder = new MediaRecorder(mediaStream);
    mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data); };
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'audio/webm' });
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result.split(',')[1];
        sendToStreamlit(base64);
      };
      reader.readAsDataURL(blob);
    };
    mediaRecorder.start();

    recording = true;
    wrapper.classList.add('recording');
    statusEl.textContent = 'Listening… tap outside to stop';
    drawFrame();
  }

  function stopRecording() {
    if (!recording) return;
    recording = false;
    wrapper.classList.remove('recording');
    statusEl.textContent = 'Transcribing…';

    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
    if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
    if (rafId) cancelAnimationFrame(rafId);
    if (audioCtx) audioCtx.close();
    resetBars();

    setTimeout(() => {
      if (!recording) statusEl.textContent = 'Tap to speak';
    }, 2500);
  }

  micBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    startRecording();
  });

  // Click anywhere outside the capsule (within this component) stops recording
  document.addEventListener('mousedown', (e) => {
    if (recording && !wrapper.contains(e.target)) {
      stopRecording();
    }
  });

  // Clicking elsewhere on the main page (outside this iframe) also stops it
  window.addEventListener('blur', () => {
    if (recording) stopRecording();
  });
})();
</script>
"""
