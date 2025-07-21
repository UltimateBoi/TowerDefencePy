import pygame
from utils.TextUtil import TextUtil
from utils.ButtonUtil import TextButton

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BG_IMAGE_PATH = "assets/background.png"

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Game")

def draw_profile_icon(screen, x, y, radius):
    pygame.draw.circle(screen, (255, 255, 255), (x, y), radius)
  # Draw a simple user icon (head and shoulders)
    pygame.draw.circle(screen, (180, 180, 180), (x, y-5), radius//2)
    pygame.draw.rect(screen, (180, 180, 180), (x-radius//2, y, radius, radius//2), border_radius=radius//4)

def draw_money_display(screen, x, y, width, height, amount):
  # Draw rounded rectangle
    pygame.draw.rect(screen, (153, 101, 21), (x, y, width, height), border_radius=height//2)
  # Draw money icon (simple green rectangle as placeholder)
    icon_rect = pygame.Rect(x+8, y+8, height-16, height-16)
    pygame.draw.rect(screen, (0, 177, 47), icon_rect, border_radius=6)
  # Draw $ text on icon
    font = pygame.font.SysFont(None, 28)
    dollar = font.render("$", True, (255,255,255))
    screen.blit(dollar, (icon_rect.x+5, icon_rect.y+2))
  # Draw amount
    amount_font = pygame.font.SysFont(None, 40)
    amount_text = amount_font.render(str(amount), True, (255,255,255))
    screen.blit(amount_text, (x+height, y+height//2 - amount_text.get_height()//2))

def main_menu():
    running = True
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)

  # Button settings
    button_width = 160
    button_height = 60
    button_radius = 20
    button_spacing = 40
    total_width = button_width * 2 + button_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_pos = SCREEN_HEIGHT - 100

    button_color = (0, 177, 47) # #00B12F
  # Buttons with rounded corners and spacing
    start_button = TextButton("start", start_x, y_pos, button_width, button_height, "Start", radius=button_radius, color=button_color)
    towers_button = TextButton("towers", start_x + button_width + button_spacing, y_pos, button_width, button_height, "Towers", radius=button_radius, color=button_color)

    money_amount = 999
    profile_radius = 32
    money_width = 120
    money_height = 48
    profile_x = 20 + profile_radius
    profile_y = 20 + profile_radius
    money_x = SCREEN_WIDTH - money_width - 20
    money_y = 20

  # Placeholder for background image
    try:
        bg_image = pygame.image.load(BG_IMAGE_PATH)
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:
        bg_image = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if start_button.is_clicked(mx, my):
                    print("Start button clicked!")
                elif towers_button.is_clicked(mx, my):
                    print("Towers button clicked!")
              # Profile icon click (circle hit test)
                elif (mx - profile_x)**2 + (my - profile_y)**2 <= profile_radius**2:
                    print("Profile icon clicked!")

      # Draw background
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((34, 139, 34)) # Fallback: green grass color

      # Draw title
        TextUtil.draw_string(screen, font, "Tower Defense Game", (255, 255, 255), SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

      # Draw buttons
        start_button.draw(screen)
        towers_button.draw(screen)

      # Draw profile icon and money display
        draw_profile_icon(screen, profile_x, profile_y, profile_radius)
        draw_money_display(screen, money_x, money_y, money_width, money_height, money_amount)

        pygame.display.flip()

    pygame.quit() 