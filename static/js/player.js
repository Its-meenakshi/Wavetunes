/* Shared mini-player logic.
   Each page defines `window.PAGE_TRACKS = [{title, artist, duration, cover}, ...]`
   and marks clickable elements with `data-track-idx="N"` before this script runs.
   `cover` is an integer 0-7 selecting one of the .cover-N gradient classes in style.css. */
(function () {
  const TRACKS = window.PAGE_TRACKS || [];
  const NOTE_FREQS = [261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 466.2, 523.3];

  const playPauseBtn = document.getElementById('playPauseBtn');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const progressBar = document.getElementById('progressBar');
  const progressFill = document.getElementById('progressFill');
  const curT = document.getElementById('curT');
  const durT = document.getElementById('durT');
  const volumeSlider = document.getElementById('volumeSlider');
  const songTitle = document.getElementById('songTitle');
  const songArtist = document.getElementById('songArtist');
  const miniCover = document.getElementById('miniCover');
  const toast = document.getElementById('toast');

  if (!playPauseBtn) return; // player not present on this page (e.g. auth pages)

  let audioCtx = null, oscillator = null, gainNode = null;
  let currentIndex = -1, playing = false, fakeTime = 0, fakeTimer = null;

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove('show'), 2800);
  }
  function formatTime(s) {
    const m = Math.floor(s / 60), sec = Math.floor(s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
  }
  function setIcon(isPlaying) {
    playPauseBtn.innerHTML = isPlaying ? '<i class="fa-solid fa-pause"></i>' : '<i class="fa-solid fa-play"></i>';
  }
  function stopTone() {
    if (oscillator) { try { oscillator.stop(); } catch (e) {} oscillator = null; }
    clearInterval(fakeTimer);
  }
  function markPlayingRows(index) {
    document.querySelectorAll('[data-track-idx]').forEach(el => {
      el.classList.toggle('playing', Number(el.dataset.trackIdx) === index);
    });
  }
  function startTone(index) {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    stopTone();
    oscillator = audioCtx.createOscillator();
    gainNode = audioCtx.createGain();
    oscillator.type = 'sine';
    oscillator.frequency.value = NOTE_FREQS[index % NOTE_FREQS.length];
    gainNode.gain.value = (volumeSlider ? volumeSlider.value : 80) / 100 * 0.06;
    oscillator.connect(gainNode).connect(audioCtx.destination);
    oscillator.start();
    playing = true;
    setIcon(true);
    fakeTimer = setInterval(() => {
      fakeTime += 1;
      const dur = TRACKS[index].duration || 200;
      if (fakeTime >= dur) { nextTrack(); return; }
      curT.textContent = formatTime(fakeTime);
      durT.textContent = formatTime(dur);
      progressFill.style.width = (fakeTime / dur * 100) + '%';
    }, 1000);
  }
  function loadTrack(index, autoplay = true) {
    const t = TRACKS[index];
    if (!t) return;
    currentIndex = index;
    fakeTime = 0;
    markPlayingRows(index);
    songTitle.textContent = t.title;
    songArtist.textContent = t.artist || t.genre || '';
    miniCover.innerHTML = `<div class="cover-${(t.cover ?? index) % 8}" style="width:100%;height:100%;"></div>`;
    durT.textContent = formatTime(t.duration || 200);
    curT.textContent = '0:00';
    progressFill.style.width = '0%';
    if (autoplay) startTone(index);
    showToast(`Demo tone playing for "${t.title}" — connect a real audio file to hear the actual track`);
  }
  function togglePlay(index) {
    if (index === currentIndex && playing) { stopTone(); playing = false; setIcon(false); return; }
    if (index === currentIndex && !playing) { startTone(index); return; }
    loadTrack(index, true);
  }
  function nextTrack() {
    if (!TRACKS.length) return;
    loadTrack((currentIndex + 1 + TRACKS.length) % TRACKS.length, true);
  }
  function prevTrack() {
    if (!TRACKS.length) return;
    loadTrack((currentIndex - 1 + TRACKS.length) % TRACKS.length, true);
  }

  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-track-idx]');
    if (el && !e.target.closest('[data-like]')) togglePlay(Number(el.dataset.trackIdx));
  });

  playPauseBtn.addEventListener('click', () => {
    if (currentIndex === -1) { loadTrack(0, true); return; }
    if (playing) { stopTone(); playing = false; setIcon(false); } else { startTone(currentIndex); }
  });
  if (prevBtn) prevBtn.addEventListener('click', prevTrack);
  if (nextBtn) nextBtn.addEventListener('click', nextTrack);
  if (progressBar) progressBar.addEventListener('click', (e) => {
    if (currentIndex === -1) return;
    const rect = progressBar.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    fakeTime = pct * (TRACKS[currentIndex].duration || 200);
  });
  if (volumeSlider) volumeSlider.addEventListener('input', () => {
    if (gainNode) gainNode.gain.value = volumeSlider.value / 100 * 0.06;
  });

  window.WaveTunesPlayer = { loadTrack, togglePlay, nextTrack, prevTrack };

  const greetEl = document.getElementById('greetText');
  if (greetEl) {
    const hour = new Date().getHours();
    greetEl.textContent = hour < 12 ? 'Good morning,' : hour < 18 ? 'Good afternoon,' : 'Good evening,';
  }
})();
