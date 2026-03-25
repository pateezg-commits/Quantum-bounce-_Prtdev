import pygame
import sys
import json
import os
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# --- FILE OPERATIONS ---
HIGH_SCORE_FILE = "high_scores.json"

def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_high_score(name, score):
    scores = load_high_scores()
    scores.append({"name": name if name else "Unknown Observer", "score": score})
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump(scores, f)

# --- QUANTUM ENGINE (3-QUBIT CIRCUIT) ---
def get_quantum_data():
    """
    Qubit 0 & 1: Entangled for Ball Bounce
    Qubit 2: Superposition for Paddle Glitch
    """
    try:
        qc = QuantumCircuit(3, 3)
        # Entangle Q0 and Q1
        qc.h(0)
        qc.cx(0, 1)
        # Superposition for Q2 (The Glitch)
        qc.h(2)
        
        qc.measure([0, 1, 2], [0, 1, 2])
        sim = AerSimulator()
        result = sim.run(qc, shots=1).result()
        outcome = list(result.get_counts().keys())[0] # String like '101'
        # Outcome is read right-to-left in Qiskit (q2, q1, q0)
        return int(outcome[2]), int(outcome[1]), int(outcome[0])
    except:
        import random
        return random.randint(0,1), random.randint(0,1), random.randint(0,1)

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Bounce by Prtdev")
clock = pygame.time.Clock()

# Fonts & Colors
title_font = pygame.font.SysFont("Courier New", 45, bold=True)
UI_font = pygame.font.SysFont("Arial", 26)
small_font = pygame.font.SysFont("Arial", 18)
CYAN, MAGENTA, WHITE = (0, 255, 255), (255, 0, 255), (255, 255, 255)
DARK_BLUE, GRAY, BLACK = (10, 10, 30), (50, 50, 50), (0, 0, 0)
GLITCH_COLOR = (0, 200, 100)

# Game Variables
player_name = ""
game_active = False
score = 0
ball1 = pygame.Rect(WIDTH//4, 100, 20, 20)
ball2 = pygame.Rect(3*WIDTH//4, 100, 20, 20)
# Paddle starts at 120 width
paddle = pygame.Rect(WIDTH//2 - 60, HEIGHT - 50, 120, 15)
speed1, speed2 = [5, 5], [-5, 5]
glitch_active = False

# --- MAIN LOOP ---
while True:
    screen.fill(DARK_BLUE)
    mx, my = pygame.mouse.get_pos()
    click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: click = True
        if event.type == pygame.KEYDOWN and not game_active:
            if event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
            elif event.key == pygame.K_RETURN and player_name:
                game_active = True
                score = 0
            else:
                if len(player_name) < 10: player_name += event.unicode

    if not game_active:
        # MENU CODE (Same as before)
        title_surf = title_font.render("QUANTUM BOUNCE", True, CYAN)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 50))
        
        # High Scores
        high_scores = load_high_scores()
        for i, entry in enumerate(high_scores):
            hs_text = small_font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE)
            screen.blit(hs_text, (WIDTH//2 - 130, 180 + (i * 22)))

        # Name Input & Button
        input_rect = pygame.Rect(WIDTH//2 - 150, 320, 300, 45)
        pygame.draw.rect(screen, GRAY, input_rect, border_radius=8)
        screen.blit(UI_font.render(f"Pilot: {player_name}", True, WHITE), (input_rect.x + 10, input_rect.y + 5))
        
        start_btn = pygame.Rect(WIDTH//2 - 75, 400, 150, 50)
        btn_col = CYAN if start_btn.collidepoint((mx, my)) else GRAY
        pygame.draw.rect(screen, btn_col, start_btn, border_radius=12)
        screen.blit(UI_font.render("START", True, BLACK), (start_btn.x+40, start_btn.y+10))

        if click and start_btn.collidepoint((mx, my)):
            paddle.width = 120 # Reset paddle
            score = 0
            game_active = True

    else:
        # --- GAMEPLAY ---
        paddle.centerx = mx
        ball1.x += speed1[0]; ball1.y += speed1[1]
        ball2.x += speed2[0]; ball2.y += speed2[1]

        for b, s in [(ball1, speed1), (ball2, speed2)]:
            if b.left <= 0 or b.right >= WIDTH: s[0] *= -1
            if b.top <= 0: s[1] *= -1

        # THE QUANTUM MOMENT
        if ball1.colliderect(paddle) or ball2.colliderect(paddle):
            b1, b2, glitch_bit = get_quantum_data()
            score += 1
            
            # Bounce Logic
            speed1[1] = -abs(speed1[1]) if b1 == 1 else abs(speed1[1])
            speed2[1] = -abs(speed2[1]) if b2 == 1 else abs(speed2[1])
            
            # PADDLE GLITCH LOGIC
            if glitch_bit == 1:
                paddle.width = 200 # Quantum Expansion
                glitch_active = True
            else:
                paddle.width = 60  # Quantum Contraction
                glitch_active = False

        if ball1.bottom > HEIGHT or ball2.bottom > HEIGHT:
            save_high_score(player_name, score)
            game_active = False

        # Drawing with Glitch visual
        paddle_color = GLITCH_COLOR if glitch_active else WHITE
        pygame.draw.rect(screen, paddle_color, paddle, border_radius=5)
        pygame.draw.ellipse(screen, CYAN, ball1)
        pygame.draw.ellipse(screen, MAGENTA, ball2)
        
        status = "EXPANDED" if glitch_active else "SHRUNK"
        screen.blit(small_font.render(f"Paddle State: {status}", True, paddle_color), (WIDTH-180, 20))
        screen.blit(UI_font.render(f"Score: {score}", True, WHITE), (20, 20))

    pygame.display.flip()
    clock.tick(60)