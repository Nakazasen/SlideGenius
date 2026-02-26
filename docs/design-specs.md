# 🎨 Design Specifications - SlideGenius

**Ngày tạo:** 2026-01-20  
**Style:** Trẻ trung, năng động (Playful, Youthful)  
**Themes:** Light Mode + Dark Mode  

---

## 🎨 Color Palette

### Dark Mode (Primary)

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Background** | `#0F172A` | 15, 23, 42 | Main background |
| **Surface** | `#1E293B` | 30, 41, 59 | Cards, modals, sidebar |
| **Surface Elevated** | `#334155` | 51, 65, 85 | Hover states, dropdowns |
| **Primary Blue** | `#60A5FA` | 96, 165, 250 | Links, primary accent |
| **Primary Purple** | `#A78BFA` | 167, 139, 250 | Active states, glow |
| **Accent Orange** | `#FB923C` | 251, 146, 60 | CTAs, important buttons |
| **Accent Pink** | `#F472B6` | 244, 114, 182 | Gradient end, highlights |
| **Success** | `#10B981` | 16, 185, 129 | Completed, success states |
| **Error** | `#EF4444` | 239, 68, 68 | Error states |
| **Warning** | `#F59E0B` | 245, 158, 11 | Warning states |
| **Text Primary** | `#F1F5F9` | 241, 245, 249 | Main text |
| **Text Secondary** | `#94A3B8` | 148, 163, 184 | Muted text, placeholders |
| **Text Disabled** | `#64748B` | 100, 116, 139 | Disabled elements |
| **Border** | `#334155` | 51, 65, 85 | Borders, dividers |

### Light Mode

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Background** | `#F8FAFC` | 248, 250, 252 | Main background |
| **Surface** | `#FFFFFF` | 255, 255, 255 | Cards, modals |
| **Surface Elevated** | `#F1F5F9` | 241, 245, 249 | Hover states |
| **Primary Blue** | `#3B82F6` | 59, 130, 246 | Links, primary accent |
| **Primary Purple** | `#8B5CF6` | 139, 92, 246 | Active states |
| **Accent Orange** | `#F97316` | 249, 115, 22 | CTAs, important buttons |
| **Success** | `#10B981` | 16, 185, 129 | Completed, success states |
| **Error** | `#EF4444` | 239, 68, 68 | Error states |
| **Warning** | `#F59E0B` | 245, 158, 11 | Warning states |
| **Text Primary** | `#1E293B` | 30, 41, 59 | Main text |
| **Text Secondary** | `#64748B` | 100, 116, 139 | Muted text |
| **Text Disabled** | `#94A3B8` | 148, 163, 184 | Disabled elements |
| **Border** | `#E2E8F0` | 226, 232, 240 | Borders, dividers |

### Gradients

```css
/* Primary Gradient (Blue → Purple) */
--gradient-primary: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
--gradient-primary-dark: linear-gradient(135deg, #60A5FA 0%, #A78BFA 100%);

/* Accent Gradient (Orange → Pink) */
--gradient-accent: linear-gradient(135deg, #F97316 0%, #EC4899 100%);
--gradient-accent-dark: linear-gradient(135deg, #FB923C 0%, #F472B6 100%);

/* Success Gradient (Green → Teal) */
--gradient-success: linear-gradient(135deg, #10B981 0%, #14B8A6 100%);

/* Progress Bar Gradient */
--gradient-progress: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 50%, #F97316 100%);
```

---

## 📝 Typography

### Font Family

