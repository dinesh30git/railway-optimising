import { useState } from "react";

export default function TrainDetails({ train, onInjectDelay }) {
  const [delay, setDelay] = useState("");

  if (!train) {
    return (
      <div className="train-details empty">
        Select a train
      </div>
    );
  }

  const applyDelay = () => {
    if (!delay || isNaN(delay)) return;
    onInjectDelay(train.train_id, Number(delay));
    setDelay("");
  };

  return (
    <div className="train-details">
      <h4>Train Details</h4>

      <p><strong>ID:</strong> {train.train_id}</p>
      <p><strong>Name:</strong> {train.train_name}</p>
      <p><strong>Route:</strong> {train.source} → {train.destination}</p>
      <p><strong>Arrival:</strong> {train.arrival_time}</p>
      <p><strong>Priority:</strong> {train.priority}</p>
      <p><strong>Status:</strong> {train.delay > 0 ? "DELAYED" : "ON TIME"}</p>

      <input
        type="number"
        placeholder="Enter delay (minutes)"
        value={delay}
        onChange={e => setDelay(e.target.value)}
      />

      <button onClick={applyDelay}>
        Inject Delay
      </button>
    </div>
  );
}
