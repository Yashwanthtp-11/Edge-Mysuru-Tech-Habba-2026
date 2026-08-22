import React, { useState, useRef } from 'react';
import VoiceButton from '../components/VoiceButton';
import './AssistantScreen.css';

export default function AssistantScreen() {
  const [isProcessing, setIsProcessing] = useState(false);
  const audioPlayerRef = useRef(null);

  const handleAudioRecorded = async (audioBlob) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      // POST to the public localtunnel API endpoint
      const response = await fetch('https://krishivaani-api-2026.loca.lt/assistant/chat', {
        method: 'POST',
        headers: {
          'Bypass-Tunnel-Reminder': 'true', // Bypasses localtunnel's anti-abuse warning screen for APIs
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to get response from assistant');
      }

      // Read the audio file returned by the backend
      const responseBlob = await response.blob();
      const audioUrl = URL.createObjectURL(responseBlob);
      
      // Play the response
      if (audioPlayerRef.current) {
        audioPlayerRef.current.src = audioUrl;
        audioPlayerRef.current.play();
      }
    } catch (error) {
      console.error(error);
      alert("Error communicating with KrishiVaani: " + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="assistant-screen">
      <div className="assistant-card">
        <div className="assistant-header">
          <div className="ai-avatar">🤖</div>
          <h1>KrishiVaani Voice AI</h1>
          <p>Ask in Kannada or Hindi about your crops, weather, or subsidies.</p>
        </div>

        <div className="voice-interaction-area">
          <VoiceButton 
            onAudioRecorded={handleAudioRecorded} 
            isProcessing={isProcessing} 
          />
        </div>
      </div>

      {/* Hidden audio element to play the AI's response */}
      <audio ref={audioPlayerRef} style={{ display: 'none' }} />
    </div>
  );
}
