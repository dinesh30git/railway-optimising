import express from "express";
import cors from "cors";
import { spawn } from "child_process";

const app = express();

// ==============================
// MIDDLEWARE
// ==============================
app.use(cors());
app.use(express.json());

// ==============================
// HEALTH CHECK (optional)
// ==============================
app.get("/", (req, res) => {
  res.send("🚦 Railway Controller Backend Running");
});

// ==============================
// ML CONFLICT PREDICTION API
// ==============================
app.post("/api/predict-conflict", (req, res) => {
  const pythonProcess = spawn("python", [
    "ai_model/predict_train.py",
    JSON.stringify(req.body)
  ]);

  let output = "";
  let error = "";

  pythonProcess.stdout.on("data", data => {
    output += data.toString();
  });

  pythonProcess.stderr.on("data", data => {
    error += data.toString();
  });

  pythonProcess.on("close", () => {
    if (error) {
      console.error("Python error:", error);
      return res.status(500).json({ error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (e) {
      res.status(500).json({
        error: "Invalid response from ML model",
        raw: output
      });
    }
  });
});

// ==============================
// START SERVER
// ==============================
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Backend running at http://localhost:${PORT}`);
});
