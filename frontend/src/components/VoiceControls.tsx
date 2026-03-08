interface VoiceControlsProps {
  onConnect: () => void;
  onStart: () => void;
  onStop: () => void;
  disabledConnect: boolean;
  disabledRecord: boolean;
}

export default function VoiceControls({
  onConnect,
  onStart,
  onStop,
  disabledConnect,
  disabledRecord,
}: VoiceControlsProps) {
  return (
    <div className="voice-controls">
      <button
        className={`btn btn-connect ${disabledConnect ? 'btn-disabled' : ''}`}
        onClick={onConnect}
        disabled={disabledConnect}
        type="button"
      >
        Connect
      </button>

      <button
        className={`btn btn-start ${disabledRecord ? 'btn-disabled' : ''}`}
        onClick={onStart}
        disabled={disabledRecord}
        type="button"
      >
        Start Speaking
      </button>

      <button className="btn btn-stop" onClick={onStop} type="button">
        Stop
      </button>
    </div>
  );
}