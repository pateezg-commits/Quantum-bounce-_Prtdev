import pygame
import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# --- QUANTUM ENGINE ---
def get_quantum_boost():
    """Returns True if the Quantum Circuit results in a '1' (Superposition collapse)"""
    try:
        qc = QuantumCircuit(1, 1)
        qc.h(0)  # Put qubit in 50/50 superposition
        qc.measure(0, 0)
        
        sim = AerSimulator()
        result = sim.run(qc, shots=1).result()
        counts = result.get_counts()
        return '1' in counts
    except Exception:
        # Fallback if Qiskit isn't fully loaded yet
        return random.choice([True, False])

# --- GAME SETUP ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Bounce")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Colors
WHITE = (255, 255, 255)
CYAN = (0, 255, 255) # "Quantum" color
BLACK = (0, 0, 0)

# Game Objects
ball = pygame.Rect(WIDTH//2, HEIGHT//2, 20, 20)
paddle = pygame.Rect(WIDTH//2 - 50, HEIGHT - 30, 100, 15)
ball_speed = [5, 5]
score = 0
last_bounce_quantum = False

# --- MAIN LOOP ---
running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Paddle Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= 8
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += 8

    # 2. Ball Movement
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # 3. Wall Collisions
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed[0] = -ball_speed[0]
    if ball.top <= 0:
        ball_speed[1] = -ball_speed[1]

    # 4. Paddle Collision (The Quantum Moment!)
    if ball.colliderect(paddle):
        ball_speed[1] = -abs(ball_speed[1]) # Bounce up
        score += 1
        
        # Trigger the Quantum Circuit
     # --- QUANTUM ENGINE (ENTANGLEMENT) ---
def get_entangled_states():
    """Returns two bits that are always the same (Entangled)"""
    qc = QuantumCircuit(2, 2)
    qc.h(0)           # Superposition on Qubit 0
    qc.cx(0, 1)       # Entangle Qubit 0 and Qubit 1
    qc.measure([0, 1], [0, 1])
    
    sim = AerSimulator()
    result = sim.run(qc, shots=1).result()
    counts = result.get_counts()
    
    # Get the measurement string, e.g., '11' or '00'
    outcome = list(counts.keys())[0] 
    return int(outcome[0]), int(outcome[1])

# --- GAME SETUP ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Ball 1 (The Leader) and Ball 2 (The Entangled Ghost)
ball1 = pygame.Rect(WIDTH//4, 100, 20, 20)
ball2 = pygame.Rect(3*WIDTH//4, 100, 20, 20)
paddle = pygame.Rect(WIDTH//2 - 60, HEIGHT - 30, 120, 15)

speed1 = [4, 4]
speed2 = [-4, 4] # Starts moving opposite
score = 0

running = True
while running:
    screen.fill((10, 10, 30)) # Dark space blue
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # Paddle Movement
    mx, _ = pygame.mouse.get_pos() # Use mouse for easier control
    paddle.centerx = mx

    # Move both balls
    ball1.x += speed1[0]; ball1.y += speed1[1]
    ball2.x += speed2[0]; ball2.y += speed2[1]

    # Wall Bounces
    for b, s in [(ball1, speed1), (ball2, speed2)]:
        if b.left <= 0 or b.right >= WIDTH: s[0] *= -1
        if b.top <= 0: s[1] *= -1

    # ENTANGLED COLLISION
    # If EITHER ball hits the paddle, both are affected by the Quantum Circuit
    if ball1.colliderect(paddle) or ball2.colliderect(paddle):
        bit1, bit2 = get_entangled_states()
        score += 1
        
        # If bit is 1, that ball reverses direction immediately
        if bit1 == 1: speed1[1] = -abs(speed1[1])
        else: speed1[1] = abs(speed1[1]) # Force it down (punishment!)

        if bit2 == 1: speed2[1] = -abs(speed2[1])
        else: speed2[1] = abs(speed2[1])

    # Game Over
    if ball1.bottom > HEIGHT or ball2.bottom > HEIGHT:
        print(f"Quantum Decoherence! Final Score: {score}")
        running = False

    # Draw
    pygame.draw.rect(screen, (255, 255, 255), paddle)
    pygame.draw.ellipse(screen, (0, 255, 255), ball1) # Cyan
    pygame.draw.ellipse(screen, (255, 0, 255), ball2) # Magenta
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()