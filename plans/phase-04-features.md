# Phase 04: AI & Outline Features

**Status:** ✅ Complete  
**Dependencies:** Phase 03  
**Estimated Time:** 2-3 hours

---

## 🎯 Objective

Xây dựng tính năng chính: Input Panel, AI generate outline, Outline Editor.

---

## 📋 Tasks

### 1. Input Panel Component

- [ ] `src/ui/components/input_panel.py`
- [ ] TextEdit cho prompt input
- [ ] Upload button (placeholder)
- [ ] "Generate" button

### 2. Outline Editor Component

- [ ] `src/ui/components/outline_editor.py`
- [ ] Hiển thị danh sách slide cards
- [ ] Drag & drop reorder
- [ ] Edit/Delete từng slide

### 3. Settings Dialog

- [ ] `src/ui/dialogs/settings_dialog.py`
- [ ] Tab: AI Settings (API Key, Model selection)
- [ ] Tab: About
- [ ] Test Connection button

### 4. Connect AI Service

- [ ] Gọi AIService.generate_outline()
- [ ] Hiển thị loading state
- [ ] Hiển thị error state
- [ ] Populate Outline Editor với kết quả

### 5. Template Picker (Right Panel)

- [ ] `src/ui/components/template_picker.py`
- [ ] Grid hiển thị 5 templates
- [ ] Select template

---

## 🧪 Test Criteria

- [ ] Nhập prompt → Generate → Outline hiển thị
- [ ] Settings dialog lưu API key
- [ ] Test Connection hoạt động
- [ ] Outline cards có thể edit/delete

---

**Next:** [Phase 05 - PPTX Generation](phase-05-pptx.md)
