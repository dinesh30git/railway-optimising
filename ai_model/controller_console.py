import pandas as pd
import joblib

# ==============================
# LOAD DATA & MODEL
# ==============================
df = pd.read_csv("daily_schedule.csv")
model = joblib.load("model.pkl")

# ==============================
# HELPER FUNCTIONS
# ==============================
def get_train(train_id):
    row = df[df["train_id"] == int(train_id)]
    if row.empty:
        print(f"\n❌ ERROR: Train ID {train_id} not found in schedule.\n")
        return None
    return row.iloc[0]

def goods_weight_rank(weight):
    rank = {"Heavy": 3, "Medium": 2, "Low": 1}
    return rank.get(weight, 0)

# ==============================
# SAME TRACK / JUNCTION CONFLICT
# ==============================
def same_track_conflict():
    print("\n--- SAME TRACK / JUNCTION CONFLICT ---")

    t1_id = input("Enter Train 1 ID: ")
    t2_id = input("Enter Train 2 ID: ")

    cp1 = int(input("Checkpoint level for Train 1 (1–5): "))
    cp2 = int(input("Checkpoint level for Train 2 (1–5): "))

    t1 = get_train(t1_id)
    t2 = get_train(t2_id)

    if t1 is None or t2 is None:
        return

    if t1["priority"] == t2["priority"] and cp1 == cp2:
        if t1["train_type"] != "Goods" and t2["train_type"] != "Goods":
            priority_train, reduced_train = (t1, t2) if t1["passenger_count"] > t2["passenger_count"] else (t2, t1)
        elif t1["train_type"] == "Goods" and t2["train_type"] == "Goods":
            priority_train, reduced_train = (t1, t2) if goods_weight_rank(t1["goods_weight"]) > goods_weight_rank(t2["goods_weight"]) else (t2, t1)
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
    print(f"⚠ Speed Limit    : {reduced_speed} km/h")

# ==============================
# DEPARTURE DELAY CONFLICT (NEW)
# ==============================
def departure_delay_conflict():
    print("\n--- DEPARTURE DELAY (REALISTIC CONTROL) ---")

    delayed_train_id = input("Enter Departure Delayed Train ID: ")
    delayed_train = get_train(delayed_train_id)
    if delayed_train is None:
        return

    upcoming_id = input("Enter Upcoming Train ID: ")
    upcoming_train = get_train(upcoming_id)
    if upcoming_train is None:
        return

    train_type = upcoming_train["train_type"]

    print(f"\n➡ Upcoming Train Type: {train_type}")

    # ------------------------------
    # LOOP LINE LOGIC
    # ------------------------------
    if train_type in ["Express", "Goods"]:
        print(
            f"🚦 {train_type} Train {upcoming_id} "
            f"→ LOOP LINE CROSSING"
        )
        
        return

    # ------------------------------
    # REDUCED SPEED LOGIC
    # ------------------------------
    if train_type in ["Passenger", "Local", "Premium"]:
        reduced_speed = int(upcoming_train["max_speed"] * 0.6)

        print(
            f"🚆 {train_type} Train {upcoming_id} "
            f"→ CAUTION BEFORE STATION"
        )
        print(
            f"⚠ Reduced Speed: {reduced_speed} km/h"
        )
        print(
            f"➡ Departure delayed Train {delayed_train_id} "
            f"cleared FIRST from station"
        )
       
        return

    # ------------------------------
    # SAFETY FALLBACK
    # ------------------------------
    reduced_speed = int(upcoming_train["max_speed"] * 0.6)
    print(
        f"⚠ Unknown train type '{train_type}' "
        f"→ Treated as Passenger | "
        f"Speed {reduced_speed} km/h"
    )

# ==============================
# DELAY CONFLICT (BLOCK-BASED)
# ==============================
def delay_conflict():
    print("\n--- DELAY CONFLICT (REALISTIC CONTROL FLOW) ---")

    delayed_train_id = input("Enter Delayed Train ID: ")
    delayed_train = get_train(delayed_train_id)
    if delayed_train is None:
        return

    def time_to_minutes(t):
        h, m = map(int, t.split(":"))
        return h * 60 + m

    delayed_arrival = time_to_minutes(delayed_train["arrival_time"])

    upcoming_trains = df[
        df["arrival_time"].notna()
        & (df["arrival_time"].apply(time_to_minutes) > delayed_arrival)
    ].sort_values("arrival_time")

    delay_cleared = False

    for _, row in upcoming_trains.iterrows():
        if not delay_cleared:
            cleared = input("Has delayed train cleared junction? (yes/no): ").lower()
            if cleared == "no":
                reduced_speed = int(row["max_speed"] * 0.6)
                print(
                    f"⏸ Train {row['train_id']} → LOOP LINE | "
                    f"Speed {reduced_speed} km/h"
                )
                continue
            else:
                delay_cleared = True

        main_free = input("Is MAIN LINE free? (yes/no): ").lower()
        if main_free == "yes":
            print(f"➡ Train {row['train_id']} → MAIN LINE")
        else:
            reduced_speed = int(row["max_speed"] * 0.6)
            print(
                f"⏸ Train {row['train_id']} → LOOP LINE | "
                f"Speed {reduced_speed} km/h"
            )

# ==============================
# CONTROLLER MENU
# ==============================
def controller_menu():
    while True:
        print("\n=================================")
        print("  TRAIN TRAFFIC CONTROLLER SYSTEM")
        print("=================================")
        print("1️⃣ Same Track / Junction Conflict")
        print("2️⃣ Arrival / Block Delay Conflict")
        print("3️⃣ Departure Delay Conflict (NEW)")
        print("4️⃣ Exit")

        choice = input("Select option (1/2/3/4): ")

        if choice == "1":
            same_track_conflict()
        elif choice == "2":
            delay_conflict()
        elif choice == "3":
            departure_delay_conflict()
        elif choice == "4":
            print("Exiting controller system.")
            break
        else:
            print("❌ Invalid option. Try again.")

# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    controller_menu()
