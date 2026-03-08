import { useState, useRef, useEffect } from 'react'
import VoiceControls from './components/VoiceControls.jsx'

function App() {
  const [status, setStatus] = useState<string>('Disconnected')
  const [lastMessage, setLastMessage] = useState<string>('')
  const wsRef = useRef<WebSocket | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<BlobPart[]>([])

  const patientId = 'patient_01' 

  const connectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close()
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/voice?patient_id=${patientId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setStatus('Connected')
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        setLastMessage(event.data)
      } else {
        const audioBlob = new Blob([event.data], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)
        audio.play().catch(e => console.warn("Autoplay blocked:", e))
      }
    }

    ws.onclose = () => {
      setStatus('Disconnected')
      console.log('WebSocket closed')
    }

    ws.onerror = (err) => {
      console.error('WebSocket error:', err)
      setStatus('Error')
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data)
        }
      }

      recorder.onstop = () => {
        if (audioChunksRef.current.length === 0) return

        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        wsRef.current?.send(blob)

        audioChunksRef.current = []

        recorder.start(4000)
      }

      recorder.start(4000) 
      setStatus('Recording... (speak now)')
    } catch (err) {
      console.error('Microphone access denied:', err)
      setStatus('Mic access denied')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
    }
    setStatus('Stopped')
  }

  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close()
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop())
      }
    }
  }, [])

 return (
    <div className="app-container">
      <h1 className="app-title">Voice AI Appointment Agent</h1>

      <div className="status-display">
        Status: <strong>{status}</strong>
      </div>

      {lastMessage && (
        <div className="last-message">
          Last message: {lastMessage}
        </div>
      )}

      <VoiceControls
        onConnect={connectWebSocket}
        onStart={startRecording}
        onStop={stopRecording}
        disabledConnect={status.includes('Connected')}
        disabledRecord={!status.includes('Connected')}
      />

      <p className="info-text">
        Speak in English, Hindi or Tamil.
        <br />
        The agent should detect language and respond accordingly.
      </p>
    </div>
  );
}

export default App