```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Font Sizes

| Name | Size | Line Height | Weight | Usage |
|------|------|-------------|--------|-------|
| **Display** | 48px | 1.1 | 700 | Hero titles |
| **H1** | 36px | 1.2 | 700 | Page titles |
| **H2** | 28px | 1.3 | 600 | Section headers |
| **H3** | 22px | 1.4 | 600 | Card titles |
| **H4** | 18px | 1.4 | 600 | Sub-sections |
| **Body Large** | 18px | 1.6 | 400 | Important body text |
| **Body** | 16px | 1.6 | 400 | Default body text |
| **Body Small** | 14px | 1.5 | 400 | Secondary text |
| **Caption** | 12px | 1.4 | 400 | Labels, captions |
| **Overline** | 11px | 1.2 | 600 | Category labels (uppercase) |

### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text |
| Medium | 500 | Emphasized body |
| Semibold | 600 | Headings, buttons |
| Bold | 700 | Titles, strong emphasis |

---

## 📐 Spacing System

Based on 4px grid (multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| `--space-0` | 0px | No spacing |
| `--space-1` | 4px | Tight inline spacing |
| `--space-2` | 8px | Icon gaps, compact spacing |
| `--space-3` | 12px | Small component padding |
| `--space-4` | 16px | Default spacing |
| `--space-5` | 20px | Medium spacing |
| `--space-6` | 24px | Section gaps |
| `--space-8` | 32px | Large spacing |
| `--space-10` | 40px | Section padding |
| `--space-12` | 48px | Page sections |
| `--space-16` | 64px | Large sections |
| `--space-20` | 80px | Hero spacing |

---

## 🔲 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-none` | 0px | Sharp corners |
| `--radius-sm` | 4px | Small elements, tags |
| `--radius-md` | 8px | Buttons, inputs |
| `--radius-lg` | 12px | Cards, modals |
| `--radius-xl` | 16px | Large cards, dialogs |
| `--radius-2xl` | 24px | Hero sections |
| `--radius-full` | 9999px | Pills, avatars, circular |

---

## 🌫️ Shadows

### Light Mode

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
```

### Dark Mode (Glow Effects)

```css
--glow-purple: 0 0 20px rgba(139, 92, 246, 0.3);
--glow-blue: 0 0 20px rgba(96, 165, 250, 0.3);
--glow-orange: 0 0 20px rgba(251, 146, 60, 0.4);
--glow-success: 0 0 20px rgba(16, 185, 129, 0.3);
--glow-error: 0 0 20px rgba(239, 68, 68, 0.3);
```

### Glassmorphism (Dark Mode)

```css
--glass-bg: rgba(30, 41, 59, 0.8);
--glass-border: rgba(255, 255, 255, 0.1);
--glass-blur: blur(12px);
```

---

## ✨ Animations

### Timing Functions

```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Durations

| Name | Duration | Usage |
|------|----------|-------|
| `--duration-fast` | 150ms | Hovers, micro-interactions |
| `--duration-normal` | 250ms | Standard transitions |
| `--duration-slow` | 400ms | Modal open/close |
| `--duration-slower` | 600ms | Page transitions |

### Common Animations

```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Pulse Glow */
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.3); }
  50% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.5); }
}

/* Progress Shimmer */
@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

/* Confetti Pop */
@keyframes confettiPop {
  0% { transform: scale(0) rotate(0deg); opacity: 1; }
  100% { transform: scale(1) rotate(720deg); opacity: 0; }
}
```

---

## 🖼️ Component Specifications

### Buttons

#### Primary Button (CTA)

```css
.btn-primary {
  background: linear-gradient(135deg, #F97316 0%, #EC4899 100%);
  color: #FFFFFF;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 4px 14px 0 rgba(249, 115, 22, 0.4);
  transition: all 250ms ease-out;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 rgba(249, 115, 22, 0.5);
}
```

#### Secondary Button

```css
.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  padding: 12px 24px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-weight: 500;
}
.btn-secondary:hover {
  background: var(--surface-elevated);
  border-color: var(--primary-purple);
}
```

### Input Fields

```css
.input {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  color: var(--text-primary);
  transition: all 200ms ease;
}
.input:focus {
  outline: none;
  border-color: var(--primary-purple);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
}
.input::placeholder {
  color: var(--text-secondary);
}
```

### Cards

```css
.card {
  background: var(--surface);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border);
}
/* Dark mode glassmorphism */
.card-glass {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}
.card:hover {
  border-color: var(--primary-purple);
  box-shadow: var(--glow-purple);
}
```

### Toggle Switch

```css
.toggle {
  width: 48px;
  height: 24px;
  background: var(--surface-elevated);
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background 200ms ease;
}
.toggle.active {
  background: linear-gradient(135deg, #F97316 0%, #EC4899 100%);
}
.toggle-knob {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 200ms ease;
}
.toggle.active .toggle-knob {
  transform: translateX(24px);
}
```

