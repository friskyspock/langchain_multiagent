// Content-Type: application/javascript
let mediaRecorder;
let audioChunks = [];
let socket;
let audioQueue = [];
let isPlaying = false;

// Function to directly upload audio file for transcription (better latency)
async function uploadAudioForTranscription(audioBlob) {
  console.log("Directly uploading audio for transcription...", audioBlob.size + " bytes");

  try {
    // Create a FormData object and append the audio blob
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');

    // Send the audio directly to the server
    const response = await fetch('/transcribe-upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Upload error:", error);
    throw error;
  }
}

// Function to transcribe audio using the mock endpoint for testing
async function transcribeAudio(audioBlob) {
  try {
    console.log("Sending audio for transcription, size:", audioBlob.size + " bytes");

    // For testing, use the mock endpoint that doesn't require a real URL
    const response = await fetch('/transcribe-mock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}) // Empty body is fine for the mock endpoint
    });

    if (!response.ok) {
      throw new Error(`Transcription failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Transcription error:", error);
    // Return a fallback result if the server request fails
    return {
      status: true,
      text: "This is a fallback transcription. The server might be unavailable."
    };
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const orb = document.getElementById("orb");
  const chatLog = document.getElementById("chatLog");
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");

  // Use wss:// for HTTPS connections, ws:// for HTTP
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

  // Set up connection status indicators
  socket.onopen = () => {
    console.log('WebSocket connection established');
    // You could add a visual indicator that the connection is active
  };

  socket.onclose = (event) => {
    console.log('WebSocket connection closed', event.code, event.reason);
    // You could add a visual indicator that the connection is closed
    // And potentially a reconnect button

    // Auto reconnect after a delay
    setTimeout(() => {
      if (socket.readyState === WebSocket.CLOSED) {
        console.log('Attempting to reconnect...');
        socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
      }
    }, 3000);
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
    // You could add a visual error indicator
  };

  socket.onmessage = async (event) => {
    const agentText = event.data;

    // Create a new message element with proper styling
    const messageElem = document.createElement('p');
    messageElem.className = 'agent';
    messageElem.innerHTML = agentText;
    chatLog.appendChild(messageElem);
    chatLog.scrollTop = chatLog.scrollHeight;

    // Start fetching audio immediately
    const audioPromise = fetch('/speak', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: agentText })
    });

    try {
      // Process the response as soon as it's available
      const audioResp = await audioPromise;

      if (audioResp.ok) {
        // Use streaming to start processing audio as soon as data starts arriving
        const reader = audioResp.body.getReader();
        const chunks = [];

        // Read chunks as they arrive
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
        }

        // Combine chunks into a single blob
        const blob = new Blob(chunks, { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(blob);

        // Add to queue instead of playing immediately
        audioQueue.push({ url: audioUrl, text: agentText });

        // Start playing if not already playing
        if (!isPlaying) {
          playNextInQueue();
        }
      } else {
        console.error('Failed to get audio response');
      }
    } catch (error) {
      console.error('Error fetching audio:', error);
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
    const audio = new Audio();

    // Preload audio for faster playback
    audio.preload = "auto";

    // Add visual feedback before audio starts playing
    orb.classList.add("talking");

    // Set up event listeners before setting the source
    audio.oncanplaythrough = () => {
      // Play as soon as enough data is available
      audio.play().catch(err => console.error("Error playing audio:", err));
    };

    audio.onended = () => {
      orb.classList.remove("talking");
      // Clean up resources
      URL.revokeObjectURL(audio.src);
      // Play the next item in queue when current one ends
      playNextInQueue();
    };

    audio.onerror = (e) => {
      console.error("Audio playback error:", e);
      orb.classList.remove("talking");
      // Continue to next audio even if there's an error
      playNextInQueue();
    };

    // Set the source last to start loading
    audio.src = nextAudio.url;
  }

  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
      // Create a loading message
      const loadingElem = document.createElement('p');
      loadingElem.className = 'user loading';
      loadingElem.textContent = "Processing your message...";
      chatLog.appendChild(loadingElem);
      chatLog.scrollTop = chatLog.scrollHeight;

      // Create audio blob
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

      try {
        let result;

        // Try the direct upload method first (better latency)
        try {
          console.log("Trying direct file upload method...");
          result = await uploadAudioForTranscription(audioBlob);
        } catch (uploadError) {
          console.log("Direct upload failed, falling back to mock endpoint...", uploadError);
          // Fall back to the mock endpoint if direct upload fails
          result = await transcribeAudio(audioBlob);
        }

        if (result.status) {
          const userText = result.text;

          // Remove the loading message
          chatLog.removeChild(loadingElem);

          // Create a new message element with proper styling
          const messageElem = document.createElement('p');
          messageElem.className = 'user';
          messageElem.textContent = userText;
          chatLog.appendChild(messageElem);
          chatLog.scrollTop = chatLog.scrollHeight;

          // Send the transcribed text to the websocket
          socket.send(userText);
        } else {
          console.error('Transcription failed:', result.error);
          // Remove the loading message
          chatLog.removeChild(loadingElem);

          // Add error message to chat
          const messageElem = document.createElement('p');
          messageElem.className = 'user error';
          messageElem.textContent = "Sorry, I couldn't understand that. Please try again.";
          chatLog.appendChild(messageElem);
          chatLog.scrollTop = chatLog.scrollHeight;
        }
      } catch (error) {
        console.error('Error during transcription:', error);
        // Remove the loading message
        chatLog.removeChild(loadingElem);

        // Add error message to chat
        const messageElem = document.createElement('p');
        messageElem.className = 'user error';
        messageElem.textContent = "Sorry, I couldn't understand that. Please try again.";
        chatLog.appendChild(messageElem);
        chatLog.scrollTop = chatLog.scrollHeight;
      }

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
  }).catch(error => {
    console.error('Error accessing microphone:', error);
    // Show error message in chat
    const messageElem = document.createElement('p');
    messageElem.className = 'agent error';
    messageElem.textContent = "Microphone access is required for this application. Please allow microphone access and reload the page.";
    chatLog.appendChild(messageElem);
  });

  // Add a welcome message when the page loads
  setTimeout(() => {
    const welcomeElem = document.createElement('p');
    welcomeElem.className = 'agent';
    welcomeElem.innerHTML = "Hello! I'm your Flight Call Agent. How can I help you today? You can ask about flight status or search for flights.";
    chatLog.appendChild(welcomeElem);
  }, 1000);
});
