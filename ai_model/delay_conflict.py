import pygame
import sys
import pandas as pd
import joblib
from enum import Enum

# ==============================
# LOAD DATA & MODEL
# ==============================
df = pd.read_csv("daily_schedule.csv")
model = joblib.load("model.pkl")

# ==============================
# ENUMS FOR SIMULATION TYPES
# ==============================
class SimulationType(Enum):
    SAME_TRACK_CONFLICT = 1
    DEPARTURE_DELAY = 2

# ==============================
# PYGAME CONFIGURATION
# ==============================
pygame.init()
WIDTH, HEIGHT = 1400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ==============================
# REALISTIC COLORS
# ==============================
SKY = (185, 215, 245)
GROUND = (200, 190, 170)
RAIL = (65, 65, 65)
SLEEPER = (135, 115, 90)
STATION_WALL = (160, 115, 75)
STATION_ROOF = (115, 55, 35)
PLATFORM = (145, 145, 145)
PLATFORM_EDGE = (220, 190, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRAIN_GREEN = (40, 160, 70)
TRAIN_ORANGE = (240, 140, 30)
TRAIN_RED = (200, 40, 40)
TRAIN_BLUE = (45, 115, 200)
SIGNAL_GREEN = (0, 200, 0)
SIGNAL_RED = (255, 0, 0)

# ==============================
# FONTS
# ==============================
font_small = pygame.font.SysFont("arial", 14)
font_normal = pygame.font.SysFont("arial", 16, bold=True)
font_title = pygame.font.SysFont("arial", 20, bold=True)

# ==============================
# HELPER FUNCTIONS
# ==============================
def get_train(train_id):
    """Fetch train details from CSV"""
    row = df[df["train_id"] == int(train_id)]
    if row.empty:
        print(f"\n❌ ERROR: Train ID {train_id} not found\n")
        return None
    return row.iloc[0]

def goods_weight_rank(weight):
    """Rank goods train by weight"""
    return {"Heavy": 3, "Medium": 2, "Low": 1}.get(weight, 0)

def time_to_min(t):
    """Convert HH:MM to minutes"""
    h, m = map(int, t.split(":"))
    return h * 60 + m

def bezier_curve(p0, p1, p2, p3, t):
    """Calculate Bezier curve point"""
    return (
        int((1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]),
        int((1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1])
    )

# ==============================
# DRAWING FUNCTIONS
# ==============================
def draw_track(y, x1, x2):
    """Draw realistic railway track"""
    # Rails
    pygame.draw.line(screen, RAIL, (x1, y-7), (x2, y-7), 5)
    pygame.draw.line(screen, RAIL, (x1, y+7), (x2, y+7), 5)
    
    # Sleepers
    for x in range(x1, x2, 35):
        pygame.draw.rect(screen, SLEEPER, (x-2, y-12, 8, 24))

def draw_curved_track(p0, p1, p2, p3):
    """Draw curved track using Bezier"""
    prev = p0
    for i in range(1, 100):
        t = i / 100
        cur = bezier_curve(p0, p1, p2, p3, t)
        pygame.draw.line(screen, RAIL, (prev[0], prev[1]-7), (cur[0], cur[1]-7), 5)
        pygame.draw.line(screen, RAIL, (prev[0], prev[1]+7), (cur[0], cur[1]+7), 5)
        if i % 5 == 0:
            mid = ((prev[0] + cur[0]) // 2, (prev[1] + cur[1]) // 2)
            pygame.draw.rect(screen, SLEEPER, (mid[0]-2, mid[1]-12, 8, 24))
        prev = cur

def draw_signal(x, y, color):
    """Draw railway signal"""
    # Removed - no signals in simulation
    pass

def draw_station(x, y):
    """Draw detailed railway station"""
    # Platform
    pygame.draw.rect(screen, PLATFORM, (x-150, y+20, 300, 25))
    pygame.draw.line(screen, PLATFORM_EDGE, (x-150, y+20), (x+150, y+20), 4)
    
    # Main building
    pygame.draw.rect(screen, STATION_WALL, (x-120, y-100, 240, 85))
    
    # Roof
    pygame.draw.rect(screen, STATION_ROOF, (x-130, y-115, 260, 18))
    
    # Windows
    for wx in range(-90, 100, 55):
        pygame.draw.rect(screen, WHITE, (x+wx, y-75, 30, 28))
        pygame.draw.line(screen, BLACK, (x+wx+15, y-75), (x+wx+15, y-47), 2)
        pygame.draw.line(screen, BLACK, (x+wx, y-61), (x+wx+30, y-61), 2)
    
    # Entrance
    pygame.draw.rect(screen, (45, 45, 45), (x+20, y-15, 45, 50))
    
    # Canopy supports
    pygame.draw.rect(screen, (120, 120, 120), (x-180, y+5, 360, 10))
    for px in range(-150, 160, 75):
        pygame.draw.line(screen, (100, 100, 100), (x+px, y+5), (x+px, y+20), 4)
    
    # Name board
    pygame.draw.rect(screen, WHITE, (x-130, y-145, 260, 28))
    pygame.draw.rect(screen, BLACK, (x-130, y-145, 260, 28), 2)
    name_text = font_title.render("COIMBATORE RAILWAY STATION", True, BLACK)
    screen.blit(name_text, (x - name_text.get_width()//2, y-141))

def draw_train(x, y, color, label, speed=0):
    """Draw detailed train with label"""
    # Train body
    pygame.draw.rect(screen, color, (x-35, y-20, 70, 40), border_radius=5)
    pygame.draw.rect(screen, BLACK, (x-35, y-20, 70, 40), 2, border_radius=5)
    
    # Windows
    pygame.draw.rect(screen, (200, 220, 240), (x-25, y-12, 15, 12))
    pygame.draw.rect(screen, (200, 220, 240), (x-5, y-12, 15, 12))
    pygame.draw.rect(screen, (200, 220, 240), (x+15, y-12, 15, 12))
    
    # Wheels
    pygame.draw.circle(screen, BLACK, (x-20, y+25), 7)
    pygame.draw.circle(screen, BLACK, (x+20, y+25), 7)
    pygame.draw.circle(screen, (100, 100, 100), (x-20, y+25), 4)
    pygame.draw.circle(screen, (100, 100, 100), (x+20, y+25), 4)
    
    # Label
    label_text = font_normal.render(label, True, BLACK)
    screen.blit(label_text, (x - label_text.get_width()//2, y-45))
    
    # Speed indicator
    if speed > 0:
        speed_text = font_small.render(f"{speed} km/h", True, BLACK)
        screen.blit(speed_text, (x - speed_text.get_width()//2, y+35))

def draw_info_panel(lines):
    """Draw information panel"""
    panel_height = len(lines) * 30 + 40
    pygame.draw.rect(screen, (240, 240, 240), (20, 20, 450, panel_height), border_radius=8)
    pygame.draw.rect(screen, BLACK, (20, 20, 450, panel_height), 3, border_radius=8)
    
    y = 40
    for line in lines:
        text = font_normal.render(line, True, BLACK)
        screen.blit(text, (35, y))
        y += 30

# ==============================
# SIMULATION 1: SAME TRACK CONFLICT
# ==============================
def run_same_track_simulation(t1, t2, priority_train, reduced_train, reduced_speed, reason):
    """Y-Junction conflict simulation"""
    pygame.display.set_caption("Same Track Conflict - Y-Junction Simulation")
    
    # Track geometry
    MAIN_Y = 220
    LOOP_Y = 360
    MERGE_X = 700
    STATION_X = 1100
    
    # Curve control points - loop merges into main
    LOWER_CURVE_START = (MERGE_X, LOOP_Y)
    LOWER_CURVE_END = (MERGE_X + 150, MAIN_Y)
    LOWER_C1 = (MERGE_X + 50, LOOP_Y)
    LOWER_C2 = (MERGE_X + 100, (LOOP_Y + MAIN_Y) // 2)
    
    # Train states - both start from left
    train1_x = -80
    train2_x = -80
    
    # Determine which train takes which route
    if priority_train["train_id"] == t1["train_id"]:
        speed1 = priority_train["max_speed"] * 0.035  # Priority on main line
        speed2 = reduced_speed * 0.035  # Reduced on loop line
        color1 = TRAIN_GREEN
        color2 = TRAIN_ORANGE
        train1_line = "main"
        train2_line = "loop"
    else:
        speed1 = reduced_speed * 0.035  # Reduced on loop line
        speed2 = priority_train["max_speed"] * 0.035  # Priority on main line
        color1 = TRAIN_ORANGE
        color2 = TRAIN_GREEN
        train1_line = "loop"
        train2_line = "main"
    
    # Track which train is merging
    train1_merging = False
    train2_merging = False
    train1_merge_progress = 0
    train2_merge_progress = 0
    train1_merged_x = 0
    train2_merged_x = 0
    
    info_lines = [
        "CONFLICT TYPE: Y-Junction / Same Track",
        f"Priority Train: {priority_train['train_id']} ({priority_train['train_name']})",
        f"Reduced Train: {reduced_train['train_id']} ({reduced_train['train_name']})",
        f"Reduced Speed: {reduced_speed} km/h",
        f"Reason: {reason}"
    ]
    
    running = True
    started = False
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    started = True
        
        # Background
        screen.fill(SKY)
        pygame.draw.rect(screen, GROUND, (0, MAIN_Y-30, WIDTH, HEIGHT))
        
        # Draw tracks - loop only goes up to merge point
        draw_track(MAIN_Y, 0, WIDTH)
        draw_track(LOOP_Y, 0, MERGE_X)
        
        # Draw merge curve
        draw_curved_track(LOWER_CURVE_START, LOWER_C1, LOWER_C2, LOWER_CURVE_END)
        
        # Draw station
        draw_station(STATION_X, MAIN_Y - 35)
        
        # Only move trains after started
        if started:
            # Update positions
            if train1_line == "loop" and not train1_merging:
                train1_x += speed1
                if train1_x >= MERGE_X:
                    train1_merging = True
                    train1_merge_progress = 0
            elif train1_merging and train1_merge_progress < 1.0:
                train1_merge_progress += 0.015
                if train1_merge_progress >= 1.0:
                    train1_merged_x = LOWER_CURVE_END[0]
            elif train1_merged_x > 0:
                train1_merged_x += speed1 * 28.6
            else:
                train1_x += speed1
            
            if train2_line == "loop" and not train2_merging:
                train2_x += speed2
                if train2_x >= MERGE_X:
                    train2_merging = True
                    train2_merge_progress = 0
            elif train2_merging and train2_merge_progress < 1.0:
                train2_merge_progress += 0.015
                if train2_merge_progress >= 1.0:
                    train2_merged_x = LOWER_CURVE_END[0]
            elif train2_merged_x > 0:
                train2_merged_x += speed2 * 28.6
            else:
                train2_x += speed2
        
        # Draw Train 1
        if train1_line == "main":
            draw_train(train1_x, MAIN_Y, color1, f"Train {t1['train_id']}", int(speed1 * 28.6))
        else:
            # Train 1 on loop line
            if not train1_merging:
                draw_train(train1_x, LOOP_Y, color1, f"Train {t1['train_id']}", int(speed1 * 28.6))
            elif train1_merge_progress < 1.0:
                # Train merging
                pos = bezier_curve(LOWER_CURVE_START, LOWER_C1, LOWER_C2, LOWER_CURVE_END, train1_merge_progress)
                draw_train(pos[0], pos[1], color1, f"Train {t1['train_id']}", int(speed1 * 28.6))
            else:
                # After merge, continue on main line
                draw_train(train1_merged_x, MAIN_Y, color1, f"Train {t1['train_id']}", int(speed1 * 28.6))
        
        # Draw Train 2
        if train2_line == "main":
            draw_train(train2_x, MAIN_Y, color2, f"Train {t2['train_id']}", int(speed2 * 28.6))
        else:
            # Train 2 on loop line
            if not train2_merging:
                draw_train(train2_x, LOOP_Y, color2, f"Train {t2['train_id']}", int(speed2 * 28.6))
            elif train2_merge_progress < 1.0:
                # Train merging
                pos = bezier_curve(LOWER_CURVE_START, LOWER_C1, LOWER_C2, LOWER_CURVE_END, train2_merge_progress)
                draw_train(pos[0], pos[1], color2, f"Train {t2['train_id']}", int(speed2 * 28.6))
            else:
                # After merge, continue on main line
                draw_train(train2_merged_x, MAIN_Y, color2, f"Train {t2['train_id']}", int(speed2 * 28.6))
        
        # Info panel
        draw_info_panel(info_lines)
        
        # Show start instruction
        if not started:
            start_text = font_title.render("Press SPACE to start simulation", True, BLACK)
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        
        # Exit condition - check all possible positions
        max_x1 = max(train1_x, train1_merged_x)
        max_x2 = max(train2_x, train2_merged_x)
        if started and max_x1 > WIDTH + 100 and max_x2 > WIDTH + 100:
            running = False
    
    return True

# ==============================
# SIMULATION 2: DEPARTURE DELAY
# ==============================
def run_departure_delay_simulation(delayed_train, upcoming_train, mode):
    """Departure delay conflict simulation"""
    pygame.display.set_caption("Departure Delay Conflict Simulation")
    
    MAIN_Y = 260
    LOOP_Y = 360
    STATION_X = 600
    LEFT_SWITCH_X = 400
    RIGHT_SWITCH_X = 900
    
    # Curve points
    LEFT_START = (LEFT_SWITCH_X, MAIN_Y)
    LEFT_END = (LEFT_SWITCH_X + 150, LOOP_Y)
    LEFT_C1 = (LEFT_SWITCH_X + 50, MAIN_Y)
    LEFT_C2 = (LEFT_SWITCH_X + 100, LOOP_Y)
    
    RIGHT_START = (RIGHT_SWITCH_X - 150, LOOP_Y)
    RIGHT_END = (RIGHT_SWITCH_X, MAIN_Y)
    RIGHT_C1 = (RIGHT_SWITCH_X - 100, LOOP_Y)
    RIGHT_C2 = (RIGHT_SWITCH_X - 50, MAIN_Y)
    
    delayed_x = STATION_X
    upcoming_x = 100
    phase = "approach"
    t_curve = 0.0
    delayed_started = False
    
    upcoming_color = TRAIN_BLUE if mode == "reduced" else TRAIN_GREEN
    
    if mode == "loop":
        info_lines = [
            "CONFLICT TYPE: Departure Delay",
            f"Delayed Train: {delayed_train['train_id']} (Stopped at station)",
            f"Upcoming Train: {upcoming_train['train_id']} ({upcoming_train['train_type']})",
            "Decision: Loop line diversion",
            "Reason: Faster train overtaking delayed departure"
        ]
    else:
        info_lines = [
            "CONFLICT TYPE: Departure Delay",
            f"Delayed Train: {delayed_train['train_id']} (Stopped at station)",
            f"Upcoming Train: {upcoming_train['train_id']} ({upcoming_train['train_type']})",
            "Decision: Reduced speed on main line",
            f"Reduced Speed: {int(upcoming_train['max_speed'] * 0.6)} km/h",
            "Reason: Delayed train must clear station first"
        ]
    
    running = True
    started = False
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    started = True
        
        # Background
        screen.fill(SKY)
        pygame.draw.rect(screen, GROUND, (0, MAIN_Y-30, WIDTH, HEIGHT))
        
        # Draw tracks
        draw_track(MAIN_Y, 0, WIDTH)
        draw_track(LOOP_Y, LEFT_END[0], RIGHT_START[0])
        draw_curved_track(LEFT_START, LEFT_C1, LEFT_C2, LEFT_END)
        draw_curved_track(RIGHT_START, RIGHT_C1, RIGHT_C2, RIGHT_END)
        
        # Draw station
        draw_station(STATION_X, MAIN_Y - 35)
        
        # Upcoming train movement - only after started
        if started:
            if mode == "loop":
                if phase == "approach":
                    upcoming_x += 2.8
                    ux, uy = upcoming_x, MAIN_Y
                    if upcoming_x >= LEFT_SWITCH_X:
                        phase = "left_curve"
                        t_curve = 0
                elif phase == "left_curve":
                    t_curve = min(1.0, t_curve + 0.015)
                    ux, uy = bezier_curve(LEFT_START, LEFT_C1, LEFT_C2, LEFT_END, t_curve)
                    if t_curve >= 1:
                        phase = "loop"
                        upcoming_x = LEFT_END[0]
                elif phase == "loop":
                    upcoming_x += 3.2
                    ux, uy = upcoming_x, LOOP_Y
                    if upcoming_x >= RIGHT_START[0]:
                        phase = "right_curve"
                        t_curve = 0
                elif phase == "right_curve":
                    t_curve = min(1.0, t_curve + 0.015)
                    ux, uy = bezier_curve(RIGHT_START, RIGHT_C1, RIGHT_C2, RIGHT_END, t_curve)
                    if t_curve >= 1:
                        phase = "after"
                        upcoming_x = RIGHT_END[0]
                else:
                    upcoming_x += 3.2
                    ux, uy = upcoming_x, MAIN_Y
                    if upcoming_x > WIDTH:
                        delayed_started = True
            else:
                upcoming_x += 1.5
                ux, uy = upcoming_x, MAIN_Y
                if upcoming_x > STATION_X - 100:
                    delayed_started = True
            
            # Delayed train movement
            if delayed_started:
                delayed_x += 2.0
        else:
            ux, uy = upcoming_x, MAIN_Y
        
        # Draw trains
        draw_train(ux, uy, upcoming_color, f"Train {upcoming_train['train_id']}", 
                  int(upcoming_train['max_speed'] if mode == "loop" else upcoming_train['max_speed'] * 0.6) if started else 0)
        draw_train(delayed_x, MAIN_Y, TRAIN_RED, f"Train {delayed_train['train_id']} (DELAYED)", 
                  0 if not delayed_started else 60)
        
        # Info panel
        draw_info_panel(info_lines)
        
        # Show start instruction
        if not started:
            start_text = font_title.render("Press SPACE to start simulation", True, BLACK)
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        
        # Exit condition
        if started and delayed_x > WIDTH + 100:
            running = False
    
    return True

# ==============================
# SIMULATION 3: ARRIVAL DELAY
# ==============================
def run_arrival_delay_simulation(delayed_train, upcoming_trains):
    """Arrival delay simulation with multiple trains"""
    pygame.display.set_caption("Arrival Delay Conflict Simulation")
    
    MAIN_Y = 240
    LOOP_Y = 340
    STATION_X = 700
    
    delayed_x = STATION_X
    trains_state = []
    
    for i, train in enumerate(upcoming_trains[:3]):  # Max 3 upcoming trains
        trains_state.append({
            'train': train,
            'x': 100 + i * 250,
            'line': 'main',
            'speed': 0,
            'color': TRAIN_ORANGE
        })
    
    delay_cleared = False
    
    info_lines = [
        "CONFLICT TYPE: Arrival Block Delay",
        f"Delayed Train: {delayed_train['train_id']} (Blocking junction)",
        "Status: Waiting for clearance",
        "Upcoming trains diverted to loop line"
    ]
    
    running = True
    frame_count = 0
    
    while running:
        clock.tick(60)
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Background
        screen.fill(SKY)
        pygame.draw.rect(screen, GROUND, (0, MAIN_Y-30, WIDTH, HEIGHT))
        
        # Draw tracks
        draw_track(MAIN_Y, 0, WIDTH)
        draw_track(LOOP_Y, 300, WIDTH)
        
        # Draw station
        draw_station(STATION_X, MAIN_Y - 35)
        
        # Delayed train clears after 5 seconds
        if frame_count > 300 and not delay_cleared:
            delay_cleared = True
            info_lines[2] = "Status: Junction cleared - trains proceeding"
        
        # Move delayed train
        if delay_cleared:
            delayed_x += 2.5
        
        # Move upcoming trains
        for state in trains_state:
            if not delay_cleared:
                # Move to loop line
                if state['x'] < 300:
                    state['x'] += 1.8
                else:
                    state['line'] = 'loop'
                    state['x'] += 2.2
                    state['color'] = TRAIN_BLUE
            else:
                # Return to main line after clearance
                state['line'] = 'main'
                state['x'] += 2.8
                state['color'] = TRAIN_GREEN
        
        # Draw signals
        draw_signal(STATION_X - 150, MAIN_Y, SIGNAL_RED if not delay_cleared else SIGNAL_GREEN)
        
        # Draw trains
        draw_train(delayed_x, MAIN_Y, TRAIN_RED, f"Train {delayed_train['train_id']} (DELAYED)", 
                  0 if not delay_cleared else 65)
        
        for state in trains_state:
            y = MAIN_Y if state['line'] == 'main' else LOOP_Y
            draw_train(state['x'], y, state['color'], f"Train {state['train']['train_id']}", 
                      int(state['train']['max_speed'] * 0.6) if not delay_cleared else state['train']['max_speed'])
        
        # Info panel
        draw_info_panel(info_lines)
        
        pygame.display.flip()
        
        # Exit after all trains pass
        if delayed_x > WIDTH + 100 and all(s['x'] > WIDTH + 100 for s in trains_state):
            running = False
    
    return True

# ==============================
# CONFLICT DECISION LOGIC
# ==============================
def same_track_conflict_decision(t1, t2, cp1, cp2):
    """Make same track conflict decision"""
    if t1["priority"] == t2["priority"] and cp1 == cp2:
        if t1["train_type"] != "Goods" and t2["train_type"] != "Goods":
            if t1["passenger_count"] > t2["passenger_count"]:
                return t1, t2, "Higher passenger count"
            else:
                return t2, t1, "Higher passenger count"
        elif t1["train_type"] == "Goods" and t2["train_type"] == "Goods":
            if goods_weight_rank(t1["goods_weight"]) > goods_weight_rank(t2["goods_weight"]):
                return t1, t2, "Heavier goods load"
            else:
                return t2, t1, "Heavier goods load"
        else:
            decision = model.predict([[t1["priority"], t2["priority"], cp1, cp2]])[0]
            priority_train, reduced_train = (t1, t2) if decision == 0 else (t2, t1)
            return priority_train, reduced_train, "ML prediction based on priority"
    else:
        decision = model.predict([[t1["priority"], t2["priority"], cp1, cp2]])[0]
        priority_train, reduced_train = (t1, t2) if decision == 0 else (t2, t1)
        return priority_train, reduced_train, "ML prediction based on priority and checkpoint"

# ==============================
# MAIN MENU
# ==============================
def main_menu():
    """Main controller menu"""
    while True:
        print("\n" + "="*60)
        print("       RAILWAY TRAFFIC CONTROL SIMULATION SYSTEM")
        print("="*60)
        print("\n1️⃣  Same Track / Y-Junction Conflict")
        print("2️⃣  Departure Delay Conflict")
        print("3️⃣  Exit System")
        print("\n" + "="*60)
        
        choice = input("\nSelect simulation type (1-3): ").strip()
        
        if choice == "1":
            # Same Track Conflict
            print("\n--- SAME TRACK / Y-JUNCTION CONFLICT ---")
            t1_id = input("Enter Train 1 ID: ").strip()
            t2_id = input("Enter Train 2 ID: ").strip()
            
            t1 = get_train(t1_id)
            t2 = get_train(t2_id)
            
            if t1 is None or t2 is None:
                continue
            
            cp1 = int(input(f"Checkpoint level for Train {t1_id} (1-5): "))
            cp2 = int(input(f"Checkpoint level for Train {t2_id} (1-5): "))
            
            priority_train, reduced_train, reason = same_track_conflict_decision(t1, t2, cp1, cp2)
            reduced_speed = int(reduced_train["max_speed"] * 0.6)
            
            print(f"\n🚦 DECISION: Train {priority_train['train_id']} given priority")
            print(f"⚠️  Train {reduced_train['train_id']} speed reduced to {reduced_speed} km/h")
            print(f"📋 Reason: {reason}\n")
            
            input("Press ENTER to start simulation...")
            run_same_track_simulation(t1, t2, priority_train, reduced_train, reduced_speed, reason)
        
        elif choice == "2":
            # Departure Delay
            print("\n--- DEPARTURE DELAY CONFLICT ---")
            delayed_id = input("Enter Departure Delayed Train ID: ").strip()
            delayed_train = get_train(delayed_id)
            
            if delayed_train is None:
                continue
            
            upcoming_id = input("Enter Upcoming Train ID: ").strip()
            upcoming_train = get_train(upcoming_id)
            
            if upcoming_train is None:
                continue
            
            # Determine mode based on train type
            if upcoming_train["train_type"] in ["Express", "Goods"]:
                mode = "loop"
                print(f"\n🚦 DECISION: {upcoming_train['train_type']} train diverted to loop line")
            else:
                mode = "reduced"
                print(f"\n🚦 DECISION: Passenger train reduced speed to {int(upcoming_train['max_speed'] * 0.6)} km/h")
            
            input("Press ENTER to start simulation...")
            run_departure_delay_simulation(delayed_train, upcoming_train, mode)
        
        elif choice == "3":
            print("\n👋 Exiting Railway Traffic Control System")
            pygame.quit()
            sys.exit()
        
        else:
            print("\n❌ Invalid choice. Please select 1-3.")

# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted. Exiting...")
        pygame.quit()
        sys.exit()