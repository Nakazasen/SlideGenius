# Phase 03: Main UI Shell

**Status:** ✅ Complete  
**Dependencies:** Phase 02  
**Estimated Time:** 1-2 hours

---

## 🎯 Objective

Xây dựng UI chính: Main Window 3 cột, Sidebar, Theme System (Light/Dark).

---

## 📋 Tasks

### 1. Theme Manager

- [ ] `src/ui/theme_manager.py` - Đổi Light/Dark theme
- [ ] `src/ui/styles/dark.qss` - Dark theme CSS
- [ ] `src/ui/styles/light.qss` - Light theme CSS

### 2. Sidebar Component  

- [ ] `src/ui/components/sidebar.py`
- [ ] Navigation: Home, History, Templates, Settings
- [ ] Highlight active item

### 3. Main Window Layout

- [ ] Update `src/app.py` với 3-column layout
- [ ] Sidebar (220px) | Content (flex) | Right Panel (320px)
- [ ] Status bar

---

## 🧪 Test Criteria

- [ ] 3-column layout hiển thị đúng
- [ ] Theme toggle hoạt động
- [ ] Sidebar navigation emit signal

---

**Next:** [Phase 04 - Features](phase-04-features.md)
