AI_ORB_HTML = """
<div id="orbWrapper" class="va-wrapper">
  <button id="orbBtn" class="va-btn" aria-label="Start voice assistant" type="button">
    <svg class="va-mic-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
      <line x1="12" y1="19" x2="12" y2="23"/>
      <line x1="8" y1="23" x2="16" y2="23"/>
    </svg>
    <div class="va-rings">
      <div class="va-ring ring1"></div>
      <div class="va-ring ring2"></div>
      <div class="va-ring ring3"></div>
    </div>
  </button>
</div>
<div id="orbStatus" class="va-status">Tap the mic to talk</div>

<style>
  html, body {
    margin: 0; padding: 0; height: 100%;
    overflow: hidden; background: transparent;
  }
  * { box-sizing: border-box; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

  .va-wrapper {
    display: flex; align-items: center; justify-content: center;
    width: 100%; height: 220px;
    overflow: hidden;               /* ← this clips the expanding rings */
  }

  .va-btn {
    position: relative;
    width: 120px; height: 120px;
    border: none; border-radius: 50%;
    background: linear-gradient(145deg, #3a7d5a 0%, #1f4a33 100%);
    box-shadow:
      0 6px 18px rgba(0,0,0,0.4),
      inset 0 1px 2px rgba(255,255,255,0.25);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    z-index: 2;
  }
  .va-btn:hover { transform: scale(1.04); }

  /* mic icon */
  .va-mic-icon {
    width: 44px; height: 44px;
    color: #ffffff;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    transition: opacity 0.2s, color 0.3s;
  }

  /* stop icon – shown when listening */
  .va-wrapper.listening .va-mic-icon {
    opacity: 0;
  }
  .va-btn::after {
    content: '';
    position: absolute; top: 50%; left: 50%;
    width: 22px; height: 22px;
    background: #ffffff;
    border-radius: 3px;
    transform: translate(-50%, -50%) scale(0);
    transition: transform 0.25s cubic-bezier(0.18, 0.89, 0.32, 1.28);
    box-shadow: 0 0 16px rgba(0,230,118,0.6);
  }
  .va-wrapper.listening .va-btn::after {
    transform: translate(-50%, -50%) scale(1);
  }

  /* expanding rings */
  .va-rings {
    position: absolute; inset: -8px; z-index: 1;
  }
  .va-ring {
    position: absolute; inset: 0;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.5);
    opacity: 0; transform: scale(0.9);
  }
  .va-wrapper.listening .va-ring {
    animation: va-ring-expand 1.8s ease-out infinite;
  }
  .ring1 { animation-delay: 0s; }
  .ring2 { animation-delay: 0.6s; }
  .ring3 { animation-delay: 1.2s; }

  @keyframes va-ring-expand {
    0%   { transform: scale(0.9); opacity: 0.7; }
    100% { transform: scale(1.4); opacity: 0; }
  }

  /* status */
  .va-status {
    text-align: center; font-size: 0.95rem; font-weight: 500;
    color: #6b756b; margin-top: 0.4rem; transition: color 0.3s;
  }
  .va-wrapper.listening + .va-status {
    color: #00e676; text-shadow: 0 0 8px rgba(0,230,118,0.6);
  }

  @media (max-width: 480px) {
    .va-wrapper { height: 190px; }
    .va-btn { width: 100px; height: 100px; }
  }
</style>

<script>
(function() {
  const wrapper = document.getElementById('orbWrapper');
  const btn = document.getElementById('orbBtn');
  const statusEl = document.getElementById('orbStatus');

  let audioCtx, analyser, source, mediaStream;
  let dataArray, rafId = null;
  let listening = false;

  function drawFrame() {
    analyser.getByteTimeDomainData(dataArray);
    let sumSquares = 0;
    for (let i = 0; i < dataArray.length; i++) {
      const v = (dataArray[i] - 128) / 128;
      sumSquares += v * v;
    }
    const rms = Math.sqrt(sumSquares / dataArray.length);
    const level = Math.min(1, rms * 3.8);

    // Scale button slightly based on voice
    const scale = 1 + level * 0.07;
    btn.style.transform = `scale(${scale.toFixed(3)})`;

    // Increase glow on the stop icon
    const stopIcon = btn.querySelector('::after'); // can't directly target, so adjust box-shadow on btn
    btn.style.boxShadow = `
      0 ${6 + level * 6}px ${18 + level * 20}px rgba(0,0,0,0.4),
      inset 0 1px 2px rgba(255,255,255,0.25),
      0 0 ${14 + level * 34}px rgba(0,230,118,${0.3 + level * 0.5})`;

    rafId = requestAnimationFrame(drawFrame);
  }

  function resetStyle() {
    btn.style.transform = '';
    btn.style.boxShadow = '';
  }

  async function startListening() {
    if (listening) return;
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      statusEl.textContent = 'Microphone access denied';
      return;
    }

    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    source = audioCtx.createMediaStreamSource(mediaStream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 512;
    dataArray = new Uint8Array(analyser.fftSize);
    source.connect(analyser);

    listening = true;
    wrapper.classList.add('listening');
    btn.setAttribute('aria-label', 'Stop voice assistant');
    statusEl.textContent = 'Listening… tap outside to stop';
    drawFrame();
  }

  function stopListening() {
    if (!listening) return;
    listening = false;
    wrapper.classList.remove('listening');
    btn.setAttribute('aria-label', 'Start voice assistant');
    statusEl.textContent = 'Tap the mic to talk';

    if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
    if (rafId) cancelAnimationFrame(rafId);
    if (audioCtx) audioCtx.close();
    resetStyle();
  }

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (listening) { stopListening(); } else { startListening(); }
  });

  document.addEventListener('mousedown', (e) => {
    if (listening && !wrapper.contains(e.target)) { stopListening(); }
  });

  window.addEventListener('blur', () => {
    if (listening) stopListening();
  });
})();
</script>
"""