# Tower Upgrades Screen Documentation

## Overview
The Tower Upgrades Screen is a comprehensive interface that allows players to browse all available towers and their upgrade paths, inspired by the BTD6 (Bloons Tower Defense 6) upgrade system. This feature provides a global overview of tower capabilities, upgrade costs, and multi-tier progression paths.

## Features

### 1. Display Layout
- **Sidebar Grid**: Left-side display with tower cards arranged in a 2-column grid
- **Tower Cards**: Each card shows:
  - Tower icon (colored circle representing the tower type)
  - Tower name
  - Base cost
  - Selection highlighting and hover effects
- **Upgrade Panel**: Right-side detailed view showing upgrade paths when a tower is selected

### 2. Tower Data System
- **JSON-Based Configuration**: All tower data stored in `data/towers.json`
- **Modular Design**: Easy to add new towers and upgrade paths
- **Comprehensive Stats**: Damage, range, fire rate, pierce, and special abilities

### 3. Upgrade Path System
- **Three Paths Per Tower**: Each tower has 3 distinct upgrade paths
  - Path 1: Usually damage-focused upgrades
  - Path 2: Range/speed/utility improvements
  - Path 3: Special abilities and unique mechanics
- **Five Tiers Per Path**: Progressive upgrades with increasing costs
- **Visual Tier Indicators**: Color-coded tiers (Gray → Green → Blue → Orange → Purple)

### 4. Difficulty-Based Pricing
- **Dynamic Cost Calculation**: Costs adjust based on difficulty setting
- **Difficulty Multipliers**:
  - E (Easy): 1.0x cost
  - M (Medium): 1.2x cost
  - H (Hard): 1.5x cost
  - I (Impoppable): 2.0x cost
- **Interactive Difficulty Selector**: Click to change difficulty and see updated costs

### 5. Tower Types Included

#### Dart Tower
- **Base Cost**: $100
- **Description**: Basic tower that shoots darts at bloons
- **Upgrade Paths**:
  - Damage Focus: Sharp Darts → Razor Sharp → Spike-o-pult → Juggernaut → Ultra-Juggernaut
  - Range & Speed: Long Range → Enhanced Eyesight → Crossbow → Sharp Shooter → Crossbow Master
  - Special Abilities: Multi-Shot → Triple Shot → SMFC → Plasma SMFC → Avatar of the Dart

#### Sniper Tower
- **Base Cost**: $300
- **Description**: Long range tower with high damage
- **Upgrade Paths**:
  - Damage Focus: Full Metal Jacket → Large Calibre → Deadly Precision → Maim MOAB → Cripple MOAB
  - Range & Speed: Night Vision → Shrapnel Shot → Bouncing Bullet → Supply Drop → Elite Sniper
  - Support: Flash Bomb → MOAB Stun → Semi-Automatic → Full Auto Rifle → Elite Defender

#### Bomb Tower
- **Base Cost**: $400
- **Description**: Shoots explosive bombs that damage multiple bloons
- **Upgrade Paths**:
  - Bigger Bombs: Bigger Bombs → Heavy Bombs → Really Big Bombs → Bomb Blitz → Bomb God
  - Missile Launcher: Missile Launcher → MOAB Mauler → Relentless Glue → MOAB Assassin → MOAB Eliminator
  - Cluster Bombs: Cluster Bombs → Recursive Cluster → Bomb Shooter → Phoenix Lord → Wizard Lord Phoenix

#### Ice Tower
- **Base Cost**: $250
- **Description**: Freezes bloons in place
- **Upgrade Paths**:
  - Stronger Freeze: Enhanced Freeze → Ice Shards → Metal Freeze → Snap Freeze → Absolute Zero
  - Damage Focus: Cold Snap → Ice Shards → Blizzard → Snowstorm → Ice Age
  - Arctic Wind: Arctic Wind → Snowstorm → Blizzard → Absolute Zero → Ice King

## Technical Implementation

### Class Structure

#### `TowerCard`
- Represents individual tower cards in the sidebar
- Handles selection states, hover effects, and click detection
- Renders tower icon, name, and base cost

