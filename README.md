# Tower Defense Game

A tower defense game inspired by Bloons TD6, built with Python and Pygame.

## Features

### Core Gameplay

- **Core Gameplay Loop**: Spawn waves of bloons, place towers, defend your base
- **Multiple Bloon Types**: Red, Blue, Green, and Yellow bloons with different health and speed
- **Tower System**: Place towers to automatically target and shoot at bloons
- **Wave Management**: Progressive waves with increasing difficulty
- **Resource Management**: Earn money by popping bloons, spend money to place towers
- **Path Following**: Bloons follow a predefined path from spawn to end
- **Projectile System**: Towers fire projectiles that track and hit bloons

### Cloud Features (New!)

- **Google Sign-In**: Secure OAuth 2.0 authentication
- **Cloud Save/Load**: Sync your game progress across devices
- **Stats Tracking**: Track your performance and achievements
- **Settings Sync**: Your preferences follow you everywhere
- **Leaderboards**: Compete with players globally (possibly in the future)
- **Guest Mode**: Play without an account
- **Offline Mode**: Full functionality without internet

## How to Play

1. **Start the Game**: Click the "Start" button in the main menu
2. **Select Tower Type**: Use the tower selection panel on the left to choose a tower type
3. **Preview Placement**: Hover over the map to see placement preview with range indicator
4. **Place Towers**: Left-click to place the selected tower type at the previewed location
5. **Select Towers**: Click on placed towers to select them and view upgrade options
6. **Upgrade Towers**: Use the upgrade panel to improve your towers with BTD6-style upgrade paths
7. **Start Waves**: Press SPACE to start the next wave of bloons
8. **Defend**: Towers will automatically target and shoot at bloons in range
9. **Survive**: Don't let bloons reach the end or you'll lose lives
10. **Progress**: Complete waves to advance to harder challenges

## Controls

- **Left Click**: Select tower type / Place tower / Select tower / Upgrade tower  
- **Right Click**: Deselect towers and cancel placement
- **T**: Toggle tower selection panel visibility
- **SPACE**: Start next wave
- **ESC**: Open pause menu

## Placement Modes

The game supports two tower placement modes (configurable in settings):

### Click to Place (Default)

1. Click a tower type to select it
2. Click on the map to place the tower
3. Right-click to deselect

### Drag and Drop

1. Click a tower type to select it  
2. Drag from the tower button to desired location
3. Release to place the tower
4. Right-click to cancel/deselect

## New Features

### BTD6-Style Tower Selection Panel

- **Tower buttons** show 4 different tower types with names and costs
- **Hover effects** highlight buttons and show affordability
- **Smart selection** only allows placing towers you can afford
- **Visual feedback** with color-coded affordability indicators

### Range Preview During Placement

- **Green circle** shows valid placement with exact tower range
- **Red circle** indicates invalid placement locations
- **Real-time preview** follows mouse movement
- **Placement validation** prevents overlapping towers and path blocking

### Interactive Tower Upgrades

- **Click towers** to select them and see their range
- **Upgrade panel** appears when a tower is selected
- **Three upgrade paths** per tower (following BTD6 mechanics)
- **BTD6 upgrade restrictions**: Advanced upgrades limit other paths
- **Visual indicators** show upgrade levels on towers
- **Real-time stat updates** when towers are upgraded

## Game Elements

### Bloons

- **Red Bloon**: 1 health, 1.0 speed, $1 reward
- **Blue Bloon**: 2 health, 1.2 speed, $2 reward
- **Green Bloon**: 3 health, 1.5 speed, $3 reward
- **Yellow Bloon**: 4 health, 2.0 speed, $4 reward

### Towers

#### Dart Monkey ($200)

- **Range**: 96 pixels, **Damage**: 1, **Fire Rate**: 0.95/sec
- Shoots single darts that can pop one bloon

#### Tack Shooter ($240)

- **Range**: 69 pixels, **Damage**: 1, **Fire Rate**: 0.7/sec
- Shoots tacks in 8 directions simultaneously

#### Boomerang Monkey ($430)

- **Range**: 84 pixels, **Damage**: 1, **Fire Rate**: 0.6/sec  
- Throws boomerangs that can hit multiple bloons

#### Bomb Shooter ($540)

- **Range**: 120 pixels, **Damage**: 1, **Fire Rate**: 0.8/sec
- Explosive projectiles with area damage

### Starting Resources

- **Money**: $650  
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

- **Resolution**: 1280x720
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

- More tower types and upgrades
- Additional bloon types with special abilities
- Sound effects and music
- Multiple maps and game modes
- Mobile support? (Unlikely. Would need to port game to mobile compatible language / SDK)
- Multiplayer co-op mode (Low chance, not impossible. Would need a lot of work on a serverside, possibly building off of my firebase app)
