# LUCA UI Style Guide

## Core Design Principles

This document captures the essential "feel" of LUCA's UI as established in the perfect template (app/ui_templates/perfect_ui_template.py).

### Visual Identity

1. **Color Palette**
   - Primary: Purple to Pink gradient (`#8b5cf6` to `#ec4899`)
   - Background: Clean white (`#FAFBFC`)
   - Text: Dark gray (`#1F2937`) on light backgrounds
   - Borders: Subtle gray (`#E5E7EB`)
   - Hover states: Purple (`#8b5cf6`) with glow effects

2. **Typography**
   - Font: Inter (with system font fallbacks)
   - Headers: Bold with gradient effect
   - Body: Regular weight, excellent readability

### Key UI Elements

1. **Gradient Effects**
   - Headers use gradient text effect
   - Buttons have gradient backgrounds
   - Logo and branding elements use gradients
   - Creates "eye-popping" visual interest

2. **Hover Interactions**
   - Cards lift slightly and show purple border
   - Buttons glow and translate upward
   - Project cards slide horizontally (4px)
   - Subtle shadows appear on hover

3. **Minimalistic Icons**
   - SVG line icons (no emojis)
   - Clean, professional symbols
   - Examples:
     - Chart icon for analytics
     - Flask for research
     - Target for goals
     - Trending line for optimization

4. **Card Design**
   - White background
   - Subtle border
   - Rounded corners (12px)
   - Hover: Purple border + shadow
   - Clean padding and spacing

5. **Status Indicators**
   - Simple dots with pulsing animation
   - Color-coded (green for active)
   - Minimal but informative

### The "Feel"

The UI should feel:
- **Professional** - Clean, modern, suitable for quantitative work
- **Responsive** - Elements react to user interaction
- **Delightful** - Subtle animations and transitions
- **Focused** - White space and clear hierarchy
- **Premium** - High-quality details and polish

### Animation Guidelines

- Transitions: 0.3s ease
- Hover effects: Smooth and subtle
- No jarring movements
- Pulse effects for status indicators
- Slide effects for navigation

### Do's and Don'ts

**DO:**
- Use gradients for visual interest
- Keep backgrounds clean and white
- Add hover effects to interactive elements
- Use SVG icons instead of emojis
- Maintain consistent spacing
- Use subtle shadows for depth

**DON'T:**
- Use dark backgrounds (except for code blocks)
- Add too many colors
- Use emojis in the interface
- Make animations too fast or slow
- Clutter the interface
- Use harsh borders or dividers

### Reference Implementation

The perfect implementation is preserved in:
`app/ui_templates/perfect_ui_template.py`

This file should be used as the reference for all UI development to maintain the desired "feel" throughout the application.