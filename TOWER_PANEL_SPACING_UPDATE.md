# Tower Panel Spacing Balance Update

## Change Summary
Adjusted the spacing between the left tower selection panel and the right upgrade display panel to create better visual balance.

## Technical Details

### Previous Layout:
- Left panel (sidebar): 380px width
- Space between panels: 20px
- Right panel start position: 400px (380 + 20)
- Right panel width: 860px (1280 - 400 - 20)

### Updated Layout:
- Left panel (sidebar): 380px width  
- Space between panels: 15px (reduced from 20px)
- Right panel start position: 395px (380 + 15)
- Right panel width: 865px (1280 - 395 - 20)

### Code Changes
In `game/ui/tower_upgrades_screen.py`, line 233:
```python
# Before:
self.upgrade_panel_x = self.sidebar_width + 20

# After: 
self.upgrade_panel_x = self.sidebar_width + 15  # Reduced from 20 to 15 for better balance
```

## Result
- More balanced spacing between left and right panels
- Tower cards maintain their 20px left margin
- Right panel gets slightly more space (865px vs 860px)
- Visual improvement with better proportional spacing

## Testing
- ✅ Compilation successful
- ✅ All unit tests pass
- ✅ Application launches correctly
- ✅ No visual regressions
