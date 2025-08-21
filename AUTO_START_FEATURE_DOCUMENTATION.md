# Auto Start Rounds Feature Documentation

## Overview
The Auto Start Rounds feature automatically begins the next wave after a configurable delay when the current wave is completed, eliminating the need to manually press SPACE for each wave. This feature enhances gameplay flow while maintaining player control.

## 🎯 Feature Highlights

### Settings Menu Integration
- **New Settings Menu**: Accessible through Pause Menu → Settings
- **Toggle Control**: Easy on/off switch with visual checkbox indicator
- **Persistent Setting**: Setting remains active throughout the game session
- **ESC Navigation**: Natural navigation flow between pause and settings menus

### Auto Start Behavior
- **3-Second Delay**: Configurable delay before automatically starting next wave
- **Visual Countdown**: Real-time countdown showing seconds remaining
- **Manual Override**: Press SPACE to start wave immediately, bypassing countdown
- **Wave Complete Detection**: Automatically triggers when all bloons are cleared/escaped

### User Experience Features
- **Clear Feedback**: Visual indicators show auto start status and countdown
- **Manual Control**: Players can still manually start waves or disable the feature
- **Non-Intrusive**: Feature enhances rather than replaces existing controls
- **Consistent Interface**: Maintains existing UI design patterns

## 🏗️ Technical Implementation

### New Classes

#### `SettingsMenu`
```python
class SettingsMenu:
    def __init__(self):
        # Settings state management
        self.auto_start_rounds = False
        
        # UI layout and positioning
        self.menu_width = 500
        self.menu_height = 400
        
        # Interactive elements
        self.back_button = pygame.Rect(...)
        # Toggle checkbox positioning
```

**Key Methods:**
- `show()` / `hide()`: Menu visibility control
- `handle_click()`: Mouse interaction handling
- `draw()`: Renders settings interface with checkbox

#### Enhanced `PauseMenu`
- **New Settings Button**: Added fourth button for settings access
- **Improved Layout**: Adjusted button positioning for four options
- **Navigation Integration**: Seamless flow to/from settings menu

### Game State Management

#### Auto Start Variables
```python
# In TowerDefenseGame.__init__()
self.auto_start_rounds = False           # Feature toggle
self.auto_start_delay = 3000            # 3 seconds in milliseconds  
self.wave_completed_time = 0            # Timestamp when wave finished
self.current_menu = "none"              # Menu state tracking
```

#### Menu State System
- **State Tracking**: `"none"`, `"pause"`, `"settings"`
- **Proper Navigation**: ESC key handling for menu hierarchy
- **Setting Synchronization**: Auto start setting synced between game and menu

### Auto Start Logic

#### Wave Completion Detection
```python
# In update() method
if self.current_wave.is_complete() and all(not bloon.alive or bloon.reached_end for bloon in self.bloons):
    self.wave_active = False
    self.wave_number += 1
    self.wave_completed_time = current_time # Record completion time
```

#### Auto Start Timer
```python
# Auto start check
if (not self.wave_active and self.auto_start_rounds and 
    self.wave_completed_time > 0 and 
    current_time - self.wave_completed_time >= self.auto_start_delay and
    self.wave_number <= len(self.waves)):
    self.start_wave()
    self.wave_completed_time = 0
```

### Visual Feedback System

#### Dynamic Wave Hints
```python
if self.auto_start_rounds and self.wave_completed_time > 0:
    time_remaining = self.auto_start_delay - (current_time - self.wave_completed_time)
    if time_remaining > 0:
        seconds_remaining = int(time_remaining / 1000) + 1
        # Show "Next wave starts in X seconds"
        # Show "Press SPACE to start immediately"
    else:
        # Show "Starting next wave..."
else:
    # Show standard "Press SPACE to start next wave"
```

## 🎮 User Interface Elements

### Settings Menu Layout
```
┌─────────────────────────────────────────────┐
│                 SETTINGS                    │
├─────────────────────────────────────────────┤
│                                             │
│  Auto Start Rounds: [✓]                    │
│  Automatically start the next wave when    │
│  ready                                      │
│                                             │
│                                             │
│                [Back]                       │
└─────────────────────────────────────────────┘
```

