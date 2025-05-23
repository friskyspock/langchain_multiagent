// Content-Type: application/javascript
let mediaRecorder;
let audioChunks = [];
let socket;
let sessionId;

document.addEventListener("DOMContentLoaded", () => {
  // Get session ID from localStorage
  sessionId = localStorage.getItem('interviewSessionId');
  if (!sessionId) {
    alert('No interview session found. Please set up an interview first.');
    window.location.href = '/setup';
    return;
  }

  // Fetch session data to display candidate info
  fetch(`/p1/recruiter_call_agent/get_session_info/${sessionId}`)
    .then(response => response.json())
    .then(data => {
      if (data.status) {
        document.getElementById('candidateName').textContent = data.candidate_name;
        document.getElementById('jobTitle').textContent = data.job_title;
      }
    })
    .catch(error => {
      console.error('Error fetching session info:', error);
    });

  const orb = document.getElementById("orb");
  const chatLog = document.getElementById("chatLog");
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");

  // Connect to WebSocket with session ID
  // Use wss:// for HTTPS connections, ws:// for HTTP
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  socket = new WebSocket(`${protocol}//${window.location.host}/p1/recruiter_call_agent/ws?session-id=${sessionId}`);

  socket.onmessage = async (event) => {
    const agentText = event.data;
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

    const audio = new Audio(audioUrl);
    orb.classList.add("talking");
    audio.play();
    audio.onended = () => orb.classList.remove("talking");
  };

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