# Nội dung Chi tiết: So sánh OpenAPI, API Blueprint, RAML, TypeSpec

## 1. Lịch sử & Tiến hóa

### OpenAPI (Swagger)
**2009-2015**: Wordnik tạo Swagger → Linux Foundation nuôi → Đổi tên OpenAPI
**Hiện tại**: OAS 3.1 - chuẩn công nghiệp toàn cầu

### API Blueprint
**2013-2015**: Apiary giới thiệu → v1.0 ổn định
**Hiện tại**: ❌ Ngừng phát triển từ 2023

### RAML
**2013-2016**: MuleSoft giới thiệu → RAML 1.0 released
**Hiện tại**: Vẫn support nhưng ít adoption

### TypeSpec
**2022-2024**: Microsoft giới thiệu → v0.x → hướng v1.0
**Hiện tại**: Mới, modern, đầy tiềm năng

---

## 2. Syntax & Dễ học

### OpenAPI
```yaml
openapi: 3.0.0
info:
  title: Book API
paths:
  /books:
    get:
      responses: { '200': {description: Success} }
```
**Phong cách**: YAML/JSON, verbose, explicit mọi thứ
**Dốc học**: 7/10 | **Readability**: 9/10

### API Blueprint
```markdown
## Books [/books]
### List books [GET]
+ Response 200 (application/json)
```
**Phong cách**: Markdown-based, human-readable, compact
**Dốc học**: 3/10 | **Readability**: 7/10

### RAML
```yaml
#%RAML 1.0
/books:
  get:
    responses:
      200:
        body:
          application/json: {type: Book}
```
**Phong cách**: YAML, DRY principle, traits reusable
**Dốc học**: 6/10 | **Readability**: 8/10

### TypeSpec
```typespec
@get("/books")
op listBooks(): Book[];
```
**Phong cách**: TypeScript-like, type-safe, modern
**Dốc học**: 4/10 | **Readability**: 9/10

## 3. Tooling & Ecosystem

| Tool | OpenAPI | API Blueprint | RAML | TypeSpec |
|------|---------|---------------|------|----------|
| **Code Gen** | Cao | Thấp | Thấp | Trung |
| **Documentation** | Cao | Thấp | Trung | Trung |
| **Mock Server** | Cao | Trung | Trung | Trung |
| **IDE Support** | Cao | Thấp | Trung | Trung |

**Ví dụ tool**:
- **OpenAPI**: `openapi-generator-cli`, Swagger UI, Prism
- **API Blueprint**: `drafter`, `aglio`, Drakov
- **RAML**: `raml2html`, `raml-parser`, Hogan
- **TypeSpec**: `tsp` CLI, OpenAPI 3 emitter

## 4. Use Cases

| Format | Nên dùng khi | Lý do |
|--------|-----------|--------|
| **OpenAPI** | Dự án enterprise, public APIs | Chuẩn công nghiệp, tooling phong phú |
| **API Blueprint** | Team nhỏ, sketch nhanh | Dễ học (Markdown), nhưng ngừng phát triển |
| **RAML** | MuleSoft ecosystem, API-first | Traits reusable, DRY code |
| **TypeSpec** | Modern teams (TS/JS), Azure | Type-safe, familiar syntax, nhưng v0.x |

## 5. Ví dụ: POST /books (Tạo sách)

**OpenAPI**:
```yaml
post:
  requestBody:
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CreateBookRequest'
  responses:
    '201':
      description: Book created
```

**API Blueprint**:
```markdown
### Create book [POST]
+ Request (application/json)
    + Attributes (CreateBook)
+ Response 201 (application/json)
    + Attributes (Book)
```

**RAML**:
```yaml
post:
  body:
    application/json:
      type: CreateBook
  responses:
    201:
      body:
        application/json:
          type: Book
```

**TypeSpec**:
```typespec
@post("/books") @status(201)
op createBook(@body book: CreateBook): Book;
```

## 6. Cheat Sheet: Syntax Mapping

| Concept | OpenAPI | API Blueprint | RAML | TypeSpec |
|---------|---------|---------------|------|----------|
| Data model | `components.schemas` | `Data Structures` | `types` | `model` |
| Endpoint | `paths` | `## Resource` | `/{path}` | `@route` |
| Parameter | `parameters` | `+ Parameters` | `uriParameters` | `@query/@path` |
| Response | `responses` | `+ Response` | `responses` | `→ ReturnType` |


