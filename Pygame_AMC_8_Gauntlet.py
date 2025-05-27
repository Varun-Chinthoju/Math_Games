import pygame
import random
import time
from math import gcd, factorial
import re # Import regex for parsing

# --- Pygame Initialization ---
pygame.init()

# --- Screen Dimensions and Setup ---
screen_width = 1000
screen_height = 700
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
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128) # For hint button

# --- Fonts ---
font_xlarge = pygame.font.Font(None, 72)
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

# --- Game States ---
MENU = 0
GET_NAME = 1
GAME_BOARD = 2
CHALLENGE_SCREEN = 3
WIN_SCREEN = 4
game_state = MENU

# --- Global Variables ---
player = None
current_challenge = None
player_answer_input = ""
feedback_message = ""
hint_message = "" # To store the generated hint
feedback_timer = 0
ANSWER_BOX_ACTIVE = False
answer_submitted = False

# --- Classes ---
class Challenge:
    def __init__(self, level, topic, question, answer, skill_token, difficulty="medium"):
        self.level = level
        self.topic = topic
        self.question = question
        self.answer = str(answer)
        self.skill_token = skill_token
        self.difficulty = difficulty
        self.hint_given = False # New flag to track if hint has been given for this challenge

    def display_question(self, surface):
        topic_text = font_medium.render(f"Topic: {self.topic}", True, BLACK)
        topic_rect = topic_text.get_rect(centerx=screen_width // 2, y=50)
        surface.blit(topic_text, topic_rect)

        words = self.question.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font_large.size(test_line)[0] > screen_width - 100:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        lines.append(' '.join(current_line))

        y_offset = 150
        for line in lines:
            question_text = font_large.render(line, True, BLACK)
            question_rect = question_text.get_rect(centerx=screen_width // 2, y=y_offset)
            surface.blit(question_text, question_rect)
            y_offset += 40

class Player:
    def __init__(self, name):
        self.name = name
        self.current_level_idx = 0
        self.skill_tokens = {}
        self.power_ups = {"Hint Helper": 1, "Double Check": 1}
        self.level_progress = {level: False for level in LEVELS}
        self.correct_streak = 0

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
    "Number Theory Nexus": pygame.Rect(50, 150, 280, 100),
    "Geometry Gymnasium": pygame.Rect(360, 150, 280, 100),
    "Algebra Arena": pygame.Rect(670, 150, 280, 100),

    "Counting & Probability Citadel": pygame.Rect(180, 350, 330, 100),
    "Problem-Solving Pinnacle": pygame.Rect(540, 350, 280, 100),
}

# --- Dynamic Question Generation Functions ---

def generate_number_theory_challenge():
    q_type = random.choice(["divisibility", "prime", "gcd_lcm"])
    
    if q_type == "divisibility":
        num = random.randint(50, 300)
        divisor = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        question = f"What is the remainder when {num} is divided by {divisor}?"
        answer = num % divisor
        return Challenge("Number Theory Nexus", "Modular Arithmetic", question, answer, "Number Sense Navigator")
    
    elif q_type == "prime":
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        p = random.choice(primes[5:]) # Pick a prime from 13 onwards
        
        factor_count = random.randint(1, 3)
        composite_num = p
        for _ in range(factor_count):
            small_prime_factors = [pr for pr in primes if pr < p and pr <= 7]
            if small_prime_factors:
                composite_num *= random.choice(small_prime_factors)
            else:
                composite_num *= random.choice([2,3,5]) # Fallback for very small 'p'

        question = f"What is the largest prime factor of {composite_num}?"
        answer = p
        return Challenge("Number Theory Nexus", "Prime Factors", question, answer, "Number Sense Navigator")

    elif q_type == "gcd_lcm":
        a = random.randint(5, 20) * random.choice([2, 3, 5])
        b = random.randint(5, 20) * random.choice([2, 3, 5])
        
        op = random.choice(["GCD", "LCM"])
        if op == "GCD":
            question = f"What is the Greatest Common Divisor (GCD) of {a} and {b}?"
            answer = gcd(a, b)
        else:
            question = f"What is the Least Common Multiple (LCM) of {a} and {b}?"
            answer = abs(a*b) // gcd(a,b)
        return Challenge("Number Theory Nexus", f"{op} Calculation", question, answer, "Number Sense Navigator")
    
    return Challenge("Number Theory Nexus", "Default", "What is 1 + 1?", 2, "Number Sense Navigator")

def generate_geometry_challenge():
    q_type = random.choice(["area_perimeter", "angles", "pythagorean"])

    if q_type == "area_perimeter":
        shape = random.choice(["rectangle", "square"])
        if shape == "rectangle":
            length = random.randint(5, 15)
            width = random.randint(3, 10)
            metric = random.choice(["area", "perimeter"])
            if metric == "area":
                question = f"A rectangle has length {length} and width {width}. What is its area?"
                answer = length * width
            else:
                question = f"A rectangle has length {length} and width {width}. What is its perimeter?"
                answer = 2 * (length + width)
            return Challenge("Geometry Gymnasium", "Area/Perimeter", question, answer, "Geometric Intuition")
        else: # square
            side = random.randint(4, 12)
            metric = random.choice(["area", "perimeter"])
            if metric == "area":
                question = f"A square has a side length of {side}. What is its area?"
                answer = side * side
            else:
                question = f"A square has a side length of {side}. What is its perimeter?"
                answer = 4 * side
            return Challenge("Geometry Gymnasium", "Area/Perimeter", question, answer, "Geometric Intuition")

    elif q_type == "angles":
        angle = random.randint(10, 80)
        op = random.choice(["complementary", "supplementary"])
        if op == "complementary":
            question = f"Two angles are complementary. One angle is {angle} degrees. What is the other angle?"
            answer = 90 - angle
        else:
            question = f"Two angles are supplementary. One angle is {angle} degrees. What is the other angle?"
            answer = 180 - angle
        return Challenge("Geometry Gymnasium", "Angle Relationships", question, answer, "Geometric Intuition")

    elif q_type == "pythagorean":
        triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
        a, b, c = random.choice(triples)
        multiplier = random.randint(1, 3)
        a *= multiplier
        b *= multiplier
        c *= multiplier

        missing = random.choice(["hypotenuse", "leg"])
        if missing == "hypotenuse":
            question = f"A right triangle has legs of length {a} and {b}. What is the length of the hypotenuse?"
            answer = c
        else:
            if random.random() < 0.5:
                question = f"A right triangle has a hypotenuse of {c} and one leg of {a}. What is the length of the other leg?"
                answer = b
            else:
                question = f"A right triangle has a hypotenuse of {c} and one leg of {b}. What is the length of the other leg?"
                answer = a
        return Challenge("Geometry Gymnasium", "Pythagorean Theorem", question, answer, "Geometric Intuition")

    return Challenge("Geometry Gymnasium", "Default", "What is the area of a triangle with base 4 and height 5?", 10, "Geometric Intuition")

def generate_algebra_challenge():
    q_type = random.choice(["linear_equation", "simple_word_problem", "expression_eval"])

    if q_type == "linear_equation":
        a = random.randint(2, 5)
        b = random.randint(-10, 10)
        c = random.randint(-20, 20)
        if (c - b) % a != 0:
            c = a * (random.randint(-5, 5)) + b
        question = f"Solve for x: {a}x + {b} = {c}"
        answer = (c - b) // a
        return Challenge("Algebra Arena", "Linear Equations", question, answer, "Algebra Alchemist")

    elif q_type == "simple_word_problem":
        num_items = random.randint(5, 15)
        cost_per_item = random.randint(2, 8)
        total_cost = num_items * cost_per_item
        question = f"John bought {num_items} apples, each costing ${cost_per_item}. How much did he pay in total?"
        answer = total_cost
        return Challenge("Algebra Arena", "Word Problems", question, answer, "Algebra Alchemist")

    elif q_type == "expression_eval":
        var = random.choice(['x', 'a', 'y'])
        val = random.randint(2, 10)
        op = random.choice(['+', '-', '*'])
        num1 = random.randint(1, 5)
        num2 = random.randint(1, 10)

        question = f"If {var} = {val}, what is {num1}{var} {op} {num2}?"
        if op == '+':
            answer = num1 * val + num2
        elif op == '-':
            answer = num1 * val - num2
        else: # '*'
            answer = num1 * val * num2
        return Challenge("Algebra Arena", "Expression Evaluation", question, answer, "Algebra Alchemist")

    return Challenge("Algebra Arena", "Default", "If x = 5, what is 2x + 3?", 13, "Algebra Alchemist")

def generate_counting_probability_challenge():
    q_type = random.choice(["counting_arrangements", "probability_die", "probability_coin"])

    if q_type == "counting_arrangements":
        num_items = random.randint(3, 5)
        question = f"How many ways can {num_items} distinct items be arranged in a line?"
        answer = factorial(num_items)
        return Challenge("Counting & Probability Citadel", "Permutations", question, answer, "Combinatorics Commander")

    elif q_type == "probability_die":
        die_sides = random.choice([4, 6, 8, 10])
        target_type = random.choice(["number", "even", "odd"])
        
        if target_type == "number":
            target = random.randint(1, die_sides)
            question = f"What is the probability of rolling a {target} on a {die_sides}-sided die?"
            answer = f"1/{die_sides}"
        elif target_type == "even":
            even_count = die_sides // 2
            question = f"What is the probability of rolling an even number on a {die_sides}-sided die?"
            g = gcd(even_count, die_sides)
            answer = f"{even_count//g}/{die_sides//g}"
        else: # odd
            odd_count = (die_sides + 1) // 2
            question = f"What is the probability of rolling an odd number on a {die_sides}-sided die?"
            g = gcd(odd_count, die_sides)
            answer = f"{odd_count//g}/{die_sides//g}"

        return Challenge("Counting & Probability Citadel", "Die Probability", question, answer, "Probability Prophet")

    elif q_type == "probability_coin":
        num_flips = random.randint(2, 3)
        event = random.choice(["all heads", "all tails", "exactly one head"])
        
        if event == "all heads":
            question = f"If you flip a fair coin {num_flips} times, what is the probability of getting all heads?"
            answer = f"1/{2**num_flips}"
        elif event == "all tails":
            question = f"If you flip a fair coin {num_flips} times, what is the probability of getting all tails?"
            answer = f"1/{2**num_flips}"
        else: # exactly one head
            question = f"If you flip a fair coin {num_flips} times, what is the probability of getting exactly one head?"
            answer = f"{num_flips}/{2**num_flips}"

        return Challenge("Counting & Probability Citadel", "Coin Probability", question, answer, "Probability Prophet")

    return Challenge("Counting & Probability Citadel", "Default", "What is the probability of picking a red card from a standard deck of 52 cards?", "1/2", "Probability Prophet")

def generate_pinnacle_challenge():
    generators = [
        generate_number_theory_challenge,
        generate_geometry_challenge,
        generate_algebra_challenge,
        generate_counting_probability_challenge
    ]
    return random.choice(generators)()

# Map level names to their generation functions
CHALLENGE_GENERATORS = {
    "Number Theory Nexus": generate_number_theory_challenge,
    "Geometry Gymnasium": generate_geometry_challenge,
    "Algebra Arena": generate_algebra_challenge,
    "Counting & Probability Citadel": generate_counting_probability_challenge,
    "Problem-Solving Pinnacle": generate_pinnacle_challenge,
}

def generate_challenge_for_level(level_name):
    generator = CHALLENGE_GENERATORS.get(level_name)
    if generator:
        return generator()
    else:
        return Challenge(level_name, "Error", "Error: No generator for this level.", "0", "Bug Finder")

# --- AI Hint Generation Function (UPDATED for specific hints) ---
def generate_hint(challenge):
    question = challenge.question
    topic = challenge.topic
    
    # Helper to extract numbers from a string
    def extract_numbers(text):
        return [int(s) for s in re.findall(r'\b\d+\b', text)]

    # Hints for Number Theory
    if topic == "Modular Arithmetic":
        numbers = extract_numbers(question)
        if len(numbers) >= 2:
            num, divisor = numbers[0], numbers[1]
            return f"Hint: Divide {num} by {divisor}. The answer is the leftover value."
    
    elif topic == "Prime Factors":
        numbers = extract_numbers(question)
        if numbers:
            num = numbers[0]
            return f"Hint: Start dividing {num} by the smallest prime numbers (2, 3, 5, etc.) until you can't anymore. The largest one you used is the answer."
            
    elif topic == "GCD Calculation":
        numbers = extract_numbers(question)
        if len(numbers) >= 2:
            a, b = numbers[0], numbers[1]
            return f"Hint: List the factors of {a} and the factors of {b}. Find the largest number common to both lists."
    
    elif topic == "LCM Calculation":
        numbers = extract_numbers(question)
        if len(numbers) >= 2:
            a, b = numbers[0], numbers[1]
            return f"Hint: List the multiples of {a} and the multiples of {b}. The smallest number common to both lists is the answer."

    # Hints for Geometry
    elif topic == "Area/Perimeter":
        if "rectangle" in question.lower():
            numbers = extract_numbers(question)
            if len(numbers) >= 2:
                length, width = numbers[0], numbers[1]
                if "area" in question.lower():
                    return f"Hint: For a rectangle, Area = Length × Width. Multiply {length} by {width}."
                else: # perimeter
                    return f"Hint: For a rectangle, Perimeter = 2 × (Length + Width). Add {length} and {width}, then multiply by 2."
        elif "square" in question.lower():
            numbers = extract_numbers(question)
            if numbers:
                side = numbers[0]
                if "area" in question.lower():
                    return f"Hint: For a square, Area = Side × Side. Multiply {side} by itself."
                else: # perimeter
                    return f"Hint: For a square, Perimeter = 4 × Side. Multiply {side} by 4."
    
    elif topic == "Angle Relationships":
        numbers = extract_numbers(question)
        if numbers:
            angle = numbers[0]
            if "complementary" in question.lower():
                return f"Hint: Complementary angles add up to 90 degrees. Subtract {angle} from 90."
            else: # supplementary
                return f"Hint: Supplementary angles add up to 180 degrees. Subtract {angle} from 180."

    elif topic == "Pythagorean Theorem":
        numbers = extract_numbers(question)
        if len(numbers) >= 2:
            val1, val2 = numbers[0], numbers[1]
            if "hypotenuse" in question.lower() and "legs" in question.lower():
                # Legs a and b are given, find c
                return f"Hint: Use a² + b² = c². So, {val1}² + {val2}² = c². Then take the square root."
            elif "hypotenuse" in question.lower() and "one leg" in question.lower():
                # Hypotenuse and one leg are given, find other leg
                return f"Hint: Use a² + b² = c². So, {val1}² + x² = {val2}² (or vice versa). Solve for x, then take the square root."
            
    # Hints for Algebra
    elif topic == "Linear Equations":
        # Example: Solve for x: 3x + 5 = 14
        match = re.search(r'(\d+)x \+ (-?\d+) = (-?\d+)', question)
        if match:
            a, b, c = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return f"Hint: First, subtract {b} from both sides. Then, divide both sides by {a}."
        # Add a case for subtraction directly in the question, e.g., 3x - 5 = 14
        match = re.search(r'(\d+)x - (\d+) = (-?\d+)', question)
        if match:
            a, b, c = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return f"Hint: First, add {b} to both sides. Then, divide both sides by {a}."
        
    elif topic == "Word Problems":
        # Example: John bought 5 apples, each costing $3. How much did he pay in total?
        numbers = extract_numbers(question)
        if len(numbers) >= 2:
            num_items, cost_per_item = numbers[0], numbers[1]
            return f"Hint: This is a multiplication problem. Multiply the number of items ({num_items}) by the cost per item (${cost_per_item})."

    elif topic == "Expression Evaluation":
        # Example: If x = 5, what is 2x + 3?
        match = re.search(r'If (\w+) = (\d+), what is ([\w\d\s\+\-\*]+)\?', question)
        if match:
            var, val, expr = match.group(1), match.group(2), match.group(3)
            return f"Hint: Replace '{var}' with {val} in the expression. Then calculate the result."

    # Hints for Counting & Probability
    elif topic == "Permutations":
        numbers = extract_numbers(question)
        if numbers:
            num_items = numbers[0]
            return f"Hint: To find the number of ways to arrange {num_items} distinct items, calculate {num_items} factorial ({num_items}!)."

    elif topic == "Die Probability":
        numbers = extract_numbers(question)
        die_sides = numbers[0] if numbers else 6 # Default to 6 if not found
        if "rolling a " in question.lower() and "number" in question.lower():
            target = numbers[1]
            return f"Hint: There is 1 favorable outcome ({target}) out of {die_sides} total possible outcomes."
        elif "even number" in question.lower():
            even_count = die_sides // 2
            return f"Hint: Count the even numbers on a {die_sides}-sided die. The probability is that count divided by {die_sides}. Simplify the fraction."
        elif "odd number" in question.lower():
            odd_count = (die_sides + 1) // 2
            return f"Hint: Count the odd numbers on a {die_sides}-sided die. The probability is that count divided by {die_sides}. Simplify the fraction."

    elif topic == "Coin Probability":
        numbers = extract_numbers(question)
        num_flips = numbers[0] if numbers else 2
        total_outcomes = 2 ** num_flips
        if "all heads" in question.lower() or "all tails" in question.lower():
            return f"Hint: There is only 1 way to get all heads/tails. The total possible outcomes are 2 raised to the power of the number of flips ({total_outcomes})."
        elif "exactly one head" in question.lower():
            return f"Hint: Think about how many positions the single head can be in. The total possible outcomes are 2 raised to the power of the number of flips ({total_outcomes})."


    # Default fallback hint
    return "This problem requires careful reading. Identify the key numbers and what the question is asking you to find."


def draw_button(surface, rect, text, font, color, hover_color, text_color=BLACK):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    current_color = hover_color if is_hovered else color
    pygame.draw.rect(surface, current_color, rect, border_radius=10)
    pygame.draw.rect(surface, BLACK, rect, 3, border_radius=10)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return is_hovered

def draw_input_box(surface, rect, text, font, active_color, inactive_color, is_active):
    color = active_color if is_active else inactive_color
    pygame.draw.rect(surface, color, rect, 2, border_radius=5)
    pygame.draw.rect(surface, WHITE, rect.inflate(-2, -2), border_radius=5)
    text_surf = font.render(text, True, BLACK)
    surface.blit(text_surf, (rect.x + 5, rect.y + 5))
    if is_active:
        cursor_pos_x = rect.x + 5 + text_surf.get_width()
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            pygame.draw.line(surface, BLACK, (cursor_pos_x, rect.y + 5), (cursor_pos_x, rect.y + rect.height - 5), 2)


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

    current_level_x = player_name_text.get_width() + 40
    level_text = font_medium.render(f"Current Level: {player.get_current_level_name()}", True, BLACK)
    screen.blit(level_text, (current_level_x, 20))

    skills_x = current_level_x + level_text.get_width() + 40
    skill_token_text = font_medium.render("Skills:", True, BLACK)
    screen.blit(skill_token_text, (skills_x, 20))
    
    x_offset = skills_x + skill_token_text.get_width() + 10
    
    for token, count in player.skill_tokens.items():
        display_token_name = token
        if len(token) > 15:
            display_token_name = token[:12] + "..."

        token_surf = font_small.render(f"{display_token_name}: {count}", True, BLACK)
        if x_offset + token_surf.get_width() > screen_width - 20:
            break
        screen.blit(token_surf, (x_offset, 25))
        x_offset += token_surf.get_width() + 15

    # Correct Streak Display (in game board)
    streak_color = GREEN if player.correct_streak >= 5 else ORANGE
    streak_text = font_medium.render(f"Streak: {player.correct_streak}/5", True, streak_color)
    streak_rect = streak_text.get_rect(topright=(screen_width - 20, 20))
    screen.blit(streak_text, streak_rect)


    # Level Zones (Buttons)
    for level_name, rect in LEVEL_LOCATIONS.items():
        color = GREEN if player.level_progress[level_name] else BLUE
        hover_color = LIGHT_GREEN if player.level_progress[level_name] else LIGHT_BLUE
        is_current_level = level_name == player.get_current_level_name()

        draw_button(screen, rect, level_name, font_medium, color, hover_color)

        if is_current_level:
            arrow_text = font_large.render("▶", True, RED)
            arrow_rect = arrow_text.get_rect(midright=(rect.left - 10, rect.centery))
            screen.blit(arrow_text, arrow_rect)


    # Power-Up Buttons
    # These are only for display, actual usage is on challenge screen
    hint_rect_board = pygame.Rect(screen_width - 150, screen_height - 100, 120, 40)
    double_check_rect_board = pygame.Rect(screen_width - 150, screen_height - 50, 120, 40)

    hint_text_board = f"Hint ({player.power_ups['Hint Helper']})"
    double_check_text_board = f"2x Check ({player.power_ups['Double Check']})"

    # Pass font_small as the font argument
    draw_button(screen, hint_rect_board, hint_text_board, font_small, DARK_GRAY, GRAY) # Display only, not clickable
    draw_button(screen, double_check_rect_board, double_check_text_board, font_small, DARK_GRAY, GRAY) # Display only, not clickable

    # Next Level Button
    next_level_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 80, 150, 50)
    can_advance = player.correct_streak >= 5 and player.current_level_idx < len(LEVELS) - 1
    
    next_level_color = GREEN if can_advance else DARK_GRAY
    next_level_hover_color = LIGHT_GREEN if can_advance else DARK_GRAY

    if draw_button(screen, next_level_rect, "Next Level", font_medium, next_level_color, next_level_hover_color, text_color=BLACK if can_advance else GRAY):
        if can_advance:
            return "next_level_clicked"


