import pandas as pd
import joblib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ==============================
# LOAD DATA & MODEL
# ==============================
df = pd.read_csv("daily_schedule.csv")
model = joblib.load("model.pkl")

# ==============================
# TRAIN STATE CLASS
# ==============================
class TrainState:
    def __init__(self, train_id, speed, position=0, line="MAIN", status="MOVING", color="green"):
        self.train_id = train_id
        self.speed = speed
        self.position = position
        self.line = line        # MAIN / LOOP
        self.status = status    # MOVING / STOPPED
        self.color = color

train_states = {}

# ==============================
# HELPER FUNCTIONS
# ==============================
def get_train(train_id):
    row = df[df["train_id"] == int(train_id)]
    if row.empty:
        print(f"\n❌ ERROR: Train ID {train_id} not found\n")
        return None
    return row.iloc[0]

def goods_weight_rank(weight):
    return {"Heavy": 3, "Medium": 2, "Low": 1}.get(weight, 0)

# ==============================
# SAME TRACK / JUNCTION CONFLICT
# ==============================
def same_track_conflict():
    print("\n--- SAME TRACK / JUNCTION CONFLICT ---")

    t1_id = input("Enter Train 1 ID: ")
    t2_id = input("Enter Train 2 ID: ")
    cp1 = int(input("Checkpoint level Train 1 (1–5): "))
    cp2 = int(input("Checkpoint level Train 2 (1–5): "))

    t1 = get_train(t1_id)
    t2 = get_train(t2_id)
    if t1 is None or t2 is None:
        return

    # Tie breaker
    if t1["priority"] == t2["priority"] and cp1 == cp2:

        if t1["train_type"] != "Goods" and t2["train_type"] != "Goods":
            priority_train, reduced_train = (
                (t1, t2) if t1["passenger_count"] > t2["passenger_count"] else (t2, t1)
            )

        elif t1["train_type"] == "Goods" and t2["train_type"] == "Goods":
            priority_train, reduced_train = (
                (t1, t2) if goods_weight_rank(t1["goods_weight"]) >
                goods_weight_rank(t2["goods_weight"]) else (t2, t1)
            )

        else:
            decision = model.predict([[t1["priority"], t2["priority"], cp1, cp2]])[0]
            priority_train, reduced_train = (t1, t2) if decision == 0 else (t2, t1)

    else:
        decision = model.predict([[t1["priority"], t2["priority"], cp1, cp2]])[0]
        priority_train, reduced_train = (t1, t2) if decision == 0 else (t2, t1)

    reduced_speed = int(reduced_train["max_speed"] * 0.6)

    print("\n🚦 CONTROLLER DECISION")
    print(f"➡ Priority Train : {priority_train['train_id']}")
    print(f"⏸ Reduced Train  : {reduced_train['train_id']}")

    # Update simulation states
    train_states.clear()
    train_states[priority_train["train_id"]] = TrainState(
        priority_train["train_id"],
        priority_train["max_speed"],
        line="MAIN",
        color="green"
    )

    train_states[reduced_train["train_id"]] = TrainState(
        reduced_train["train_id"],
        reduced_speed,
        line="LOOP",
        color="orange"
    )

    run_simulation()

# ==============================
# DELAY CONFLICT
# ==============================
def delay_conflict():
    print("\n--- DELAY CONFLICT ---")
    delayed_id = input("Enter Delayed Train ID: ")
    delayed = get_train(delayed_id)
    if delayed is None:
        return

    train_states.clear()

    # Delayed train stopped at junction
    train_states[delayed["train_id"]] = TrainState(
        delayed["train_id"],
        speed=0,
        status="STOPPED",
        color="red"
    )

    print("🚨 Delayed train stopped at junction")

    upcoming = df[df["train_id"] != delayed["train_id"]].head(2)

    for _, row in upcoming.iterrows():
        reduced_speed = int(row["max_speed"] * 0.6)
        train_states[row["train_id"]] = TrainState(
            row["train_id"],
            reduced_speed,
            line="LOOP",
            color="orange"
        )

    run_simulation()

# ==============================
# VISUAL SIMULATION
# ==============================
def run_simulation():
    fig, ax = plt.subplots()
    ax.set_xlim(0, 100)
    ax.set_ylim(-2, 2)

    # Tracks
    ax.plot([0, 100], [0, 0], 'k-', lw=3)
    ax.plot([0, 100], [-1, -1], 'k--', lw=2)

    train_dots = {}

    def init():
        for tid, state in train_states.items():
            y = 0 if state.line == "MAIN" else -1
            dot, = ax.plot(state.position, y, 'o', color=state.color, label=f"Train {tid}")
            train_dots[tid] = dot
        ax.legend()
        return train_dots.values()

    def update(frame):
        for tid, state in train_states.items():
            if state.status == "MOVING":
                state.position += state.speed * 0.02
            y = 0 if state.line == "MAIN" else -1
            train_dots[tid].set_data(state.position, y)
        return train_dots.values()

    animation.FuncAnimation(fig, update, init_func=init, frames=200, interval=100)
    plt.title("🚦 Train Traffic Control Simulation")
    plt.show()

# ==============================
# CONTROLLER MENU
# ==============================
def controller_menu():
    while True:
        print("\n==============================")
        print(" TRAIN TRAFFIC CONTROLLER ")
        print("==============================")
        print("1. Same Track / Junction Conflict")
        print("2. Delay Conflict")
        print("3. Exit")

        ch = input("Select option: ")

        if ch == "1":
            same_track_conflict()
        elif ch == "2":
            delay_conflict()
        elif ch == "3":
            break
        else:
            print("❌ Invalid choice")

# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    controller_menu()
