import React, { useState, useRef } from 'react';
import './VoiceButton.css'; // We'll add this next!

export default function VoiceButton({ onAudioRecorded, isProcessing }) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    if (isProcessing) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        onAudioRecorded(audioBlob);
        
        // Stop all tracks to turn off the red recording light in browser tab
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Please allow microphone access to use the voice assistant.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="voice-button-container">
      <button 
        className={`voice-button ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
        onPointerDown={startRecording}
        onPointerUp={stopRecording}
        onPointerLeave={stopRecording}
        disabled={isProcessing}
      >
        <div className="mic-icon">
          {isProcessing ? '⏳' : (isRecording ? '🎙️' : '🎤')}
        </div>
        {isRecording && <div className="pulse-ring"></div>}
      </button>
      <p className="voice-hint">
        {isProcessing 
          ? "KrishiVaani is thinking..." 
          : (isRecording ? "Release to send" : "Tap and hold to speak")}
      </p>
    </div>
  );
}
