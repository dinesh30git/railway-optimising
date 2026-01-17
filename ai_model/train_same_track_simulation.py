import pygame
import sys
import pandas as pd
import joblib

# ==============================
# LOAD DATA & MODEL
# ==============================
df = pd.read_csv("daily_schedule.csv")
model = joblib.load("model.pkl")

# ==============================
# GLOBAL STATE
# ==============================
conflict_decision = {
    "priority": None,
    "priority_id": None,
    "reduced_id": None,
    "reduced_speed": None
}
decision_reason = ""

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
    global decision_reason

    t1_id = input("Enter Train 1 ID: ")
    t2_id = input("Enter Train 2 ID: ")
    cp1 = int(input("Checkpoint level Train 1 (1–5): "))
    cp2 = int(input("Checkpoint level Train 2 (1–5): "))

    t1 = get_train(t1_id)
    t2 = get_train(t2_id)
    if t1 is None or t2 is None:
        return

    if t1["priority"] == t2["priority"] and cp1 == cp2:
        if t1["train_type"] != "Goods" and t2["train_type"] != "Goods":
            priority_train, reduced_train = (
                (t1, t2) if t1["passenger_count"] > t2["passenger_count"]
                else (t2, t1)
            )
            decision_reason = "Higher passenger count"

        elif t1["train_type"] == "Goods" and t2["train_type"] == "Goods":
            priority_train, reduced_train = (
                (t1, t2) if goods_weight_rank(t1["goods_weight"]) >
                goods_weight_rank(t2["goods_weight"])
                else (t2, t1)
            )
            decision_reason = "Heavier goods train"

        else:
            decision = model.predict([[t1["priority"], t2["priority"], cp1, cp2]])[0]
            priority_train, reduced_train = (t1, t2) if decision == 0 else (t2, t1)
            decision_reason = "ML-based decision"
    else:
        decision = model.predict([[t1["priority"], t2["priority"], cp1, cp2]])[0]
        priority_train, reduced_train = (t1, t2) if decision == 0 else (t2, t1)
        decision_reason = "ML-based decision"

    reduced_speed = int(reduced_train["max_speed"] * 0.6)

    conflict_decision["priority"] = (
        "train1" if priority_train["train_id"] == int(t1_id) else "train2"
    )
    conflict_decision["priority_id"] = priority_train["train_id"]
    conflict_decision["reduced_id"] = reduced_train["train_id"]
    conflict_decision["reduced_speed"] = reduced_speed

    run_simulation()

