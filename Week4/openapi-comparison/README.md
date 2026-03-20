# So sánh OpenAPI, API Blueprint, RAML, và TypeSpec

## Tổng quan

Bài so sánh này giới thiệu 4 định dạng/công cụ phổ biến để mô tả API RESTful đó là:

| Format | Mục đích | Ưu điểm | Nhược điểm | Phát triển |
|--------|---------|---------|-----------|-----------|
| **OpenAPI** | Mô tả specs dựa trên JSON/YAML | - Chuẩn công nghiệp (OAS 3.0)<br>- Tooling phong phú<br>- Sinh code tốt | - Verbose khi chi tiết<br>- Dốc học cao | Red Hat, Google, IBM |
| **API Blueprint** | Markdown-based API specification | - Dễ học, dễ đọc<br>- Syntax gần Markdown<br>- Lightweight | - Ít support tool<br>- Ít operator<br>- Ngừng phát triển | Apiary (ngừng) |
| **RAML** | RESTful API Modeling Language | - Reutilizable (traits)<br>- Type hỗ trợ tốt<br>- DRY principle | - Cộng đồng nhỏ<br>- Ít adoption<br>- Syntax khó học | MuleSoft |
| **TypeSpec** | Mới nhất, dựa trên TypeScript | - Hiện đại, type-safe<br>- Syntax quen thuộc với lập trình viên<br>- Dễ mở rộng | - Mới (v0.x)<br>- Ecosystem chưa chín<br>- Documentation còn thiếu | Microsoft |

## Cấu trúc project

```
0_OpenAPI/
  ├── openapi.yaml           # OpenAPI 3.0 specification
  └── README.md              # Hướng dẫn cài đặt & sinh code

1_APIBlueprint/
  ├── api.apib               # API Blueprint format
  └── README.md              # Hướng dẫn cài đặt & sinh code

2_RAML/
  ├── api.raml               # RAML 1.0 specification
  └── README.md              # Hướng dẫn cài đặt & sinh code

3_TypeSpec/
  ├── main.tsp               # TypeSpec definition
  ├── models.tsp             # Data models
  └── README.md              # Hướng dẫn cài đặt & sinh code

SLIDE_CONTENT.md             # Nội dung so sánh chi tiết
```

## API Demo: Book Management CRUD

Tất cả các định dạng đều sử dụng cùng một API CRUD để quản lý sách:

### Resource: Book
- **GET /books** - Lấy danh sách sách
- **POST /books** - Tạo sách mới
- **GET /books/{id}** - Lấy chi tiết sách
- **PUT /books/{id}** - Cập nhật sách
- **DELETE /books/{id}** - Xóa sách

### Book Schema
```json
{
  "id": "uuid",
  "title": "string (required)",
  "author": "string (required)",
  "isbn": "string",
  "publishYear": "integer",
  "price": "number",
  "category": "string"
}
```

## Quick Start

### 1. OpenAPI (Khuyên dùng)
```bash
cd 0_OpenAPI
# Xem chi tiết trong README.md
```

### 2. API Blueprint
```bash
cd 1_APIBlueprint
# Xem chi tiết trong README.md
```

### 3. RAML
```bash
cd 2_RAML
# Xem chi tiết trong README.md
```

### 4. TypeSpec (Tương lai của API specs?)
```bash
cd 3_TypeSpec
# Xem chi tiết trong README.md
```

## Recommended Tools

| Format | Tools | Installation |
|--------|-------|--------------|
| OpenAPI | Swagger UI, Redoc, Code Gen | npm/pip/docker |
| API Blueprint | Drafter, Aglio | npm install apiary |
| RAML | API Workbench, API Designer | VS Code extension |
| TypeSpec | tsp CLI, Emitter | npm install -g @typespec/compiler |

## Tài liệu tham khảo

- [OpenAPI Specification](https://spec.openapis.org/)
- [API Blueprint](https://apiblueprint.org/)
- [RAML Specification](https://raml.org/)
- [TypeSpec Documentation](https://microsoft.github.io/typespec/)
