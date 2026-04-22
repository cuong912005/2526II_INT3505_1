**Subject:** Quan trọng: Nâng cấp Payment API v2 và Kế hoạch Khai tử API v1

Kính gửi Quý Developer,

Chúng tôi xin trân trọng thông báo việc phát hành chính thức **Payment API v2**, nhằm mang lại khả năng hỗ trợ Đa tiền tệ (Multi-currency) và cấu trúc dữ liệu chuẩn hóa, an toàn hơn.

Cùng với việc ra mắt này, **Payment API v1 sẽ chính thức bị đánh dấu là lỗi thời (Deprecated) và sẽ ngừng hoạt động hoàn toàn vào ngày 01 tháng 12 năm 2026.**

### Tại sao lại có sự thay đổi này?
Hệ thống v1 hiện tại giới hạn ở mức tiền tệ mặc định (USD). Để hỗ trợ quý đối tác mở rộng thị trường quốc tế, chúng tôi đã tái cấu trúc API để hỗ trợ nhiều mã tiền tệ ISO-4217, đồng thời chuẩn hóa các trường trạng thái thanh toán.

### Những thay đổi chính trong API v2 (Breaking Changes)
1. **Thay thế trường `amount_usd`:** Trường này đã bị xóa bỏ. Số tiền thanh toán giờ đây được đóng gói trong một object `amount` bao gồm hai trường `value` (số tiền) và `currency` (mã tiền tệ, e.g., "USD", "EUR").
2. **Trạng thái Enum:** Các trạng thái trả về tại trường `status` (ví dụ: `completed`, `pending`) sẽ đổi thành chữ in hoa chữ (`COMPLETED`, `PENDING`).

**Ví dụ Payload v2:**
```json
// Cũ (v1)
{
  "amount_usd": 150.5,
  "status": "completed"
}

// Mới (v2)
{
  "amount": {
    "value": 150.5,
    "currency": "USD"
  },
  "status": "COMPLETED"
}
```

### Lịch trình Chuyển đổi (Timeline)
- **Hôm nay (01/06):** API v2 chính thức hoạt động.
- **01/09/2026:** API v1 bắt đầu trả về cảnh báo `Warning` trong HTTP Header.
- **15/11/2026:** Giai đoạn Brownout - Hệ thống sẽ ngẫu nhiên từ chối một lượng nhỏ các requests vào v1 để giả lập việc ngừng hoạt động.
- **01/12/2026 (Ngày ngưng hoạt động - Sunset):** API v1 sẽ ngừng hoạt động hoàn toàn. Các truy cập vào v1 sẽ nhận mã lỗi `410 Gone`.

### Hành động cần thực hiện
Vui lòng cập nhật ứng dụng của quý vị để chuyển sang sử dụng các endpoint `/api/v2/*` trước thời hạn Sunset để đảm bảo dịch vụ không bị gián đoạn.

Xem hướng dẫn nâng cấp chi tiết tại: [Link_toi_developer_portal/migration-v1-v2]

Nếu quý vị có bất kỳ câu hỏi nào hoặc cần hỗ trợ trong quá trình chuyển đổi, xin vui lòng liên hệ đội ngũ Hỗ trợ Nhà phát triển tại địa chỉ `api-support@yourcompany.com`.

Trân trọng,
Đội ngũ Nền tảng Thanh toán