# ==============================
# PYGAME SIMULATION
# ==============================
def run_simulation():
    pygame.init()

    WIDTH, HEIGHT = 1200, 460
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Railway Y-Junction Conflict Simulation")

    clock = pygame.time.Clock()

    # COLORS
    SKY = (200, 225, 255)
    GROUND = (195, 185, 165)
    RAIL = (90, 90, 90)
    SLEEPER = (120, 100, 80)
    GREEN = (0, 170, 0)
    ORANGE = (255, 160, 0)
    BLACK = (0, 0, 0)
    PANEL = (240, 240, 240)

    font = pygame.font.SysFont("arial", 18)
    bold = pygame.font.SysFont("arial", 18, bold=True)

    TOP_Y = 150
    BOTTOM_Y = 310
    SINGLE_Y = 230
    MERGE_X = 650

    train1_x = -120
    train2_x = -120

    speed1 = 3.2
    speed2 = 3.2

    if conflict_decision["priority"] == "train1":
        speed2 = conflict_decision["reduced_speed"] * 0.03
    else:
        speed1 = conflict_decision["reduced_speed"] * 0.03

    def draw_track(y, x1, x2):
        pygame.draw.line(screen, RAIL, (x1, y - 6), (x2, y - 6), 4)
        pygame.draw.line(screen, RAIL, (x1, y + 6), (x2, y + 6), 4)
        for x in range(x1, x2, 30):
            pygame.draw.rect(screen, SLEEPER, (x, y - 10, 6, 20))

    def draw_train(x, y, color, train_id):
        pygame.draw.rect(screen, color, (x, y - 18, 80, 36))
        pygame.draw.circle(screen, BLACK, (x + 15, y + 22), 5)
        pygame.draw.circle(screen, BLACK, (x + 65, y + 22), 5)
        screen.blit(font.render(f"Train {train_id}", True, BLACK),
                    (x + 6, y - 38))

    # ==============================
    # REALISTIC STATION (UPDATED)
    # ==============================
    def draw_station(x, y):
        # Platform
        pygame.draw.rect(screen, (165, 165, 165), (x - 60, y + 40, 300, 22))
        pygame.draw.line(screen, (230, 200, 40),
                         (x - 60, y + 40), (x + 240, y + 40), 3)

        # Building
        pygame.draw.rect(screen, (165, 115, 75),
                         (x - 30, y - 55, 240, 90))

        # Roof
        pygame.draw.rect(screen, (120, 60, 40),
                         (x - 40, y - 70, 260, 15))

        # Windows
        for wx in range(0, 200, 50):
            pygame.draw.rect(screen, (245, 245, 245),
                             (x - 15 + wx, y - 35, 30, 25))

        # Entrance
        pygame.draw.rect(screen, (50, 50, 50),
                         (x + 95, y - 10, 40, 45))

        # Canopy
        pygame.draw.rect(screen, (130, 130, 130),
                         (x - 90, y + 20, 360, 8))
        for p in range(-60, 260, 70):
            pygame.draw.line(screen, (110, 110, 110),
                             (x + p, y + 20), (x + p, y + 40), 3)

        # Name board
        pygame.draw.rect(screen, (255, 255, 255),
                         (x - 40, y - 95, 260, 25))
        screen.blit(bold.render("COIMBATORE RAILWAY STATION", True, BLACK),
                    (x - 35, y - 92))

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # BACKGROUND
        screen.fill(SKY)
        pygame.draw.rect(screen, GROUND, (0, HEIGHT // 2 - 70, WIDTH, HEIGHT))

        # TRACKS
        draw_track(TOP_Y, 0, MERGE_X)
        draw_track(BOTTOM_Y, 0, MERGE_X)
        draw_track(SINGLE_Y, MERGE_X + 110, WIDTH - 260)
        pygame.draw.line(screen, RAIL, (MERGE_X, TOP_Y),
                         (MERGE_X + 110, SINGLE_Y), 4)
        pygame.draw.line(screen, RAIL, (MERGE_X, BOTTOM_Y),
                         (MERGE_X + 110, SINGLE_Y), 4)

        # STATION
        draw_station(WIDTH - 240, SINGLE_Y - 35)

        # INFO PANEL
        pygame.draw.rect(screen, PANEL, (15, 15, 430, 130))
        screen.blit(bold.render(
            f"Priority Train : Train {conflict_decision['priority_id']}",
            True, BLACK), (25, 25))
        screen.blit(font.render(
            f"Reduced Train  : Train {conflict_decision['reduced_id']}",
            True, BLACK), (25, 55))
        screen.blit(font.render(
            f"Reason         : {decision_reason}",
            True, BLACK), (25, 85))

        # SPEED PANEL
        pygame.draw.rect(screen, PANEL, (WIDTH - 260, 15, 240, 60))
        screen.blit(bold.render("Reduced Speed", True, BLACK),
                    (WIDTH - 240, 25))
        screen.blit(bold.render(
            f"{conflict_decision['reduced_speed']} km/h",
            True, BLACK), (WIDTH - 240, 45))

        # MOVE TRAINS
        train1_x += speed1
        train2_x += speed2

        if train1_x < MERGE_X:
            draw_train(train1_x, TOP_Y, GREEN,
                       conflict_decision["priority_id"]
                       if conflict_decision["priority"] == "train1"
                       else conflict_decision["reduced_id"])
        else:
            draw_train(train1_x, SINGLE_Y, GREEN,
                       conflict_decision["priority_id"]
                       if conflict_decision["priority"] == "train1"
                       else conflict_decision["reduced_id"])

        if train2_x < MERGE_X:
            draw_train(train2_x, BOTTOM_Y, ORANGE,
                       conflict_decision["priority_id"]
                       if conflict_decision["priority"] == "train2"
                       else conflict_decision["reduced_id"])
        else:
            draw_train(train2_x, SINGLE_Y, ORANGE,
                       conflict_decision["priority_id"]
                       if conflict_decision["priority"] == "train2"
                       else conflict_decision["reduced_id"])

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    same_track_conflict()
