import { useState, useRef, useEffect } from "react";

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

  export const useVoice = (onResult) => {
    const [listening, setListening] = useState(false);
    const recognitionRef = useRef(null);
  
    useEffect(() => {
      console.log('[DEBUG] Initializing speech recognition...');
      if (!SpeechRecognition) {
        console.error('[ERROR] SpeechRecognition API not available');
        return;
      }
  
      const recog = new SpeechRecognition();
      console.log('[DEBUG] SpeechRecognition instance created', recog);
      
      recog.lang = "fr-FR";
      recog.interimResults = true;
      recog.maxAlternatives = 1;
  
      recog.onresult = (event) => {
        console.log('[DEBUG] SpeechRecognition result received', event);
        let interim = "";
        let final = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const res = event.results[i];
          console.log('[DEBUG] Result item:', res);
          if (res.isFinal) {
            final += res[0].transcript;
          } else {
            interim += res[0].transcript;
          }
        }
        console.log('[DEBUG] Interim:', interim, 'Final:', final);
        if (interim) onResult(interim, false);
        if (final) onResult(final, true);
      };
  
      recog.onerror = (e) => {
        console.error('[ERROR] SpeechRecognition error:', e);
        setListening(false);
      };
  
      recog.onend = () => {
        console.log('[DEBUG] SpeechRecognition ended');
        setListening(false);
      };
  
      recognitionRef.current = recog;
  
      return () => {
        if (recognitionRef.current) {
          console.log('[DEBUG] Cleaning up speech recognition');
          recognitionRef.current.stop();
        }
      };
    }, [onResult]);
  
    const start = () => {
      console.log('[DEBUG] Starting voice recognition');
      if (!recognitionRef.current) {
        console.error('[ERROR] Recognition not initialized');
        return;
      }
      try {
        recognitionRef.current.start();
        console.log('[DEBUG] Recognition started successfully');
        setListening(true);
      } catch (e) {
        console.error('[ERROR] Failed to start recognition:', e);
        onResult(`Impossible de démarrer le microphone: ${e.message}`, true);
      }
    };
  
    const stop = () => {
      console.log('[DEBUG] Stopping voice recognition');
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        setListening(false);
      }
    };
  
    return { listening, start, stop };
  };

export const speakText = (text) => {
  if (!window.speechSynthesis) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = "fr-FR";
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
};

export const readMessageAloud = (text) => {
  if (!text) return;
  
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  
  speakText(text);
};