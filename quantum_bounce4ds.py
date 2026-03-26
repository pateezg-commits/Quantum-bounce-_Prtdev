import pygame
import sys
import random
import os
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileProgram, compileShader
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# --- 1. SYSTEMS & DATA ---
sim = AerSimulator()
HS_FILE = "quantum_high.txt"

def get_rank(score):
    if score < 10: return "NOVICE OBSERVER"
    if score < 25: return "WAVEFUNCTION COLLAPSER"
    if score < 50: return "ENTANGLEMENT MASTER"
    return "SINGULARITY GOD"

def load_hs():
    if os.path.exists(HS_FILE):
        try:
            with open(HS_FILE, "r") as f: return int(f.read())
        except: return 0
    return 0

def save_hs(score):
    if score > load_hs():
        with open(HS_FILE, "w") as f: f.write(str(score))

# --- 2. GPU SHADERS ---
VERTEX_SHADER = """
#version 120
varying vec3 vNormal;
varying vec3 vFragPos;
void main() {
    vFragPos = vec3(gl_ModelViewMatrix * gl_Vertex);
    vNormal = gl_NormalMatrix * gl_Normal;
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
"""

FRAGMENT_SHADER = """
#version 120
varying vec3 vNormal;
varying vec3 vFragPos;
uniform vec3 objCol;
uniform float time;
uniform float glow;
uniform float vib;
uniform float alpha;
void main() {
    float pulse = (sin(time * 10.0) + 1.0) * 0.5 * glow;
    vec3 lightDir = normalize(vec3(5.0, 10.0, 5.0) - vFragPos);
    float diff = max(dot(normalize(vNormal), lightDir), 0.0);
    float noise = fract(sin(dot(vFragPos.xy, vec2(12.989, 78.233))) * 43.58) * vib;
    vec3 color = (objCol * (0.6 + diff)) + vec3(pulse * 0.2) + vec3(noise);
    gl_FragColor = vec4(color, alpha);
}
"""

# --- 3. RENDERING HELPERS ---
def draw_text(x, y, text, color=(0, 255, 200), center=False):
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    text_surface = font.render(text, True, color)
    if center: x -= text_surface.get_width() // 2
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glEnable(GL_DEPTH_TEST)

def draw_cube(size_vec):
    sx, sy, sz = size_vec
    glBegin(GL_QUADS)
    glNormal3f(0,0,1); glVertex3f(-sx,-sy,sz); glVertex3f(sx,-sy,sz); glVertex3f(sx,sy,sz); glVertex3f(-sx,sy,sz)
    glNormal3f(0,0,-1); glVertex3f(-sx,-sy,-sz); glVertex3f(-sx,sy,-sz); glVertex3f(sx,sy,-sz); glVertex3f(sx,-sy,-sz)
    glNormal3f(0,1,0); glVertex3f(-sx,sy,-sz); glVertex3f(-sx,sy,sz); glVertex3f(sx,sy,sz); glVertex3f(sx,sy,-sz)
    glNormal3f(-1,0,0); glVertex3f(-sx,-sy,-sz); glVertex3f(-sx,-sy,sz); glVertex3f(-sx,sy,sz); glVertex3f(-sx,sy,-sz)
    glNormal3f(1,0,0); glVertex3f(sx,-sy,-sz); glVertex3f(sx,sy,-sz); glVertex3f(sx,sy,sz); glVertex3f(sx,-sy,sz)
    glEnd()

# --- 4. INITIALIZATION ---
pygame.init()
W, H = 800, 600
pygame.display.set_mode((W, H), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Quantum Bounce by Prt Dev")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 22, bold=True)
title_font = pygame.font.SysFont("Consolas", 48, bold=True)

try:
    shader = compileProgram(compileShader(VERTEX_SHADER, GL_VERTEX_SHADER), compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))
    u_vars = {n: glGetUniformLocation(shader, n) for n in ["objCol", "time", "glow", "vib", "alpha"]}
except: shader = None

glEnable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def reset_game():
    # Generate 100 stars in 3D space
    stars = [[random.uniform(-40, 40), random.uniform(-30, 30), random.uniform(-60, 10)] for _ in range(150)]
    return {
        "state": "MENU", "score": 0, "high": load_hs(), "stability": 0.0, "shake": 0.0,
        "stars": stars,
        "b1": {"pos": [-4.0, 5.0, 0.0], "speed": [0.14, 0.20], "real": True},
        "b2": {"pos": [4.0, 5.0, 0.0], "speed": [-0.14, -0.20], "real": False},
        "paddle": {"pos": [0, -8, 0], "size": [4.0, 0.4, 2.0], "real": True}
    }

g = reset_game()