#### `UpgradePathDisplay`
- Manages the detailed upgrade view panel
- Displays tower information, base stats, and all upgrade paths
- Handles difficulty selection and cost calculations

#### `TowerUpgradesScreen`
- Main controller class for the entire screen
- Manages layout, data loading, and event handling
- Coordinates between tower cards and upgrade display

### Data Structure (towers.json)
```json
{
  "towers": {
    "tower_id": {
      "name": "Tower Name",
      "description": "Tower description",
      "base_cost": 100,
      "base_stats": {
        "damage": 1,
        "range": 100,
        "fire_rate": 1.0
      },
      "icon_color": [139, 69, 19],
      "upgrade_paths": {
        "path1": {
          "name": "Path Name",
          "description": "Path description",
          "upgrades": [
            {
              "name": "Upgrade Name",
              "description": "Upgrade description",
              "cost": 150,
              "stats": {"damage": 2}
            }
          ]
        }
      }
    }
  },
  "difficulty_multipliers": {
    "E": 1.0,
    "M": 1.2,
    "H": 1.5,
    "I": 2.0
  }
}
```

### Integration Points

#### Main Menu Integration
- Accessed via "Towers" button on main menu
- Seamless navigation back to main menu
- Proper screen reinitialization after use

#### UI Components
- Uses existing `TextButton` and `TextUtil` utilities
- Consistent styling with game's visual theme
- Responsive mouse interaction system

## Navigation and Controls

### Mouse Controls
- **Left Click**: Select tower cards, change difficulty, navigate back
- **Hover**: Visual feedback on interactive elements

### Keyboard Controls
- **ESC**: Return to main menu (future enhancement)

### Navigation Flow
1. Main Menu → Click "Towers" button
2. Tower Upgrades Screen → Select tower from sidebar
3. View upgrade paths and costs
4. Adjust difficulty to see cost changes
5. Click "Back" to return to main menu

## Visual Design

### Color Scheme
- **Background**: Dark theme (30, 30, 30)
- **Sidebar**: Slightly lighter (40, 40, 40)
- **Cards**: Context-sensitive colors (selection, hover states)
- **Upgrade Tiers**: Progressive color coding for visual hierarchy

### Typography
- **Title**: 48pt font for main heading
- **Card Text**: 24pt for tower names, 20pt for costs
- **Upgrade Text**: 18pt for upgrade names, 14pt for descriptions

### Layout Principles
- **Sidebar Width**: 300px for tower selection
- **Grid Layout**: 2-column tower card arrangement
- **Responsive Spacing**: Consistent padding and margins
- **Visual Hierarchy**: Clear information organization

## Future Enhancements

### Planned Features
1. **Tower Purchasing**: Global currency system for unlocking upgrades
2. **Progress Tracking**: Save/load upgrade unlock states
3. **Search/Filter**: Find specific towers or upgrade types
4. **Comparison Mode**: Side-by-side tower comparisons
5. **Preview Mode**: Visual representation of upgraded towers
6. **Sound Effects**: Audio feedback for interactions
7. **Animations**: Smooth transitions and hover effects

### Technical Improvements
1. **Caching System**: Improve performance for large tower sets
2. **Localization**: Multi-language support
3. **Accessibility**: Keyboard navigation, screen reader support
4. **Mobile Support**: Touch-friendly interface adaptations

## File Structure
```
game/
├── ui/
│   ├── tower_upgrades_screen.py  # Main implementation
│   └── __init__.py               # Package exports
data/
└── towers.json                   # Tower data configuration
MainMenu.py                       # Integration point
```

## Usage Example
```python
from game.ui.tower_upgrades_screen import TowerUpgradesScreen

# Initialize the screen
upgrades_screen = TowerUpgradesScreen(1280, 720)

# Game loop
while running:
    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()
    
    result = upgrades_screen.update(events, mouse_pos)
    if result == "back":
        break
    
    upgrades_screen.draw(screen)
    pygame.display.flip()
```

This comprehensive tower upgrades system provides players with detailed information about tower capabilities while maintaining the visual style and usability standards of the main game.
