import pygame
import sys
import json
import os
import random
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

# --- QUANTUM ENGINE (4-QUBIT CIRCUIT) ---
def get_quantum_data():
    """
    Q0/Q1: Entanglement (Balls)
    Q2: Glitch (Paddle)
    Q3: Superposition (Invisibility)
    """
    try:
        qc = QuantumCircuit(4, 4)
        qc.h(0); qc.cx(0, 1) # Entangle
        qc.h(2)              # Paddle Glitch
        qc.h(3)              # Ball Superposition
        
        qc.measure([0,1,2,3], [0,1,2,3])
        sim = AerSimulator()
        result = sim.run(qc, shots=1).result()
        outcome = list(result.get_counts().keys())[0]
        # Qiskit outcome is bit-reversed: [q3, q2, q1, q0]
        return int(outcome[3]), int(outcome[2]), int(outcome[1]), int(outcome[0])
    except:
        return random.randint(0,1), random.randint(0,1), random.randint(0,1), random.randint(0,1)

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

# Game Variables
player_name = ""
game_active = False
score = 0
ball1 = pygame.Rect(WIDTH//4, 100, 20, 20)
ball2 = pygame.Rect(3*WIDTH//4, 100, 20, 20)
paddle = pygame.Rect(WIDTH//2 - 60, HEIGHT - 50, 120, 15)
speed1, speed2 = [5, 5], [-5, 5]

# Mode States
glitch_active = False
superposition_active = False # Controls invisibility

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
        if event.type == pygame.KEYDOWN:
            if not game_active:
                if event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
                else:
                    if len(player_name) < 10 and event.unicode.isprintable(): 
                        player_name += event.unicode

    if not game_active:
        # --- MENU ---
        title_surf = title_font.render("QUANTUM BOUNCE", True, CYAN)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 50))
        screen.blit(small_font.render("by Prtdev", True, MAGENTA), (WIDTH//2 - 40, 100))
        
        # High Scores Display
        high_scores = load_high_scores()
        for i, entry in enumerate(high_scores):
            hs_text = small_font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE)
            screen.blit(hs_text, (WIDTH//2 - 130, 180 + (i * 22)))

        # Name Input & Start Button
        input_rect = pygame.Rect(WIDTH//2 - 150, 320, 300, 45)
        pygame.draw.rect(screen, GRAY, input_rect, border_radius=8)
        screen.blit(UI_font.render(f"Pilot: {player_name}", True, WHITE), (input_rect.x + 10, input_rect.y + 5))
        
        start_btn = pygame.Rect(WIDTH//2 - 75, 400, 150, 50)
        btn_col = CYAN if start_btn.collidepoint((mx, my)) else GRAY
        pygame.draw.rect(screen, btn_col, start_btn, border_radius=12)
        screen.blit(UI_font.render("START", True, BLACK), (start_btn.x+40, start_btn.y+10))

        # START BUTTON FIX: Resetting all states
        if click and start_btn.collidepoint((mx, my)):
            ball1.center, ball2.center = (WIDTH//4, 100), (3*WIDTH//4, 100)
            speed1, speed2 = [5, 5], [-5, 5]
            paddle.width = 120
            score = 0
            superposition_active = False
            game_active = True

    else:
        # --- GAMEPLAY ---
        paddle.centerx = mx
        ball1.x += speed1[0]; ball1.y += speed1[1]
        ball2.x += speed2[0]; ball2.y += speed2[1]

        # Wall Collisions (Acts as the "Observer")
        for b, s in [(ball1, speed1), (ball2, speed2)]:
            if b.left <= 0 or b.right >= WIDTH or b.top <= 0:
                if b.left <= 0 or b.right >= WIDTH: s[0] *= -1
                if b.top <= 0: s[1] *= -1
                superposition_active = False # Observation collapses the wave function

        # Quantum Collision
        if ball1.colliderect(paddle) or ball2.colliderect(paddle):
            s_bit, g_bit, b2_bit, b1_bit = get_quantum_data()
            score += 1
            
            # Ball Directions
            speed1[1] = -abs(speed1[1]) if b1_bit == 1 else abs(speed1[1])
            speed2[1] = -abs(speed2[1]) if b2_bit == 1 else abs(speed2[1])
            
            # Paddle Glitch
            paddle.width = 180 if g_bit == 1 else 70
            glitch_active = (g_bit == 1)
            
            # Superposition Mode (Invisibility)
            superposition_active = (s_bit == 1)

        # Game Over
        if ball1.bottom > HEIGHT or ball2.bottom > HEIGHT:
            save_high_score(player_name, score)
            game_active = False # Return to menu

        # Drawing logic
        pygame.draw.rect(screen, (0, 200, 100) if glitch_active else WHITE, paddle, border_radius=5)
        
        # Superposition Ball Effect
        if not superposition_active:
            pygame.draw.ellipse(screen, CYAN, ball1)
            pygame.draw.ellipse(screen, MAGENTA, ball2)
        else:
            # Draw faint ghost outlines instead of being totally invisible if you prefer
            pygame.draw.ellipse(screen, (40, 40, 80), ball1, 2)
            pygame.draw.ellipse(screen, (80, 40, 80), ball2, 2)
            screen.blit(small_font.render("SUPERPOSITION ACTIVE", True, (150, 0, 0)), (WIDTH//2 - 80, 20))

        screen.blit(UI_font.render(f"Score: {score}", True, WHITE), (20, 20))

    pygame.display.flip()
    clock.tick(60)