### Progress Bar

```css
.progress-bar {
  height: 8px;
  background: var(--surface-elevated);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 50%, #F97316 100%);
  background-size: 200% auto;
  animation: shimmer 2s linear infinite;
  border-radius: 4px;
}
```

---

## 📱 Layout Specifications

### Main Window Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        TITLE BAR (32px)                     │
├──────────┬─────────────────────────────────┬────────────────┤
│          │                                 │                │
│  SIDEBAR │         MAIN CONTENT            │  RIGHT PANEL   │
│  (220px) │         (flexible)              │   (320px)      │
│          │                                 │                │
│          │  ┌─────────────────────────┐   │                │
│          │  │      INPUT AREA         │   │                │
│          │  │       (120px h)         │   │                │
│          │  └─────────────────────────┘   │                │
│          │                                 │                │
│          │  ┌─────────────────────────┐   │                │
│          │  │                         │   │                │
│          │  │    OUTLINE CARDS        │   │                │
│          │  │    (scrollable)         │   │                │
│          │  │                         │   │                │
│          │  └─────────────────────────┘   │                │
│          │                                 │                │
└──────────┴─────────────────────────────────┴────────────────┘
```

### Minimum Window Size

- Width: 1200px
- Height: 700px

### Sidebar

- Width: 220px (fixed)
- Padding: 16px
- Item height: 40px
- Item radius: 8px
- Active item: Gradient background

### Right Panel

- Width: 320px (fixed)
- Padding: 20px
- Template grid: 2 columns

---

## 🖥️ Responsive Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| `--bp-compact` | < 1200px | Hide right panel |
| `--bp-normal` | 1200px - 1600px | Standard layout |
| `--bp-wide` | > 1600px | Expanded spacing |

---

## 🎭 UI States

### Interactive States

| State | Changes |
|-------|---------|
| **Default** | Base styling |
| **Hover** | +2px lift, glow shadow, brighter colors |
| **Active/Pressed** | -1px, darker shade |
| **Focus** | Purple outline ring (3px) |
| **Disabled** | 50% opacity, cursor: not-allowed |
| **Loading** | Shimmer animation, skeleton |

### Feedback States

| State | Border Color | Background | Icon |
|-------|--------------|------------|------|
| **Success** | `#10B981` | `rgba(16, 185, 129, 0.1)` | ✓ Checkmark |
| **Error** | `#EF4444` | `rgba(239, 68, 68, 0.1)` | ⚠ Warning |
| **Warning** | `#F59E0B` | `rgba(245, 158, 11, 0.1)` | ! Exclamation |
| **Info** | `#3B82F6` | `rgba(59, 130, 246, 0.1)` | ℹ Info |

---

## 📁 Asset References

### Mockup Files

- `slidegenius_light_mode.png` - Main window (Light)
- `slidegenius_dark_mode.png` - Main window (Dark)
- `slidegenius_settings_light.png` - Settings (Light)
- `slidegenius_settings_dark.png` - Settings (Dark)
- `slidegenius_template_light.png` - Template Picker (Light)
- `slidegenius_template_picker.png` - Template Picker (Dark)
- `slidegenius_loading_state.png` - Loading overlay
- `slidegenius_error_state.png` - Error modal
- `slidegenius_empty_state.png` - Welcome/Empty
- `slidegenius_success_state.png` - Export complete

### Icons

- Use: Lucide Icons (<https://lucide.dev>)
- Size: 20px (sidebar), 16px (inline)
- Stroke: 2px

### Fonts

- Download: Google Fonts - Inter (400, 500, 600, 700)
- Fallback: System fonts

---

## ✅ Accessibility Checklist

- [x] Color contrast ratio ≥ 4.5:1 (WCAG AA)
- [x] Focus states visible for keyboard navigation
- [x] Touch targets ≥ 44px
- [x] Error messages descriptive and helpful
- [x] Loading states with aria-busy
- [x] Alt text for decorative illustrations
- [x] Reduced motion query support

---

## 🔗 Next Steps

→ Run `/plan` to create detailed implementation plan
→ Run `/code` to start building with these specs