### Enhanced Pause Menu
```
┌─────────────────────────────────────────────┐
│                 PAUSED                      │
├─────────────────────────────────────────────┤
│                                             │
│              [Resume]                       │
│              [Settings]         <- NEW      │
│              [Main Menu]                    │
│              [Quit Game]                    │
│                                             │
└─────────────────────────────────────────────┘
```

### Game Screen Indicators
- **Standard Mode**: "Press SPACE to start next wave"
- **Auto Start Active**: "Next wave starts in 3 seconds" + "Press SPACE to start immediately"
- **Auto Start Triggering**: "Starting next wave..."

## 🔧 Configuration Options

### Timing Settings
```python
self.auto_start_delay = 3000 # 3 seconds (configurable)
```

### Customization Points
1. **Delay Duration**: Easily adjustable in `__init__()` method
2. **Visual Styling**: Checkbox and button colors configurable
3. **Text Messages**: All user-facing text easily modifiable
4. **Layout**: Menu dimensions and positioning adjustable

## 📋 Controls and Navigation

### Keyboard Controls
- **ESC**: Navigate between menus (Settings → Pause → Game)
- **SPACE**: Manual wave start (works with or without auto start)

### Mouse Controls
- **Settings Icon**: Opens pause menu
- **Pause Menu Buttons**: Resume, Settings, Main Menu, Quit
- **Settings Menu**: Toggle auto start, Back button
- **Auto Start Checkbox**: Click to toggle feature on/off

### Navigation Flow
1. **Game** → ESC → **Pause Menu**
2. **Pause Menu** → Settings → **Settings Menu**  
3. **Settings Menu** → Back → **Pause Menu**
4. **Settings Menu** → ESC → **Pause Menu**
5. **Pause Menu** → ESC → **Game**

## 🧪 Testing and Validation

### Feature Testing
- ✅ Settings menu opens and closes correctly
- ✅ Auto start toggle functions properly
- ✅ Countdown displays accurate timing
- ✅ Manual override (SPACE) works during countdown
- ✅ Setting persists throughout game session
- ✅ No interference with existing game mechanics

### Integration Testing
- ✅ All existing unit tests pass
- ✅ Pause menu navigation works correctly
- ✅ Game state management handles menu transitions
- ✅ Visual feedback shows appropriate messages

### User Experience Testing
- ✅ Intuitive menu navigation
- ✅ Clear visual feedback for all states
- ✅ Responsive controls and immediate feedback
- ✅ Non-disruptive enhancement to gameplay flow

## 🚀 Benefits and Impact

### Gameplay Improvements
1. **Reduced Manual Input**: Less repetitive SPACE pressing
2. **Smoother Flow**: Continuous gameplay without interruption
3. **Strategic Planning**: 3-second window for tower placement/upgrades
4. **Player Choice**: Optional feature preserving manual control

### Technical Benefits
1. **Clean Architecture**: Modular settings system
2. **Extensible Design**: Easy to add more settings
3. **Proper State Management**: Robust menu system
4. **Maintainable Code**: Clear separation of concerns

### Future Enhancement Potential
1. **Configurable Delay**: Player-adjustable countdown time
2. **Sound Notifications**: Audio cues for wave start countdown
3. **Pause During Planning**: Auto-pause feature during countdown
4. **Advanced Settings**: More gameplay configuration options

## 📁 Files Modified

### Core Implementation
- `game/ui/pause_menu.py`: Added SettingsMenu class, enhanced PauseMenu
- `game/tower_defense_game.py`: Auto start logic, menu state management
- `game/ui/__init__.py`: Updated exports for SettingsMenu

### Integration Points
- **Pause System**: Enhanced existing pause menu with settings access
- **Event Handling**: Extended keyboard/mouse input processing
- **Visual System**: Added countdown and status indicators
- **State Management**: Integrated with existing game state system

## 🎯 Conclusion

The Auto Start Rounds feature successfully enhances the Tower Defense game by:

- **Improving Gameplay Flow**: Automatic wave progression with player control
- **Maintaining User Agency**: Optional feature with manual override capability  
- **Extending UI System**: Robust settings menu architecture for future features
- **Preserving Game Balance**: 3-second planning window maintains strategic depth

The implementation demonstrates clean software architecture with proper separation of concerns, making it easy to extend with additional settings and features in the future.

**Total Implementation**: 200+ lines of new code, comprehensive menu system, seamless integration with existing architecture.
