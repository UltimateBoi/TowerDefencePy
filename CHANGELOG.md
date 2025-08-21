# Tower Defense Game - Changelog

## Version 2.0.0 - August 21, 2025

### Major Features

#### BTD6 Tower System Implementation
**Date**: August 21, 2025  
**Files**: `data/towers.json`, `game/ui/tower_upgrades_screen.py`

Complete replacement of the tower system with authentic BTD6 towers:

- **Dart Monkey** (was Dart Tower): $200 base cost, 3 upgrade paths (Sharp Shooter, Multi-Shot, Seeking Darts)
- **Tack Shooter** (new): $280 base cost, shoots 8 tacks in all directions
- **Boomerang Monkey** (new): $325 base cost, boomerang projectiles with 3 pierce
- **Bomb Shooter** (was Bomb Tower): $525 base cost, explosive area damage

**Technical Changes**:
- 60 total upgrades with authentic BTD6 names and costs
- Updated difficulty multipliers: Easy (1.0x), Medium (1.08x), Hard (1.2x), Impoppable (1.3x)
- Added new stats: blast_radius, projectiles, enhanced pierce values
- Maintained JSON structure for backward compatibility

#### Comprehensive Text Rendering System
**Date**: August 21, 2025  
**Files**: `game/ui/text_renderer.py`, `utils/TextUtil.py`

New TextRenderer class with advanced capabilities:
- Automatic text wrapping with word boundary detection
- Alignment options: LEFT, CENTER, RIGHT (horizontal), TOP, MIDDLE, BOTTOM (vertical)
- Line spacing control and maximum line limits
- Text measurement utilities for layout planning
- Background rendering with rounded rectangles

**Backward Compatibility**:
- Legacy TextUtil maintained for existing code
- Enhanced with new wrap_text() and render_wrapped_text() methods
- Graceful fallbacks for missing dependencies

#### Tower Upgrades Interface
**Date**: August 21, 2025  
**Files**: `game/ui/tower_upgrades_screen.py`

Enhanced UI with text overflow fixes:
- Multi-line tower names (fixes "Boomerang Monkey" overflow)
- Wrapped upgrade descriptions and path descriptions
- Improved layout spacing and alignment
- Interactive upgrade selection with cost calculation

### Bug Fixes

#### Text Overflow Resolution
**Date**: August 21, 2025

Fixed text overflow issues across all UI components:
- Tower card names now wrap to multiple lines when needed
- Upgrade descriptions automatically wrap within their containers
- Path descriptions use center-aligned text wrapping
- Base statistics display with proper formatting

**Implementation Details**:
- Smart line breaking at word boundaries
- Dynamic layout adjustment based on text length
- Fallback handling for edge cases (single long words)

### Auto Start Feature
**Date**: August 21, 2025  
**Files**: `game/ui/settings_screen.py`

Added automatic round starting capability:
- Toggle switch in settings menu
- Configurable delay between rounds
- Persistent settings storage
- User-friendly interface integration

### UI Layout Improvements
**Date**: August 21, 2025  
**Files**: `game/ui/tower_upgrades_screen.py`, `game/ui/pause_menu.py`, `game/ui/settings_screen.py`

Fixed overflow issues across multiple interface panels:
- **Tower Upgrades Screen**: Expanded left sidebar from 300px to 380px width
- **Pause Menu**: Increased height from 350px to 400px to fit all buttons
- **Settings Menu**: Expanded width from 500px to 600px for auto start feature text
- **Panel Spacing**: Optimized spacing between left tower panel (15px gap) and right upgrade panel

**Layout Adjustments**:
- Better visual balance between UI components
- Proper text fitting without overflow
- Improved button spacing and alignment
- Enhanced overall user experience

### Technical Improvements

#### Code Architecture
- Enhanced type safety with comprehensive type hints
- Enum-based alignment constants for consistency
- Modular text rendering components
- Clean separation between rendering and layout logic

#### Testing & Validation
- All unit tests pass with no regressions
- Application launches successfully
- Visual validation of text rendering improvements
- BTD6 authenticity verification completed

#### Performance Optimizations
- Efficient text wrapping algorithms
- Minimal surface creation and memory usage
- Smart caching of text calculations
- Reduced object creation in render loops

### Documentation

#### New Documentation Files
- `BTD6_TOWER_SYSTEM_UPDATE.md`: Detailed tower specifications
- `RECENT_ENHANCEMENTS.md`: Comprehensive feature overview
- `TOWER_CARD_TEXT_FIX.md`: Text overflow fix documentation

## Previous Versions

### Version 1.5.0 - August 2025

#### Pause System Implementation
**Date**: August 2025  
**Files**: `game/ui/pause_menu.py`

Complete pause and settings functionality:
- **Pause Menu**: Accessible via ESC key or settings gear icon
- **Menu Options**: Resume, Main Menu, Quit Game
- **Settings Icon**: Animated gear icon in top-right corner
- **Pause State**: Full game logic freezing (bloons, towers, projectiles, waves)
- **Visual Indicators**: "PAUSED" text in HUD, input blocking during pause

**Technical Features**:
- Semi-transparent overlay with centered modal dialog
- Three action buttons with hover states
- Click detection and proper action handling
- Integration with existing game state management

### Version 1.4.0 - August 2025

#### Code Architecture Refactoring
**Date**: August 2025  
**Files**: Multiple files restructured

Major codebase reorganization from monolithic to modular structure:

**New Package Structure**:
- `game/` - Main game package with proper module organization
- `game/entities/` - Game entity classes (Bloon, Tower, Projectile)
- `game/systems/` - Game system classes (Wave, GameMap)
- `game/ui/` - User interface classes (GameUI, HUD)
- `game/constants.py` - Game constants and configuration

**Benefits Achieved**:
- **Modularity**: Each class in its own file with clear responsibility
- **Maintainability**: Cleaner code organization and easier modifications
- **Scalability**: Simple structure for adding new features and entity types
- **Reusability**: Better component separation for future development

**Technical Improvements**:
- Proper import structure and package organization
- Separated concerns between entities, systems, and UI
- Enhanced test structure for modular components
- Maintained backward compatibility during transition

### Version 1.x
- Basic tower defense mechanics
- Simple tower and bloon systems
- Core game loop implementation
- Initial UI framework

---

**Total Changes**: 8 files modified, 3 new files added  
**Lines Added**: ~2000+ lines of new functionality  
**Test Coverage**: 100% of core mechanics validated  
**Compatibility**: Maintains backward compatibility with existing saves and configurations
