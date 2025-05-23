// Content-Type: application/javascript
let mediaRecorder;
let audioChunks = [];
let socket;
let audioQueue = [];
let isPlaying = false;

document.addEventListener("DOMContentLoaded", () => {
  const orb = document.getElementById("orb");
  const chatLog = document.getElementById("chatLog");
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");

  // Use wss:// for HTTPS connections, ws:// for HTTP
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  socket = new WebSocket(`${protocol}//${window.location.host}/p1/recruiter_call_agent/ws`);

  socket.onmessage = async (event) => {
    const agentText = event.data;

    // Create a new message element with proper styling
    const messageElem = document.createElement('p');
    messageElem.className = 'agent';
    messageElem.innerHTML = agentText;
    chatLog.appendChild(messageElem);
    chatLog.scrollTop = chatLog.scrollHeight;

    const audioResp = await fetch('/p1/speak', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: agentText })
    });
    const blob = await audioResp.blob();
    const audioUrl = URL.createObjectURL(blob);

    // Add to queue instead of playing immediately
    audioQueue.push({ url: audioUrl, text: agentText });

    // Start playing if not already playing
    if (!isPlaying) {
      playNextInQueue();
    }
  };

  // Function to play next audio in queue
  function playNextInQueue() {
    if (audioQueue.length === 0) {
      isPlaying = false;
      return;
    }

    isPlaying = true;
    const nextAudio = audioQueue.shift();
    const audio = new Audio(nextAudio.url);

    orb.classList.add("talking");

    audio.play();

    audio.onended = () => {
      orb.classList.remove("talking");
      // Play the next item in queue when current one ends
      playNextInQueue();
    };
  }

  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const res = await fetch('/p1/transcribe', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      const userText = data.text;

      // Create a new message element with proper styling
      const messageElem = document.createElement('p');
      messageElem.className = 'user';
      messageElem.textContent = userText;
      chatLog.appendChild(messageElem);
      chatLog.scrollTop = chatLog.scrollHeight;

      socket.send(userText);
      audioChunks = [];
    };

    startBtn.onclick = () => {
      if (mediaRecorder.state !== 'recording') {
        audioChunks = [];
        mediaRecorder.start();
        orb.classList.add("talking");
        startBtn.disabled = true;
        stopBtn.disabled = false;
      }
    };

    stopBtn.onclick = () => {
      if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        orb.classList.remove("talking");
        startBtn.disabled = false;
        stopBtn.disabled = true;
      }
    };
  });
});
