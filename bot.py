import pygame, random, sys, json

pygame.init()

WIDTH, HEIGHT = 700, 950
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordly")

FONT = pygame.font.Font(None, 64)
SMALL = pygame.font.Font(None, 40)
BIG = pygame.font.Font(None, 100)
KEY_FONT = pygame.font.Font(None, 36)
hard_mode = False  # ← глобальный флаг режима
hard_btn_rect = None


with open("words.json", "r") as f:
    data = json.load(f)
    WORDS = data["words"]

#цвета
colors = {
    "bg": (18, 18, 19),  # фон
    "dark": (35, 35, 38),  # пустые поля
    "gray": (140, 140, 145),  # неправильные буквы
    "yellow": (181, 159, 59),  # буквы не на месте
    "green": (83, 141, 78),  # буквы на месте
    "white": (255, 255, 255),
    "red": (200, 60, 60),
}

keyboard_layout = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]


def new_game():
    global \
        WORD, \
        guesses, \
        current, \
        key_colors, \
        game_over, \
        win, \
        error_text, \
        greens, \
        yellows
    greens = []
    yellows = []
    WORD = random.choice(WORDS)
    guesses = []
    current = ""
    key_colors = {}
    game_over = False
    win = False
    error_text = ""


new_game()


def check_hard_mode(word):
    global hard_mode, yellows, greens
    if not hard_mode:
        return True
    for char, i in yellows:
        if char not in word:
            return False
    for char, index in greens:
        if word[index] != char:
            return False
    return True


def evaluate_guess(word):
    global greens, yellows
    result = ["gray"] * 5
    word_letters = list(WORD)
    for i in range(5):
        if word[i] == word_letters[i]:
            if (word[i], i) in yellows:
                yellows.remove((word[i], i))
            if (word[i], i) not in greens:
                greens.append((word[i], i))
            result[i] = "green"
            word_letters[i] = None
    for i in range(5):
        if result[i] == "gray" and word[i] in word_letters:
            if (word[i], i) not in yellows:
                yellows.append((word[i], i))
            result[i] = "yellow"
            word_letters[word_letters.index(word[i])] = None
    for i, ch in enumerate(word):
        update_key_color(ch.upper(), result[i])
    return result


def update_key_color(ch, new_color):
    priority = {"gray": 1, "yellow": 2, "green": 3}
    old = key_colors.get(ch, "dark")
    if priority[new_color] > priority.get(old, 0):
        key_colors[ch] = new_color


def draw_keyboard():
    start_y = 730
    spacing_y = 60
    for row_i, row in enumerate(keyboard_layout):
        y = start_y + row_i * spacing_y
        offset = (WIDTH - len(row) * 55) // 2
        for i, ch in enumerate(row):
            x = offset + i * 55
            key_state = key_colors.get(ch, "dark")
            color = colors[key_state]
            rect = pygame.Rect(x, y, 50, 50)
            pygame.draw.rect(screen, color, rect, border_radius=6)
            text = KEY_FONT.render(ch, True, colors["white"]) #текст в квартинкуы
            screen.blit(text, (x + 12, y + 10))


