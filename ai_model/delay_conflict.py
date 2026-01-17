import pygame
import sys
import pandas as pd

# ==============================
# LOAD SCHEDULE
# ==============================
df = pd.read_csv("daily_schedule.csv")

def time_to_min(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

# ==============================
# CONTROLLER LOGIC
# ==============================
def departure_delay_controller():
    print("\n--- DEPARTURE DELAY (AUTOMATIC CONTROL) ---")
    delayed_id = int(input("Enter Departure Delayed Train ID: "))

    delayed = df[df["train_id"] == delayed_id]
    if delayed.empty:
        print("❌ Train not found")
        sys.exit()

    delayed_time = time_to_min(delayed.iloc[0]["arrival_time"])

    upcoming = df[
        df["arrival_time"].apply(time_to_min) > delayed_time
    ].sort_values("arrival_time").iloc[0]

    upcoming_type = upcoming["train_type"]

    if upcoming_type in ["Goods", "Express"]:
        mode = "loop"
    else:
        mode = "reduced"

    return upcoming_type, mode

# ==============================
# GET DECISION
# ==============================
upcoming_type, mode = departure_delay_controller()

# ==============================
# TOP-LEFT MESSAGE (YOUR PREFERRED WORDING)
# ==============================
if mode == "loop":
    info_lines = [
        f"Upcoming Train Type : {upcoming_type}",
        "Decision            : Loop line diversion",
        "Reason              : Faster train allowed to overtake delayed departure"
    ]
else:
    info_lines = [
        f"Upcoming Train Type : {upcoming_type}",
        "Decision            : Reduced speed on main line",
        "Reason              : Departure delayed train must clear the station first"
    ]

# ==============================
# PYGAME SETUP
# ==============================
pygame.init()
WIDTH, HEIGHT = 1400, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Departure Delay – Coimbatore Railway Station")
clock = pygame.time.Clock()

# ==============================
# COLORS (REALISTIC)
# ==============================
SKY = (185, 215, 235)
GROUND = (210, 200, 175)
RAIL = (70, 70, 70)
SLEEPER = (145, 120, 95)

DELAYED = (190, 30, 30)
PASSENGER = (40, 120, 210)
GOODS = (40, 150, 90)

STATION_WALL = (165, 120, 80)
STATION_ROOF = (120, 60, 40)
PLATFORM = (150, 150, 150)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

font = pygame.font.SysFont("arial", 16, bold=True)
big_font = pygame.font.SysFont("arial", 18, bold=True)

# ==============================
# GEOMETRY
# ==============================
MAIN_Y = 260
LOOP_Y = 360

LEFT_SWITCH_X = 420
RIGHT_SWITCH_X = 1020
STATION_X = 680

# ==============================
# STATES
# ==============================
delayed_x = STATION_X
upcoming_x = 120
phase = "approach"
t_curve = 0.0
delayed_started = False

# ==============================
# BEZIER CURVE
# ==============================
def bezier(p0, p1, p2, p3, t):
    return (
        int((1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]),
        int((1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1])
    )

LEFT_START = (LEFT_SWITCH_X, MAIN_Y)
LEFT_END = (LEFT_SWITCH_X + 180, LOOP_Y)
LEFT_C1 = (LEFT_SWITCH_X + 60, MAIN_Y)
LEFT_C2 = (LEFT_SWITCH_X + 120, LOOP_Y)

RIGHT_START = (RIGHT_SWITCH_X - 180, LOOP_Y)
RIGHT_END = (RIGHT_SWITCH_X, MAIN_Y)
RIGHT_C1 = (RIGHT_SWITCH_X - 120, LOOP_Y)
RIGHT_C2 = (RIGHT_SWITCH_X - 60, MAIN_Y)

# ==============================
# DRAW FUNCTIONS
# ==============================
def draw_track(y, x1, x2):
    pygame.draw.line(screen, RAIL, (x1, y-6), (x2, y-6), 4)
    pygame.draw.line(screen, RAIL, (x1, y+6), (x2, y+6), 4)
    for x in range(x1, x2, 30):
        pygame.draw.rect(screen, SLEEPER, (x, y-10, 6, 20))

def draw_curve(p0, p1, p2, p3):
    prev = p0
    for i in range(1, 80):
        t = i / 80
        cur = bezier(p0, p1, p2, p3, t)
        pygame.draw.line(screen, RAIL, prev, cur, 4)
        if i % 4 == 0:
            pygame.draw.rect(
                screen, SLEEPER,
                ((prev[0] + cur[0]) // 2 - 4, (prev[1] + cur[1]) // 2 - 4, 8, 4)
            )
        prev = cur

def draw_train(x, y, color, label):
    pygame.draw.rect(screen, color, (x-25, y-15, 50, 30))
    screen.blit(font.render(label, True, BLACK), (x-45, y-35))

def draw_station():
    pygame.draw.rect(screen, PLATFORM, (STATION_X-120, MAIN_Y+15, 240, 18))
    pygame.draw.rect(screen, STATION_WALL, (STATION_X-100, MAIN_Y-90, 200, 70))
    pygame.draw.rect(screen, STATION_ROOF, (STATION_X-110, MAIN_Y-100, 220, 15))

    for i in range(-60, 80, 40):
        pygame.draw.rect(screen, WHITE, (STATION_X+i, MAIN_Y-70, 20, 20))

    pygame.draw.rect(screen, WHITE, (STATION_X-110, MAIN_Y-125, 220, 22))
    screen.blit(
        big_font.render("COIMBATORE RAILWAY STATION", True, BLACK),
        (STATION_X-108, MAIN_Y-123)
    )

# ==============================
# MAIN LOOP
# ==============================
running = True
while running:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # BACKGROUND
    screen.fill(SKY)
    pygame.draw.rect(screen, GROUND, (0, MAIN_Y-10, WIDTH, HEIGHT))

    # TRACKS
    draw_track(MAIN_Y, 0, WIDTH)
    draw_track(LOOP_Y, LEFT_END[0], RIGHT_START[0])
    draw_curve(LEFT_START, LEFT_C1, LEFT_C2, LEFT_END)
    draw_curve(RIGHT_START, RIGHT_C1, RIGHT_C2, RIGHT_END)

    # STATION
    draw_station()

    # UPCOMING TRAIN MOVEMENT
    if mode == "loop":
        if phase == "approach":
            upcoming_x += 2.8
            if upcoming_x >= LEFT_SWITCH_X:
                phase = "left_curve"
                t_curve = 0
            ux, uy = upcoming_x, MAIN_Y

        elif phase == "left_curve":
            t_curve += 0.02
            ux, uy = bezier(LEFT_START, LEFT_C1, LEFT_C2, LEFT_END, t_curve)
            if t_curve >= 1:
                phase = "loop"
                upcoming_x = LEFT_END[0]

        elif phase == "loop":
            upcoming_x += 3
            ux, uy = upcoming_x, LOOP_Y
            if upcoming_x >= RIGHT_START[0]:
                phase = "right_curve"
                t_curve = 0

        elif phase == "right_curve":
            t_curve += 0.02
            ux, uy = bezier(RIGHT_START, RIGHT_C1, RIGHT_C2, RIGHT_END, t_curve)
            if t_curve >= 1:
                phase = "after"
                upcoming_x = RIGHT_END[0]

        else:
            upcoming_x += 3
            ux, uy = upcoming_x, MAIN_Y
            if upcoming_x > WIDTH:
                delayed_started = True
    else:
        upcoming_x += 1.2
        ux, uy = upcoming_x, MAIN_Y
        delayed_started = True

    # DEPARTURE DELAYED TRAIN
    if delayed_started:
        delayed_x += 1.8

    color = GOODS if mode == "loop" else PASSENGER
    draw_train(ux, uy, color, upcoming_type)
    draw_train(delayed_x, MAIN_Y, DELAYED, "Departure Delayed")

    # TOP LEFT INFO
    y = 20
    for line in info_lines:
        screen.blit(font.render(line, True, BLACK), (20, y))
        y += 25

    pygame.display.flip()

pygame.quit()
sys.exit()
