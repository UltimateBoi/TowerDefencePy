import pygame
import subprocess
from utils.TextUtil import TextUtil
from utils.ButtonUtil import TextButton
import getpass
from game import TowerDefenseGame
from game.ui.tower_upgrades_screen import TowerUpgradesScreen

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BG_IMAGE_PATH = "assets/background.png"

def get_git_commit_hash():
    """Get the current git commit hash (short version)"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"

def get_window_title():
    """Get the window title with git commit hash"""
    commit_hash = get_git_commit_hash()
    return f"Tower Defense Game - git-{commit_hash}"

def draw_money_display(screen, x, y, width, height, amount):
   # Draw rounded rectangle
    pygame.draw.rect(screen, (153, 101, 21), (x, y, width, height), border_radius=height//2)
    # Draw money icon (simple green square as placeholder)
    icon_size = height - 16
    icon_x = x + (height - icon_size) // 2
    icon_y = y + (height - icon_size) // 2
    icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
    pygame.draw.rect(screen, (0, 177, 47), icon_rect, border_radius=icon_size//4)
    # Draw $ text on icon
    font = pygame.font.SysFont(None, 28)
    dollar = font.render("$", True, (255,255,255))
    dollar_rect = dollar.get_rect(center=(icon_rect.centerx, icon_rect.centery))
    screen.blit(dollar, dollar_rect)
    # Draw amount
    amount_font = pygame.font.SysFont(None, 40)
    amount_text = amount_font.render(str(amount), True, (255,255,255))
    screen.blit(amount_text, (x+height, y+height//2 - amount_text.get_height()//2))

def main_menu():
    # Initialize screen inside the function
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(get_window_title())
    
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

    button_color = (0, 177, 47) #00B12F
    # Buttons with rounded corners and spacing
    start_button = TextButton("start", start_x, y_pos, button_width, button_height, "Start", radius=button_radius, color=button_color)
    towers_button = TextButton("towers", start_x + button_width + button_spacing, y_pos, button_width, button_height, "Towers", radius=button_radius, color=button_color)

    money_width = 120
    money_height = 48
    money_amount = 999
    username = getpass.getuser()
    profile_x = 20 # Adjusted for text
    profile_y = 20
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
                    # Start the tower defense game
                    game = TowerDefenseGame()
                    game.run()
                    # Reinitialize display after game ends
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    pygame.display.set_caption(get_window_title())
                elif towers_button.is_clicked(mx, my):
                    print("Towers button clicked!")
                    # Show tower upgrades screen
                    tower_upgrades_screen = TowerUpgradesScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
                    upgrades_running = True
                    
                    while upgrades_running:
                        upgrades_events = pygame.event.get()
                        mouse_pos = pygame.mouse.get_pos()
                        
                        for upgrade_event in upgrades_events:
                            if upgrade_event.type == pygame.QUIT:
                                upgrades_running = False
                                running = False # Exit main menu too
                        
                        result = tower_upgrades_screen.update(upgrades_events, mouse_pos)
                        if result == "back":
                            upgrades_running = False
                        
                        tower_upgrades_screen.draw(screen)
                        pygame.display.flip()
                    
                    # Reinitialize display after tower upgrades screen
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    pygame.display.set_caption(get_window_title())
                # Profile icon click (circle hit test)
                # The profile icon click logic is removed as per the edit hint.

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
        # Draw username with blurred rounded rectangle background
        font = pygame.font.SysFont(None, 36)
        TextUtil.draw_text_with_blur_rect(screen, username, font, profile_x, profile_y, padding=16, border_radius=20, blur_radius=8)
        draw_money_display(screen, money_x, money_y, money_width, money_height, money_amount)

        pygame.display.flip()

    pygame.quit() 