def draw_board():
    #окрашивание всего поля
    screen.fill(colors["bg"])
    # рисуем сетку
    for row in range(6):
        for col in range(5):
            rect = pygame.Rect(100 + col * 90, 120 + row * 90, 80, 80)
            pygame.draw.rect(screen, colors["dark"], rect, border_radius=6)

    # прошлые слова
    for r, word in enumerate(guesses):
        result = evaluate_guess(word)
        for c, ch in enumerate(word):
            rect = pygame.Rect(100 + c * 90, 120 + r * 90, 80, 80)
            pygame.draw.rect(screen, colors[result[c]], rect, border_radius=6)
            text = FONT.render(ch.upper(), True, colors["white"])
            screen.blit(text, (rect.x + 20, rect.y + 10))

    # текущее слово
    for i, ch in enumerate(current):
        rect = pygame.Rect(100 + i * 90, 120 + len(guesses) * 90, 80, 80)
        pygame.draw.rect(screen, colors["dark"], rect, border_radius=6)
        text = FONT.render(ch.upper(), True, colors["white"])
        screen.blit(text, (rect.x + 20, rect.y + 10))

    # заголовок
    title = SMALL.render("Wordly", True, colors["white"])
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    # КНОПКА HARD
    draw_hard_button()

    # сообщение об ошибке не валидное слово
    if error_text:
        err = SMALL.render(error_text, True, colors["red"])
        screen.blit(err, (WIDTH // 2 - err.get_width() // 2, 670))

    draw_keyboard()
    if game_over:
        return draw_end_screen()

    pygame.display.flip() #обновление прорисовки
    return None


def draw_hard_button():
    global hard_btn_rect
    label = "HARD: ON" if hard_mode else "HARD: OFF"
    color = colors["yellow"] if hard_mode else colors["gray"]
    w, h = 160, 44
    x, y = WIDTH - w - 20, 30  # правый верхний угол
    hard_btn_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, hard_btn_rect, border_radius=8)
    txt = SMALL.render(label, True, colors["white"])
    screen.blit(
        txt, (x + (w - txt.get_width()) // 2, y + (h - txt.get_height()) // 2 - 2)
    )


def draw_end_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT)) #новый слой
    overlay.set_alpha(220)#прозрачность
    overlay.fill(colors["bg"])
    screen.blit(overlay, (0, 0))#накладывается наверх

    msg = "YOU WON!" if win else "YOU LOST!"
    color = colors["green"] if win else colors["red"]
    text = BIG.render(msg, True, color)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 300))

    if not win:
        wtxt = SMALL.render(f"Word was: {WORD.upper()}", True, colors["white"])
        screen.blit(wtxt, (WIDTH // 2 - wtxt.get_width() // 2, 400))

    btn_rect = pygame.Rect(WIDTH // 2 - 120, 500, 240, 80)
    pygame.draw.rect(screen, colors["green"], btn_rect, border_radius=12)
    btn_text = SMALL.render("TRY AGAIN", True, colors["white"])
    screen.blit(
        btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - 10)
    )
    pygame.display.flip()
    return btn_rect


#основной цикл
btn_rect = None
while True:
    btn_rect = draw_board()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # экран конца игры
        if game_over:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and btn_rect
                and btn_rect.collidepoint(event.pos)
            ):
                new_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                new_game()
            continue

        # обработка ввода
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(current) == 5:
                if current not in WORDS:
                    error_text = "Not a valid word!"
                    continue
                error_text = ""
                flag = check_hard_mode(current)
                if not flag:
                    error_text = "Hard mode! Use all hints that you have"
                else:
                    guesses.append(current)
                    if current == WORD:
                        win = True
                        game_over = True
                    elif len(guesses) == 6:
                        win = False
                        game_over = True
                current = ""
            elif event.key == pygame.K_BACKSPACE:
                current = current[:-1]
            elif event.unicode.isalpha() and len(current) < 5 and ord('a' )<= ord(event.unicode.lower()) <= ord('z'):
                current += event.unicode.lower()

        # клики по экранной клавиатуре
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = event.pos
            if (
                hard_btn_rect
                and hard_btn_rect.collidepoint(mx, my)
                and len(guesses) < 1
            ):
                hard_mode = not hard_mode
                # по желанию: чистим знания подсказок, если включили/выключили режим
                greens = []
                yellows = []
                error_text = "Hard Mode: ON" if hard_mode else "Hard Mode: OFF"
                continue
            start_y = 730
            spacing_y = 60
            for row_i, row in enumerate(keyboard_layout):
                y = start_y + row_i * spacing_y
                offset = (WIDTH - len(row) * 55) // 2
                for i, ch in enumerate(row):
                    x = offset + i * 55
                    rect = pygame.Rect(x, y, 50, 50)
                    if rect.collidepoint(mx, my):
                        if len(current) < 5:
                            current += ch.lower()
