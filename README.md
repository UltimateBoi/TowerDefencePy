# Tower Defense Game

A tower defense game inspired by Bloons TD6, built with Python and Pygame.

## Features

- **Core Gameplay Loop**: Spawn waves of bloons, place towers, defend your base
- **Multiple Bloon Types**: Red, Blue, Green, and Yellow bloons with different health and speed
- **Tower System**: Place towers to automatically target and shoot at bloons
- **Wave Management**: Progressive waves with increasing difficulty
- **Resource Management**: Earn money by popping bloons, spend money to place towers
- **Path Following**: Bloons follow a predefined path from spawn to end
- **Projectile System**: Towers fire projectiles that track and hit bloons

## How to Play

1. **Start the Game**: Click the "Start" button in the main menu
2. **Place Towers**: Left-click anywhere on the map to place a tower (costs $10)
3. **Start Waves**: Press SPACE to start the next wave of bloons
4. **Defend**: Towers will automatically target and shoot at bloons in range
5. **Survive**: Don't let bloons reach the end or you'll lose lives
6. **Progress**: Complete waves to advance to harder challenges

## Controls

- **Left Click**: Place tower
- **SPACE**: Start next wave
- **ESC**: Quit game

## Game Elements

### Bloons
- **Red Bloon**: 1 health, 1.0 speed, $1 reward
- **Blue Bloon**: 2 health, 1.2 speed, $2 reward
- **Green Bloon**: 3 health, 1.5 speed, $3 reward
- **Yellow Bloon**: 4 health, 2.0 speed, $4 reward

### Towers
- **Range**: 100 pixels
- **Damage**: 1 per shot
- **Fire Rate**: 1 shot per second
- **Cost**: $10

### Starting Resources
- **Money**: $50
- **Lives**: 20

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game:
```bash
python __main__.py
```

## Technical Details

- **Resolution**: 1280x720 (fixed)
- **Frame Rate**: 60 FPS
- **Map Format**: JSON files in the `maps/` directory
- **Path System**: Bloons follow waypoints defined in the map data

## Game Architecture

- **Bloon Class**: Handles bloon movement, health, and rendering
- **Tower Class**: Manages tower targeting, shooting, and range
- **Projectile Class**: Handles projectile movement and collision
- **Wave Class**: Controls bloon spawning and wave progression
- **GameMap Class**: Loads and renders the game map
- **TowerDefenseGame Class**: Main game loop and state management

## Future Enhancements

The current implementation focuses on core gameplay. Potential additions include:
- Tower upgrades and different tower types
- More bloon types with special abilities
- Sound effects and music
- Multiple maps
- Achievement system
- Save/load functionality
- Special abilities and power-ups
