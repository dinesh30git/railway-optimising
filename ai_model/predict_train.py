import sys
import json
import pandas as pd
import joblib

# ==============================
# LOAD MODEL AND DATA
# ==============================
model = joblib.load("model.pkl")
df = pd.read_csv("daily_schedule.csv")

# ==============================
# PREDICTION FUNCTION
# ==============================
def predict_conflict(data):
    train1_id = int(data["train1_id"])
    train2_id = int(data["train2_id"])
    cp1 = int(data["cp1"])
    cp2 = int(data["cp2"])

    t1 = df[df["train_id"] == train1_id].iloc[0]
    t2 = df[df["train_id"] == train2_id].iloc[0]

    features = [[
        int(t1["priority"]),
        int(t2["priority"]),
        cp1,
        cp2
    ]]

    decision = int(model.predict(features)[0])

    if decision == 0:
        return {
            "priority_train": train1_id,
            "reduced_train": train2_id,
            "suggested_speed": int(t2["max_speed"] * 0.6),
            "reason": "ML predicted lower priority on same block"
        }
    else:
        return {
            "priority_train": train2_id,
            "reduced_train": train1_id,
            "suggested_speed": int(t1["max_speed"] * 0.6),
            "reason": "ML predicted lower priority on same block"
        }

# ==============================
# ENTRY POINT FOR NODE
# ==============================
if __name__ == "__main__":
    input_data = json.loads(sys.argv[1])
    result = predict_conflict(input_data)
    print(json.dumps(result))
