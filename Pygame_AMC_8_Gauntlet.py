import pygame
import random
import time

# --- Pygame Initialization ---
pygame.init()

# --- Screen Dimensions and Setup ---
screen_width = 1000  # Increased width for better layout
screen_height = 700  # Increased height
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("AMC 8 Gauntlet")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
LIGHT_GREEN = (0, 255, 0)
RED = (200, 0, 0)
LIGHT_RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (50, 50, 200)
LIGHT_BLUE = (100, 100, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# --- Fonts ---
font_xlarge = pygame.font.Font(None, 72) # For titles
font_large = pygame.font.Font(None, 48) # For main text, questions
font_medium = pygame.font.Font(None, 32) # For status, instructions
font_small = pygame.font.Font(None, 24) # For small labels, details

# --- Game States ---
MENU = 0
GET_NAME = 1
GAME_BOARD = 2
CHALLENGE_SCREEN = 3
WIN_SCREEN = 4
game_state = MENU

# --- Global Variables ---
player = None
challenges = []
current_challenge = None
player_answer_input = "" # Stores what player types
feedback_message = "" # For correct/incorrect messages
feedback_timer = 0 # To control how long feedback message is shown
ANSWER_BOX_ACTIVE = False # To check if the answer box is clicked for input

# --- Classes ---
class Challenge:
    def __init__(self, level, topic, question, answer, skill_token, difficulty="medium"):
        self.level = level
        self.topic = topic
        self.question = question
        self.answer = str(answer) # Store answer as string for consistent comparison
        self.skill_token = skill_token
        self.difficulty = difficulty

    def display_question(self, surface):
        # Render topic
        topic_text = font_medium.render(f"Topic: {self.topic}", True, BLACK)
        topic_rect = topic_text.get_rect(centerx=screen_width // 2, y=50)
        surface.blit(topic_text, topic_rect)

        # Render question - split into lines if too long
        words = self.question.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font_large.size(test_line)[0] > screen_width - 100: # Check width
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        lines.append(' '.join(current_line)) # Add the last line

        y_offset = 150
        for line in lines:
            question_text = font_large.render(line, True, BLACK)
            question_rect = question_text.get_rect(centerx=screen_width // 2, y=y_offset)
            surface.blit(question_text, question_rect)
            y_offset += 40 # Line spacing

class Player:
    def __init__(self, name):
        self.name = name
        self.current_level_idx = 0 # Index in the levels list
        self.skill_tokens = {} # e.g., {'Number Sense Navigator': 3}
        self.power_ups = {"Hint Helper": 1, "Double Check": 1} # Start with some power-ups
        self.level_progress = {level: False for level in LEVELS} # Track if a level is "completed"

    def get_current_level_name(self):
        return LEVELS[self.current_level_idx]

    def add_skill_token(self, token_name):
        self.skill_tokens[token_name] = self.skill_tokens.get(token_name, 0) + 1

    def use_power_up(self, power_up_name):
        if self.power_ups.get(power_up_name, 0) > 0:
            self.power_ups[power_up_name] -= 1
            return True
        return False

# --- Game Data ---
LEVELS = [
    "Number Theory Nexus",
    "Geometry Gymnasium",
    "Algebra Arena",
    "Counting & Probability Citadel",
    "Problem-Solving Pinnacle"
]

LEVEL_LOCATIONS = {
    "Number Theory Nexus": pygame.Rect(100, 100, 250, 100),
    "Geometry Gymnasium": pygame.Rect(400, 100, 250, 100),
    "Algebra Arena": pygame.Rect(700, 100, 250, 100),
    "Counting & Probability Citadel": pygame.Rect(250, 300, 250, 100),
    "Problem-Solving Pinnacle": pygame.Rect(550, 300, 250, 100),
}

# --- Functions ---
def create_all_challenges():
    all_challenges = [
        # Level A: Number Theory Nexus
        Challenge("Number Theory Nexus", "Advanced Divisibility", "What is the largest prime factor of 255?", 17, "Number Sense Navigator", "hard"),
        Challenge("Number Theory Nexus", "Modular Arithmetic", "What is the remainder when 50 is divided by 7?", 1, "Number Sense Navigator"),
        Challenge("Number Theory Nexus", "Prime Factorization", "How many positive integer divisors does 36 have?", 9, "Number Sense Navigator"),
        Challenge("Number Theory Nexus", "LCM/GCD", "What is the LCM of 12 and 18?", 36, "Number Sense Navigator"),

        # Level B: Geometry Gymnasium
        Challenge("Geometry Gymnasium", "Area & Perimeter", "A square has a perimeter of 28 units. What is its area?", 49, "Geometric Intuition"),
        Challenge("Geometry Gymnasium", "Angle Chasing", "Two angles are supplementary. One angle is 3 times the other. What is the measure of the smaller angle?", 45, "Geometric Intuition"),
        Challenge("Geometry Gymnasium", "Pythagorean Theorem", "A right triangle has legs of length 6 and 8. What is the length of the hypotenuse?", 10, "Geometric Intuition"),
        Challenge("Geometry Gymnasium", "Circles", "A circle has a diameter of 10. What is its circumference in terms of pi?", "10pi", "Geometric Intuition"), # Accept '10pi'

        # Level C: Algebra Arena
        Challenge("Algebra Arena", "Linear Equations", "Solve for x: 3x - 7 = 14", 7, "Algebra Alchemist"),
        Challenge("Algebra Arena", "Inequalities", "Which integer satisfies: 2x + 1 < 9 and x > 2?", 3, "Algebra Alchemist"),
        Challenge("Algebra Arena", "Word Problems", "If a shirt costs $20 and is on sale for 15% off, what is the new price?", 17, "Algebra Alchemist"),
        Challenge("Algebra Arena", "Expressions", "Evaluate 4a - 2b when a = 5 and b = 3.", 14, "Algebra Alchemist"),

        # Level D: Counting & Probability Citadel
        Challenge("Counting & Probability Citadel", "Counting", "How many different ways can 5 distinct books be arranged on a shelf?", 120, "Combinatorics Commander"),
        Challenge("Counting & Probability Citadel", "Probability", "What is the probability of rolling an even number on a standard 6-sided die?", "1/2", "Probability Prophet"), # Accept '1/2'
        Challenge("Counting & Probability Citadel", "Combinations", "How many distinct 2-digit numbers can be formed using digits 1, 2, 3, 4 without repetition?", 12, "Combinatorics Commander"),
        Challenge("Counting & Probability Citadel", "Probability", "If you flip a coin twice, what is the probability of getting two heads?", "1/4", "Probability Prophet"),

        # Level E: Problem-Solving Pinnacle (Mixed)
        Challenge("Problem-Solving Pinnacle", "Mixed", "A car travels at 60 mph for 30 minutes. How many miles does it travel?", 30, "Math Champion"),
        Challenge("Problem-Solving Pinnacle", "Mixed", "What is the value of 1/2 + 1/4 + 1/8?", "7/8", "Math Champion"),
        Challenge("Problem-Solving Pinnacle", "Mixed", "If a store buys an item for $50 and sells it for $75, what is the percent profit?", 50, "Math Champion"),
        Challenge("Problem-Solving Pinnacle", "Mixed", "The average of 5 numbers is 10. If four of the numbers are 8, 12, 9, 11, what is the fifth number?", 10, "Math Champion"),
    ]
    # Shuffle challenges within each level
    shuffled_challenges = []
    for level_name in LEVELS:
        level_specific_challenges = [c for c in all_challenges if c.level == level_name]
        random.shuffle(level_specific_challenges)
        shuffled_challenges.extend(level_specific_challenges)
    return shuffled_challenges


def draw_button(surface, rect, text, font, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    current_color = hover_color if is_hovered else color
    pygame.draw.rect(surface, current_color, rect, border_radius=10)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return is_hovered # Return if hovered for click detection

def draw_input_box(surface, rect, text, font, active_color, inactive_color, is_active):
    color = active_color if is_active else inactive_color
    pygame.draw.rect(surface, color, rect, 2, border_radius=5) # Border
    pygame.draw.rect(surface, WHITE, rect.inflate(-2, -2), border_radius=5) # Fill
    text_surf = font.render(text, True, BLACK)
    surface.blit(text_surf, (rect.x + 5, rect.y + 5))
    # Make sure cursor is always visible if active
    if is_active:
        cursor_pos = text_surf.get_width() + rect.x + 7
        pygame.draw.line(surface, BLACK, (cursor_pos, rect.y + 5), (cursor_pos, rect.y + rect.height - 5), 2)


# --- Game State Drawing Functions ---
def draw_menu():
    screen.fill(LIGHT_BLUE)
    title_text = font_xlarge.render("AMC 8 Gauntlet", True, BLACK)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(title_text, title_rect)

    start_text = font_large.render("Press SPACE to Start", True, BLACK)
    start_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(start_text, start_rect)

def draw_get_name():
    screen.fill(LIGHT_BLUE)
    prompt_text = font_large.render("Enter your name, Math Adventurer:", True, BLACK)
    prompt_rect = prompt_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(prompt_text, prompt_rect)

    name_box_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 300, 50)
    draw_input_box(screen, name_box_rect, player_answer_input, font_large, BLUE, DARK_GRAY, ANSWER_BOX_ACTIVE)

    instruction_text = font_small.render("Press ENTER to confirm", True, DARK_GRAY)
    instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height // 2 + 70))
    screen.blit(instruction_text, instruction_rect)


def draw_game_board():
    screen.fill(GRAY)

    # Player Info Panel
    pygame.draw.rect(screen, WHITE, (10, 10, screen_width - 20, 60), border_radius=10)
    player_name_text = font_medium.render(f"Player: {player.name}", True, BLACK)
    screen.blit(player_name_text, (20, 20))
    level_text = font_medium.render(f"Current Level: {player.get_current_level_name()}", True, BLACK)
    screen.blit(level_text, (200, 20))

    # Skill Tokens
    skill_token_text = font_medium.render("Skills:", True, BLACK)
    screen.blit(skill_token_text, (450, 20))
    x_offset = 530
    for token, count in player.skill_tokens.items():
        token_surf = font_small.render(f"{token}: {count}", True, BLACK)
        screen.blit(token_surf, (x_offset, 25))
        x_offset += token_surf.get_width() + 15

    # Level Zones
    for level_name, rect in LEVEL_LOCATIONS.items():
        color = GREEN if player.level_progress[level_name] else BLUE
        hover_color = LIGHT_GREEN if player.level_progress[level_name] else LIGHT_BLUE
        is_current_level = level_name == player.get_current_level_name()

        # Draw Level Box
        pygame.draw.rect(screen, hover_color if rect.collidepoint(pygame.mouse.get_pos()) else color, rect, border_radius=15)
        pygame.draw.rect(screen, BLACK, rect, 3, border_radius=15) # Border

        # Level Name
        level_text_surf = font_large.render(level_name, True, BLACK)
        level_text_rect = level_text_surf.get_rect(center=rect.center)
        screen.blit(level_text_surf, level_text_rect)

        # Indicate current level
        if is_current_level:
            arrow_text = font_xlarge.render(">", True, RED)
            arrow_rect = arrow_text.get_rect(midright=(rect.left - 10, rect.centery))
            screen.blit(arrow_text, arrow_rect)


    # Power-Up Buttons (Conceptual)
    hint_rect = pygame.Rect(screen_width - 150, screen_height - 100, 120, 40)
    double_check_rect = pygame.Rect(screen_width - 150, screen_height - 50, 120, 40)

    hint_text = f"Hint ({player.power_ups['Hint Helper']})"
    double_check_text = f"2x Check ({player.power_ups['Double Check']})"

    draw_button(screen, hint_rect, hint_text, font_small, DARK_GRAY, GRAY)
    draw_button(screen, double_check_rect, double_check_text, font_small, DARK_GRAY, GRAY)

    # Next Level Button
    if player.get_current_level_name() != LEVELS[-1]: # Not the last level
        next_level_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 80, 150, 50)
        if draw_button(screen, next_level_rect, "Next Level", font_medium, GREEN, LIGHT_GREEN):
            return "next_level_clicked" # Signal to caller


def draw_challenge_screen():
    screen.fill(YELLOW)

    if current_challenge:
        current_challenge.display_question(screen)

        # Answer Input Box
        answer_box_rect = pygame.Rect(screen_width // 2 - 200, screen_height - 150, 400, 50)
        draw_input_box(screen, answer_box_rect, player_answer_input, font_large, BLUE, DARK_GRAY, ANSWER_BOX_ACTIVE)

        # Submit Button
        submit_button_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 80, 150, 50)
        draw_button(screen, submit_button_rect, "Submit", font_large, GREEN, LIGHT_GREEN)

        # Feedback Message
        if feedback_message:
            feedback_text_surf = font_large.render(feedback_message, True, RED if "Incorrect" in feedback_message else GREEN)
            feedback_text_rect = feedback_text_surf.get_rect(center=(screen_width // 2, screen_height - 250))
            screen.blit(feedback_text_surf, feedback_text_rect)
    else:
        # This state should ideally not be reached if challenges are managed correctly
        temp_text = font_large.render("Loading Challenge...", True, BLACK)
        temp_rect = temp_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(temp_text, temp_rect)

def draw_win_screen():
    screen.fill(GREEN)
    win_text = font_xlarge.render(f"Congratulations, {player.name}!", True, BLACK)
    win_rect = win_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(win_text, win_rect)

    champion_text = font_large.render("You are a Math Champion!", True, BLACK)
    champion_rect = champion_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(champion_text, champion_rect)

    # Display final skill tokens
    skills_title = font_medium.render("Your Mastered Skills:", True, BLACK)
    skills_title_rect = skills_title.get_rect(center=(screen_width // 2, screen_height // 2 + 80))
    screen.blit(skills_title, skills_title_rect)

    y_offset = screen_height // 2 + 120
    for token, count in player.skill_tokens.items():
        skill_line = font_small.render(f"- {token}: {count} points", True, BLACK)
        skill_line_rect = skill_line.get_rect(center=(screen_width // 2, y_offset))
        screen.blit(skill_line, skill_line_rect)
        y_offset += 30


# --- Main Game Loop ---
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Event Handling based on Game State ---
        if game_state == MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = GET_NAME
                player_answer_input = "" # Clear input for name
                ANSWER_BOX_ACTIVE = True # Make input box active for name

        elif game_state == GET_NAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                name_box_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 300, 50)
                if name_box_rect.collidepoint(event.pos):
                    ANSWER_BOX_ACTIVE = True
                else:
                    ANSWER_BOX_ACTIVE = False
            if event.type == pygame.KEYDOWN and ANSWER_BOX_ACTIVE:
                if event.key == pygame.K_RETURN:
                    if player_answer_input.strip(): # Ensure name is not empty
                        player = Player(player_answer_input.strip())
                        challenges = create_all_challenges() # Initialize challenges once player exists
                        game_state = GAME_BOARD
                        ANSWER_BOX_ACTIVE = False
                    else:
                        print("Please enter a name!") # Placeholder feedback
                elif event.key == pygame.K_BACKSPACE:
                    player_answer_input = player_answer_input[:-1]
                else:
                    player_answer_input += event.unicode

        elif game_state == GAME_BOARD:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Check level clicks
                for level_name, rect in LEVEL_LOCATIONS.items():
                    if rect.collidepoint(mouse_pos) and level_name == player.get_current_level_name():
                        # Only allow clicking current level to start a challenge
                        selected_level_challenges = [c for c in challenges if c.level == level_name and c not in player.completed_challenges] # Needs tracking of completed challenges
                        # For simplicity here, we'll just pick from any for that level.
                        # In a full game, you'd track challenges already solved for a level.
                        available_challenges_for_current_level = [c for c in challenges if c.level == player.get_current_level_name()]
                        if available_challenges_for_current_level:
                            current_challenge = random.choice(available_challenges_for_current_level)
                            game_state = CHALLENGE_SCREEN
                            player_answer_input = ""
                            feedback_message = ""
                            ANSWER_BOX_ACTIVE = True # Activate input box for challenge

                # Check Next Level button click
                next_level_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 80, 150, 50)
                if next_level_rect.collidepoint(mouse_pos) and player.get_current_level_name() != LEVELS[-1]:
                    player.current_level_idx += 1
                    if player.current_level_idx >= len(LEVELS): # Check if all levels completed
                        game_state = WIN_SCREEN
                    else:
                        player.level_progress[LEVELS[player.current_level_idx-1]] = True # Mark previous level as complete
                        # Reset challenges if needed or manage specific level progress
                        # For now, just allow moving to next level.

        elif game_state == CHALLENGE_SCREEN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                answer_box_rect = pygame.Rect(screen_width // 2 - 200, screen_height - 150, 400, 50)
                submit_button_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 80, 150, 50)

                if answer_box_rect.collidepoint(event.pos):
                    ANSWER_BOX_ACTIVE = True
                else:
                    ANSWER_BOX_ACTIVE = False

                if submit_button_rect.collidepoint(event.pos):
                    if current_challenge:
                        is_correct = False
                        try:
                            # Attempt to evaluate if it's a numeric expression
                            evaluated_player_answer = str(eval(player_answer_input.replace('^', '**').replace('pi', str(3.14159)))) # Basic pi handling
                            if evaluated_player_answer == current_challenge.answer:
                                is_correct = True
                            else:
                                # Also check direct string comparison for "1/2", "10pi" etc.
                                if player_answer_input.lower().strip() == current_challenge.answer.lower().strip():
                                    is_correct = True
                        except (NameError, SyntaxError, TypeError):
                            # Fallback to direct string comparison if eval fails
                            if player_answer_input.lower().strip() == current_challenge.answer.lower().strip():
                                is_correct = True


                        if is_correct:
                            feedback_message = "Correct!"
                            player.add_skill_token(current_challenge.skill_token)
                        else:
                            feedback_message = f"Incorrect. Answer was: {current_challenge.answer}"
                        feedback_timer = pygame.time.get_ticks() # Start feedback timer

                        # After feedback, transition back to game board
                        # We'll transition after a short delay
                        # For now, immediate transition for simplicity
                        game_state = GAME_BOARD
                        ANSWER_BOX_ACTIVE = False
                        current_challenge = None # Clear current challenge

            if event.type == pygame.KEYDOWN and ANSWER_BOX_ACTIVE:
                if event.key == pygame.K_RETURN:
                    # Submit on Enter key if input box is active (handled by button click logic above)
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    player_answer_input = player_answer_input[:-1]
                else:
                    player_answer_input += event.unicode
                    
        elif game_state == WIN_SCREEN:
            # Maybe a restart button here?
            pass


    # --- Drawing ---
    screen.fill(WHITE) # Clear screen each frame

    if game_state == MENU:
        draw_menu()
    elif game_state == GET_NAME:
        draw_get_name()
    elif game_state == GAME_BOARD:
        draw_game_board()
    elif game_state == CHALLENGE_SCREEN:
        draw_challenge_screen()
    elif game_state == WIN_SCREEN:
        draw_win_screen()


    # Update feedback message display time
    if feedback_message and pygame.time.get_ticks() - feedback_timer > 2000: # Display for 2 seconds
        feedback_message = ""

    pygame.display.flip() # Update the full display Surface to the screen
    clock.tick(60) # Limit frame rate to 60 FPS

pygame.quit()