def draw_challenge_screen():
    screen.fill(YELLOW) # This fills the background for the challenge screen.

    # Streak Display in Challenge Screen
    streak_color = GREEN if player.correct_streak >= 5 else ORANGE
    streak_text = font_medium.render(f"Streak: {player.correct_streak}/5", True, streak_color)
    streak_rect = streak_text.get_rect(topright=(screen_width - 20, 20))
    screen.blit(streak_text, streak_rect)

    # Back to Map Button
    back_button_rect = pygame.Rect(20, 20, 150, 40)
    if draw_button(screen, back_button_rect, "Back to Map", font_small, BLUE, LIGHT_BLUE):
        return "back_to_map_clicked"

    if current_challenge:
        current_challenge.display_question(screen)

        # Hint Button
        hint_button_rect = pygame.Rect(screen_width - 150, screen_height - 60, 120, 40)
        
        # Determine if hint button should be active
        # Active if power-up available AND hint not already given for THIS challenge AND not submitted
        hint_can_be_used = player.power_ups['Hint Helper'] > 0 and not current_challenge.hint_given and not answer_submitted

        hint_button_color = PURPLE if hint_can_be_used else DARK_GRAY
        hint_button_hover = LIGHT_BLUE if hint_can_be_used else DARK_GRAY
        hint_button_text = f"Hint ({player.power_ups['Hint Helper']})"

        if hint_can_be_used:
            if draw_button(screen, hint_button_rect, hint_button_text, font_small, hint_button_color, hint_button_hover, text_color=WHITE):
                global hint_message # Declare as global to modify
                if player.use_power_up("Hint Helper"): # Try to use a hint
                    hint_message = generate_hint(current_challenge)
                    current_challenge.hint_given = True # Set flag so hint cannot be given again for this challenge
        else: # Draw disabled button
             draw_button(screen, hint_button_rect, hint_button_text, font_small, DARK_GRAY, DARK_GRAY, text_color=GRAY)


        # Display Hint
        if hint_message:
            # Re-wrap text for display based on screen width
            hint_lines = []
            words = hint_message.split(' ')
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font_small.size(test_line)[0] > screen_width - 100:
                    hint_lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    current_line.append(word)
            hint_lines.append(' '.join(current_line))

            hint_y_offset = screen_height - 400 # Initial position for hint
            for line in hint_lines:
                hint_text_surf = font_small.render(line, True, DARK_GRAY)
                hint_rect = hint_text_surf.get_rect(centerx=screen_width // 2, y=hint_y_offset)
                screen.blit(hint_text_surf, hint_rect)
                hint_y_offset += 25 # Line spacing

        # Adjust vertical positioning based on hint visibility
        input_y_pos = screen_height - 200
        feedback_y_pos = input_y_pos - 60
        button_y_pos = screen_height - 120

        if hint_message:
            # If hint is visible, push down other elements slightly
            last_hint_line_bottom = screen_height - 400 + (len(hint_lines) * 25)
            input_y_pos = max(input_y_pos, last_hint_line_bottom + 20) # Ensure gap
            feedback_y_pos = input_y_pos - 60
            button_y_pos = input_y_pos + 80 # Place buttons below input box

        # Answer Input Box
        answer_box_rect = pygame.Rect(screen_width // 2 - 200, input_y_pos, 400, 50)
        draw_input_box(screen, answer_box_rect, player_answer_input, font_large, BLUE, DARK_GRAY, ANSWER_BOX_ACTIVE and not answer_submitted)

        # Feedback Message
        if feedback_message:
            feedback_text_surf = font_large.render(feedback_message, True, RED if "Incorrect" in feedback_message else GREEN)
            feedback_text_rect = feedback_text_surf.get_rect(center=(screen_width // 2, feedback_y_pos))
            screen.blit(feedback_text_surf, feedback_text_rect)

        # Conditional Buttons
        if not answer_submitted:
            # Submit Button
            submit_button_rect = pygame.Rect(screen_width // 2 - 75, button_y_pos, 150, 50)
            if draw_button(screen, submit_button_rect, "Submit", font_large, GREEN, LIGHT_GREEN):
                return "submit_answer_clicked"
        else:
            # Next Challenge Button
            next_challenge_button_rect = pygame.Rect(screen_width // 2 - 100, button_y_pos, 200, 50)
            if draw_button(screen, next_challenge_button_rect, "Next Challenge", font_large, BLUE, LIGHT_BLUE):
                return "next_challenge_clicked"
    else:
        # This part should be displayed if current_challenge is None (for debugging)
        temp_text = font_large.render("Loading Challenge... (current_challenge is None)", True, BLACK)
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

        if game_state == MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = GET_NAME
                player_answer_input = ""
                ANSWER_BOX_ACTIVE = True

        elif game_state == GET_NAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                name_box_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 300, 50)
                if name_box_rect.collidepoint(event.pos):
                    ANSWER_BOX_ACTIVE = True
                else:
                    ANSWER_BOX_ACTIVE = False
            if event.type == pygame.KEYDOWN and ANSWER_BOX_ACTIVE:
                if event.key == pygame.K_RETURN:
                    if player_answer_input.strip():
                        player = Player(player_answer_input.strip())
                        game_state = GAME_BOARD
                        ANSWER_BOX_ACTIVE = False
                    else:
                        print("Please enter a name!")
                elif event.key == pygame.K_BACKSPACE:
                    player_answer_input = player_answer_input[:-1]
                else:
                    player_answer_input += event.unicode

        elif game_state == GAME_BOARD:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for level_name, rect in LEVEL_LOCATIONS.items():
                    if rect.collidepoint(mouse_pos) and level_name == player.get_current_level_name():
                        current_challenge = generate_challenge_for_level(level_name)
                        game_state = CHALLENGE_SCREEN
                        player_answer_input = ""
                        feedback_message = ""
                        hint_message = "" # Clear hint when new challenge starts
                        answer_submitted = False
                        ANSWER_BOX_ACTIVE = True
                        break

                next_level_rect = pygame.Rect(screen_width // 2 - 75, screen_height - 80, 150, 50)
                if next_level_rect.collidepoint(mouse_pos):
                    if player.correct_streak >= 5 and player.current_level_idx < len(LEVELS) - 1:
                        player.level_progress[player.get_current_level_name()] = True
                        player.current_level_idx += 1
                        player.correct_streak = 0
                        feedback_message = f"Entering {player.get_current_level_name()}!"
                        feedback_timer = pygame.time.get_ticks()
                    elif player.current_level_idx == len(LEVELS) - 1 and player.correct_streak >=5:
                        player.level_progress[player.get_current_level_name()] = True
                        game_state = WIN_SCREEN
                    else:
                        feedback_message = "Need 5 correct answers in a row to advance!"
                        feedback_timer = pygame.time.get_ticks()


        elif game_state == CHALLENGE_SCREEN:
            # Handle button clicks through the return values of draw_challenge_screen
            action = draw_challenge_screen() # Call this to draw and get actions

            if event.type == pygame.MOUSEBUTTONDOWN:
                if action == "back_to_map_clicked":
                    game_state = GAME_BOARD
                    player_answer_input = ""
                    feedback_message = ""
                    hint_message = "" # Clear hint
                    answer_submitted = False
                    ANSWER_BOX_ACTIVE = False
                    current_challenge = None
                elif action == "submit_answer_clicked":
                    if current_challenge and not answer_submitted:
                        is_correct = False
                        player_answer_strip = player_answer_input.lower().strip()
                        correct_answer_strip = current_challenge.answer.lower().strip()

                        try:
                            # Evaluate common math expressions
                            eval_player_answer = str(eval(player_answer_strip.replace('^', '**').replace('pi', str(3.14159265))))
                            if eval_player_answer == correct_answer_strip:
                                is_correct = True
                            elif player_answer_strip == correct_answer_strip: # For cases where eval isn't needed or fails
                                is_correct = True
                        except (NameError, SyntaxError, TypeError):
                            # Fallback for non-evaluatable inputs (e.g., fractions like "1/2")
                            if player_answer_strip == correct_answer_strip:
                                is_correct = True

                        if is_correct:
                            feedback_message = "Correct!"
                            player.add_skill_token(current_challenge.skill_token)
                            player.correct_streak += 1
                        else:
                            feedback_message = f"Incorrect. Answer was: {current_challenge.answer}"
                            player.correct_streak = 0
                        
                        answer_submitted = True
                        ANSWER_BOX_ACTIVE = False
                        hint_message = "" # Clear hint after submission
                elif action == "next_challenge_clicked":
                    current_challenge = generate_challenge_for_level(player.get_current_level_name())
                    player_answer_input = ""
                    feedback_message = ""
                    hint_message = "" # Clear hint for next challenge
                    answer_submitted = False
                    ANSWER_BOX_ACTIVE = True

            if event.type == pygame.KEYDOWN and ANSWER_BOX_ACTIVE and not answer_submitted:
                if event.key == pygame.K_RETURN:
                    if current_challenge:
                        is_correct = False
                        player_answer_strip = player_answer_input.lower().strip()
                        correct_answer_strip = current_challenge.answer.lower().strip()

                        try:
                            # Evaluate common math expressions
                            eval_player_answer = str(eval(player_answer_strip.replace('^', '**').replace('pi', str(3.14159265))))
                            if eval_player_answer == correct_answer_strip:
                                is_correct = True
                            elif player_answer_strip == correct_answer_strip: # For cases where eval isn't needed or fails
                                is_correct = True
                        except (NameError, SyntaxError, TypeError):
                            # Fallback for non-evaluatable inputs (e.g., fractions like "1/2")
                            if player_answer_strip == correct_answer_strip:
                                is_correct = True

                        if is_correct:
                            feedback_message = "Correct!"
                            player.add_skill_token(current_challenge.skill_token)
                            player.correct_streak += 1
                        else:
                            feedback_message = f"Incorrect. Answer was: {current_challenge.answer}"
                            player.correct_streak = 0
                        
                        answer_submitted = True
                        ANSWER_BOX_ACTIVE = False
                        hint_message = "" # Clear hint after submission

                elif event.key == pygame.K_BACKSPACE:
                    player_answer_input = player_answer_input[:-1]
                else:
                    player_answer_input += event.unicode
                    
        elif game_state == WIN_SCREEN:
            pass


    # --- Drawing ---
    # The screen.fill(WHITE) from here has been removed. Each draw_state function now handles its own background.

    if game_state == MENU:
        draw_menu()
    elif game_state == GET_NAME:
        draw_get_name()
    elif game_state == GAME_BOARD:
        draw_game_board()
    elif game_state == CHALLENGE_SCREEN:
        # Drawing for CHALLENGE_SCREEN is explicitly handled by the action = draw_challenge_screen()
        # call within the event loop for this state.
        pass 
    elif game_state == WIN_SCREEN:
        draw_win_screen()

    # Clear feedback message after a delay on the game board
    if game_state == GAME_BOARD and feedback_message and pygame.time.get_ticks() - feedback_timer > 2000:
        feedback_message = ""


    pygame.display.flip()
    clock.tick(60)

pygame.quit()