# --- 5. MAIN LOOP ---
while True:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    t = pygame.time.get_ticks() / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT: pygame.quit(); sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if g["state"] in ["MENU", "DEAD"]:
                # Check if clicking near the SPAWN center
                h = g["high"]; g = reset_game(); g["high"] = h; g["state"] = "PLAY"
        if event.type == KEYDOWN:
            if event.key == K_SPACE and g["state"] == "PLAY":
                 g['paddle']['real'] = not g['paddle']['real']

    # --- 3D RENDERING ---
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(45, (W/H), 0.1, 150.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    glTranslatef(random.uniform(-g['shake'], g['shake']), random.uniform(-g['shake'], g['shake']), -40)
    g['shake'] *= 0.9

    if shader:
        glUseProgram(shader)
        glUniform1f(u_vars["time"], t)

        # 1. Background Stars (Parallax)
        for s in g['stars']:
            glUniform3f(u_vars["objCol"], 0.8, 0.9, 1.0)
            glUniform1f(u_vars["alpha"], 0.6); glUniform1f(u_vars["vib"], 0)
            glPushMatrix()
            # Stars move slowly toward the camera to simulate 3D travel
            s[2] += 0.05
            if s[2] > 10: s[2] = -60
            glTranslatef(s[0], s[1], s[2])
            draw_cube([0.05, 0.05, 0.05])
            glPopMatrix()

        if g["state"] == "PLAY":
            mx, my = pygame.mouse.get_pos()
            g['paddle']['pos'][0] = (mx - W/2) * 0.08
            g['paddle']['pos'][1] = -8 + (H/2 - my) * 0.04
            g['paddle']['pos'][2] = np.sin(t * 1.5) * (g['stability'] * 10.0)
            g['stability'] = min(1.0, g['stability'] + 0.0008)

            for ball_key in ['b1', 'b2']:
                b = g[ball_key]
                b['pos'][0] += b['speed'][0]; b['pos'][1] += b['speed'][1]
                b['pos'][2] = np.cos(t * 1.2 + (0 if b['real'] else 3.14)) * 5.0
                
                if abs(b['pos'][0]) > 18: b['speed'][0] *= -1
                if b['pos'][1] > 14: 
                    b['speed'][1] *= -1
                    g['b1']['real'], g['b2']['real'] = g['b2']['real'], g['b1']['real']
                    g['shake'] = 0.6

                p, ps = g['paddle']['pos'], g['paddle']['size']
                if abs(b['pos'][0] - p[0]) < ps[0] + 1.0 and abs(b['pos'][1] - p[1]) < ps[1] + 1.0 and abs(b['pos'][2] - p[2]) < ps[2] + 1.2:
                    if g['paddle']['real'] == b['real']:
                        g['score'] += 1; g['stability'] = max(0.0, g['stability'] - 0.25)
                        b['speed'][1] = abs(b['speed'][1]); b['pos'][1] = p[1] + 1.8
                        g['shake'] = 0.3

                if b['pos'][1] < -20:
                    if not b['real'] and g['stability'] < 0.2:
                        b['pos'][1] = 14; b['speed'][1] = -abs(b['speed'][1]); g['score'] += 5; g['shake'] = 1.2
                    else:
                        g["state"] = "DEAD"; save_hs(g["score"])

            # Draw Paddle
            p_col = (1, 1, 1) if g['paddle']['real'] else (0.4, 0.0, 0.8)
            glUniform3f(u_vars["objCol"], *p_col); glUniform1f(u_vars["alpha"], 1.0 if g['paddle']['real'] else 0.5)
            glPushMatrix(); glTranslatef(*g['paddle']['pos']); draw_cube(g['paddle']['size']); glPopMatrix()

            # Draw Balls
            for ball_key in ['b1', 'b2']:
                b = g[ball_key]; col = (0, 1, 1) if b['real'] else (1, 0, 1)
                glUniform3f(u_vars["objCol"], *col); glUniform1f(u_vars["alpha"], 1.0 if b['real'] else 0.4)
                glPushMatrix(); glTranslatef(*b['pos']); glRotatef(t*250, 1, 1, 1); draw_cube([0.7, 0.7, 0.7]); glPopMatrix()

        elif g["state"] == "MENU":
            glUniform3f(u_vars["objCol"], 0, 1, 0.5); glUniform1f(u_vars["alpha"], 0.8)
            glPushMatrix(); glRotatef(t*30, 0, 1, 0); draw_cube([5, 5, 5]); glPopMatrix()

        elif g["state"] == "DEAD":
            glUniform3f(u_vars["objCol"], 1, 0, 0); glUniform1f(u_vars["alpha"], 1.0)
            glPushMatrix(); glRotatef(t*180, 1, 1, 0); draw_cube([6, 0.5, 6]); glPopMatrix()

    # --- 2D OVERLAY ---
    glUseProgram(0)
    if g["state"] == "PLAY":
        draw_text(20, 560, f"SCORE: {g['score']}")
        draw_text(20, 530, f"PADDLE: {'SOLID' if g['paddle']['real'] else 'PHASED'}", (255, 255, 255))
        draw_text(20, 500, f"COHERENCE: {int((1-g['stability'])*100)}%")
    elif g["state"] == "MENU":
        draw_text(W//2, 450, "Quantum Bounce", (0, 255, 255), True)
        draw_text(W//2, 410, "by Prt Dev", (200, 200, 200), True)
        # Spawn Button Visual
        btn_col = (0, 255, 100) if (t * 2) % 2 > 1 else (0, 200, 80)
        draw_text(W//2, 280, "[ SPAWN ]", btn_col, True)
        draw_text(W//2, 100, f"MAX SINGULARITY: {g['high']}", (255, 215, 0), True)
    elif g["state"] == "DEAD":
        draw_text(W//2, 400, "SYSTEM DECOHERENCE", (255, 0, 0), True)
        draw_text(W//2, 350, f"FINAL RANK: {get_rank(g['score'])}", (255, 255, 255), True)
        draw_text(W//2, 250, "[ CLICK TO SPAWN ]", (255, 255, 255), True)

    pygame.display.flip(); clock.tick(60)