# 💡 BRIEF: Express Mode (Tạo Nhanh)

**Ngày tạo:** 2026-02-04
**Trạng thái:** Brainstorming

---

## 1. VẤN ĐỀ CẦN GIẢI QUYẾT

- Hiện tại user phải đi qua 2 bước: Tạo Outline -> Sửa Outline -> Tạo Slide.
- Đôi khi user muốn "mì ăn liền", tin tưởng vào AI và muốn thấy kết quả cuối cùng ngay lập tức.
- Quy trình hiện tại hơi dài dòng cho các nhu cầu demo nhanh.

## 2. GIẢI PHÁP ĐỀ XUẤT

Thêm chế độ **"Tạo Nhanh" (Express Mode)** tại màn hình chính.

### Flow Mới

1. **Home Screen:** User nhập Prompt + Số slide.
2. **Template Selection:** User chọn Template ngay tại màn hình này (hoặc popup).
3. **Action:** Bấm nút "Tạo Ngay" (bên cạnh nút "Tạo Dàn Ý").
4. **Processing:**
   - AI tạo Outline ngầm.
   - AI tự động điền nội dung vào các slide.
   - App tự động chuyển sang màn hình Editor.
5. **Result:** Hiển thị Slide đã hoàn thiện trong Editor. User có thể sửa tiếp hoặc Export ngay.

## 3. TÍNH NĂNG (MVP)

- [ ] Thêm Toggle/Tab "Chế độ: Cơ bản / Nhanh" hoặc nút mới "Express Generate".
- [ ] Cho phép chọn Template ngay ở Home Screen (hiện tại đang ở bước Export mới chọn).
- [ ] Logic gộp bước: Generate Outline -> Auto-confirm -> Show Editor.

## 4. ƯỚC TÍNH

- **Độ phức tạp:** Trung bình (Thay đổi luồng UI, tái sử dụng logic cũ).
- **Rủi ro:** Không có rủi ro lớn. Logic AI không đổi.

## 5. BƯỚC TIẾP THEO

→ Chạy `/plan` để thiết kế luồng data và UI chi tiết.
