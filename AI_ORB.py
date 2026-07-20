AI_ORB_HTML = """
<div id="orbWrapper" class="orb-wrapper">
  <button id="orbBtn" class="orb-btn" aria-label="Start voice assistant" type="button">
    <div class="orb-ring"></div>
    <div class="orb-ring delay"></div>
    <div id="orbCore" class="orb-core"></div>
  </button>
</div>
<div id="orbStatus" class="orb-status">Tap the orb to talk</div>

<style>
  html, body { margin: 0; padding: 0; background: transparent; overflow: visible; }
  * { box-sizing: border-box; font-family: 'Inter', sans-serif; }

  .orb-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 210px;
  }

  .orb-btn {
    position: relative;
    width: 150px;
    height: 150px;
    border: none;
    background: transparent;
    padding: 0;
    cursor: pointer;
  }

  .orb-core {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background:
      radial-gradient(circle at 32% 28%, rgba(255,255,255,0.9), rgba(255,255,255,0) 40%),
      radial-gradient(circle at 65% 70%, #7cb342 0%, #2e7d32 55%, #1b5e20 100%);
    box-shadow:
      0 0 40px rgba(67, 160, 71, 0.45),
      0 0 90px rgba(67, 160, 71, 0.28),
      inset 0 0 30px rgba(255, 255, 255, 0.18);
    animation: orb-breathe 3.4s ease-in-out infinite;
    transition: box-shadow 0.08s linear;
    transform-origin: center;
  }

  .orb-ring {
    position: absolute;
    inset: -16px;
    border-radius: 50%;
    border: 1.5px solid rgba(67, 160, 71, 0.35);
    animation: orb-ripple 3.4s ease-out infinite;
  }
  .orb-ring.delay { animation-delay: 1.1s; }

  @keyframes orb-breathe {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.06); }
  }
  @keyframes orb-ripple {
    0%   { transform: scale(0.94); opacity: 0.55; }
    70%  { opacity: 0; }
    100% { transform: scale(1.35); opacity: 0; }
  }

  /* While actively listening, JS drives .orb-core's transform/box-shadow
     directly per audio frame, so the CSS breathing animation is paused
     to avoid the two fighting over the same properties. */
  .orb-wrapper.listening .orb-core { animation-play-state: paused; }
  .orb-wrapper.listening .orb-ring { animation-duration: 1.6s; }

  .orb-status {
    text-align: center;
    font-size: 1rem;
    font-weight: 500;
    color: #6b756b;
    margin-top: -0.6rem;
  }

  @media (max-width: 480px) {
    .orb-wrapper { height: 175px; }
    .orb-btn { width: 120px; height: 120px; }
    .orb-ring { inset: -13px; }
  }
</style>

<script>
(function() {
  const wrapper = document.getElementById('orbWrapper');
  const orbBtn = document.getElementById('orbBtn');
  const orbCore = document.getElementById('orbCore');
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
    const level = Math.min(1, rms * 4.5); // amplify so normal speech clearly moves the orb

    const scale = 1 + level * 0.4;
    const glowCore = 40 + level * 100;
    const glowOuter = 90 + level * 160;
    const glowAlpha1 = 0.45 + level * 0.4;
    const glowAlpha2 = 0.28 + level * 0.32;

    orbCore.style.transform = `scale(${scale.toFixed(3)})`;
    orbCore.style.boxShadow =
      `0 0 ${glowCore.toFixed(0)}px rgba(67, 160, 71, ${glowAlpha1.toFixed(2)}), ` +
      `0 0 ${glowOuter.toFixed(0)}px rgba(67, 160, 71, ${glowAlpha2.toFixed(2)}), ` +
      `inset 0 0 30px rgba(255, 255, 255, 0.18)`;

    rafId = requestAnimationFrame(drawFrame);
  }

  function resetOrbStyle() {
    orbCore.style.transform = '';
    orbCore.style.boxShadow = '';
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
    orbBtn.setAttribute('aria-label', 'Stop voice assistant');
    statusEl.textContent = 'Listening… tap outside to stop';
    drawFrame();
  }

  function stopListening() {
    if (!listening) return;
    listening = false;
    wrapper.classList.remove('listening');
    orbBtn.setAttribute('aria-label', 'Start voice assistant');
    statusEl.textContent = 'Tap the orb to talk';

    if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
    if (rafId) cancelAnimationFrame(rafId);
    if (audioCtx) audioCtx.close();
    resetOrbStyle();
  }

  orbBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (listening) {
      stopListening();
    } else {
      startListening();
    }
  });

  // Click anywhere outside the orb (within this component) stops listening
  document.addEventListener('mousedown', (e) => {
    if (listening && !wrapper.contains(e.target)) {
      stopListening();
    }
  });

  // Clicking elsewhere on the main page also stops it
  window.addEventListener('blur', () => {
    if (listening) stopListening();
  });
})();
</script>
"""