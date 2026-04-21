import serial
import serial.tools.list_ports
import pygame
import random
import time
import sys

# ── Config ──────────────────────────────────────────────────
PORT = "COM3"        # Windows: COM3/COM4 etc. | Mac/Linux: /dev/ttyUSB0
BAUD = 115200
WIDTH, HEIGHT = 800, 600

# ── Colors ──────────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
BG      = (30,  30,  50)
GREEN   = (80,  200, 120)
RED     = (220, 80,  80)
YELLOW  = (240, 200, 60)
BLUE    = (80,  140, 220)

GESTURES = ["ROCK", "PAPER", "SCISSORS"]

EMOJI = {
    "ROCK":     "✊",
    "PAPER":    "✋",
    "SCISSORS": "✌️",
}

def determine_winner(player, computer):
    if player == computer:
        return "DRAW"
    wins = {("ROCK","SCISSORS"), ("SCISSORS","PAPER"), ("PAPER","ROCK")}
    return "WIN" if (player, computer) in wins else "LOSE"

# ── Mock Serial (no ESP32 needed for now) ────────────────────
class MockSerial:
    in_waiting = 0
    def readline(self): return b""
    def close(self): pass

ser = MockSerial()

# ── Uncomment below and comment MockSerial when ESP32 is ready ──
# try:
#     ser = serial.Serial(PORT, BAUD, timeout=1)
#     time.sleep(2)
#     print(f"Connected to {PORT}")
# except Exception as e:
#     print(f"Serial error: {e}")
#     print("Available ports:", [p.device for p in serial.tools.list_ports.comports()])
#     sys.exit()

# ── Pygame Setup ─────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors – Glove Edition")
font_xl  = pygame.font.SysFont("segoeui", 90)
font_lg  = pygame.font.SysFont("segoeui", 60)
font_md  = pygame.font.SysFont("segoeui", 36)
font_sm  = pygame.font.SysFont("segoeui", 26)
clock    = pygame.time.Clock()

# ── Game State ───────────────────────────────────────────────
player_gesture   = None
computer_gesture = None
result           = None
score            = {"WIN": 0, "LOSE": 0, "DRAW": 0}
state            = "WAITING"

def draw_centered(text, font, color, y, surface=screen):
    surf = font.render(text, True, color)
    surface.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

def draw_screen():
    screen.fill(BG)

    draw_centered("Rock  Paper  Scissors", font_md, BLUE, 20)

    score_text = f"  Wins: {score['WIN']}   Losses: {score['LOSE']}   Draws: {score['DRAW']}  "
    draw_centered(score_text, font_sm, WHITE, 65)

    pygame.draw.line(screen, BLUE, (50, 100), (750, 100), 2)

    if state == "WAITING":
        draw_centered("Make your gesture!", font_md, YELLOW, 200)
        draw_centered("Press R = Rock  |  P = Paper  |  S = Scissors", font_sm, WHITE, 260)
        draw_centered("✊   ✋   ✌️", font_xl, WHITE, 320)

    elif state == "RESULT":
        draw_centered("YOU", font_sm, GREEN, 120)
        draw_centered(EMOJI.get(player_gesture, "?"), font_xl, GREEN, 150)
        draw_centered(player_gesture or "", font_md, GREEN, 260)

        draw_centered("VS", font_lg, WHITE, 190)

        comp_label = font_sm.render("COMPUTER", True, RED)
        screen.blit(comp_label, (520, 120))
        comp_emoji = font_xl.render(EMOJI.get(computer_gesture, "?"), True, RED)
        screen.blit(comp_emoji, (530, 150))
        comp_name = font_md.render(computer_gesture or "", True, RED)
        screen.blit(comp_name, (530, 260))

        if result == "WIN":
            color, msg = GREEN,  "You Win!"
        elif result == "LOSE":
            color, msg = RED,    "You Lose!"
        else:
            color, msg = YELLOW, "Draw!"

        pygame.draw.rect(screen, color, (150, 320, 500, 70), border_radius=12)
        result_surf = font_lg.render(msg, True, BLACK)
        screen.blit(result_surf, (WIDTH//2 - result_surf.get_width()//2, 330))

        draw_centered("Press R / P / S to play again", font_sm, WHITE, 420)

    pygame.display.flip()

# ── Main Loop ────────────────────────────────────────────────
print("Game started! Press R, P, or S to play.")

while True:
    line = ""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ser.close()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ser.close()
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_r:
                line = "ROCK"
            elif event.key == pygame.K_p:
                line = "PAPER"
            elif event.key == pygame.K_s:
                line = "SCISSORS"

    # Handle keyboard input
    if line in GESTURES:
        player_gesture   = line
        computer_gesture = random.choice(GESTURES)
        result           = determine_winner(player_gesture, computer_gesture)
        score[result]   += 1
        state            = "RESULT"
        print(f"Player: {player_gesture} | CPU: {computer_gesture} | {result}")

    # Handle real ESP32 serial input (active when ESP32 is connected)
    if ser.in_waiting:
        try:
            serial_line = ser.readline().decode("utf-8").strip().upper()
            if serial_line in GESTURES:
                player_gesture   = serial_line
                computer_gesture = random.choice(GESTURES)
                result           = determine_winner(player_gesture, computer_gesture)
                score[result]   += 1
                state            = "RESULT"
                print(f"Player: {player_gesture} | CPU: {computer_gesture} | {result}")
        except Exception as e:
            print(f"Read error: {e}")

    draw_screen()
    clock.tick(30)