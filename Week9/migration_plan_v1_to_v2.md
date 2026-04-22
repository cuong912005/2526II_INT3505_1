# Kế hoạch Nâng cấp (Migration Plan): Payment API v1 sang v2

## 1. Mục tiêu và Lý do Nâng cấp (Why)
- **Hỗ trợ Đa tiền tệ (Multi-currency):** API v1 hiện tại chỉ hỗ trợ USD (`amount_usd`). Hệ thống cần mở rộng sang các thị trường quốc tế (EUR, VND, JPY).
- **Chuẩn hóa Trạng thái (Status Normalization):** Các giá trị trạng thái thanh toán trong v1 không đồng nhất. v2 sẽ sử dụng Enum UPPERCASE tiêu chuẩn (VD: `COMPLETED`, `PENDING`, `FAILED`).
- **Cải thiện Hiệu suất:** Tối ưu hóa backend queries cho tập dữ liệu lớn.

## 2. Chi tiết Breaking Changes (What)
Đây là các thay đổi có thể làm vỡ ứng dụng của client nếu họ không cập nhật code:

### 2.1. Cấu trúc Response
- **v1:** 
  ```json
  { "id": 1, "amount_usd": 50.0, "status": "completed" }
  ```
- **v2:** Field `amount_usd` bị xóa. Thay bằng object nested `amount`.
  ```json
  { "id": 1, "amount": { "value": 50.0, "currency": "USD" }, "status": "COMPLETED" }
  ```

### 2.2. Payload Request (POST /payments)
- **v1:** Gửi `amount_usd` (float).
- **v2:** Bắt buộc gửi `amount` object. Nếu không có `currency`, mặc định sẽ trả về lỗi `400 Bad Request` thay vì tự động nhận USD.

## 3. Chiến lược Versioning
Sử dụng **URL Versioning** (`/api/v1/payments` -> `/api/v2/payments`) do hệ thống thanh toán cần URL rõ ràng, cấu trúc cache mạch lạc và thuận tiện nhất cho developer của đối tác tích hợp.

## 4. Lộ trình (Timeline & Milestones)

| Giai đoạn | Thời gian | Hành động | Trạng thái API |
| :--- | :--- | :--- | :--- |
| **1. Công bố (Announce)** | Ngày 01/06/2026 | Ra mắt API v2. Gửi email thông báo cho tất cả developers. Cập nhật tài liệu (Swagger/Redoc). | v1: Active <br>v2: Active |
| **2. Đánh dấu Deprecated** | Ngày 01/09/2026 | Gắn cảnh báo `Deprecation` vào HTTP Header của API v1 (`Warning: 299 - "API v1 is deprecated"`). | v1: Deprecated <br>v2: Active |
| **3. Brownout (Thử nghiệm rớt mạng)** | Ngày 15/11/2026 | Bắt đầu trả về lỗi `503 Service Unavailable` xen kẽ (1% -> 5% requests) trong 2 tuần tiếp theo đối với v1 để báo động những ai chưa chuyển đổi. | v1: Brownout <br>v2: Active |
| **4. Khai tử (Sunset / End of Life)** | Ngày 01/12/2026 | Tắt hoàn toàn v1. Mọi request vào v1 sẽ nhận `410 Gone` hoặc chuyển hướng `301 Moved Permanently` (nếu an toàn). | v1: Offline <br>v2: Active |

## 5. Hỗ trợ Developer (Support Strategy)
- Cung cấp **Migration Guide** chi tiết trên Developer Portal kèm code snippets bằng nhiều ngôn ngữ (Python, JS, Java).
- Thêm endpoint `/api/v1/to_v2_checker` để dev kiểm tra xem payload v1 của họ sẽ trông như thế nào ở v2.
- Team Support chủ động rà soát logs và gửi email nhắc nhở riêng cho các top-tier clients (có lượng traffic v1 cao nhất) vào tháng 10.
