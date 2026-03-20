# Hướng dẫn cài đặt Tools

## 1. OpenAPI

### Cài đặt
```bash
# Cài đặt Swagger UI (Docker)
docker run -p 8080:8080 -e SWAGGER_JSON=/data/openapi.yaml -v $(pwd)/0_OpenAPI:/data swaggerapi/swagger-ui

# Hoặc dùng Node.js
npm install -g @openapitools/openapi-generator

# Hoặc dùng Python
pip install openapi-spec-validator
```

### Sinh code từ OpenAPI
```bash
# Node.js (Express)
openapi-generator-cli generate -i openapi.yaml -g nodejs-express-server -o generated

# Python (Flask)
openapi-generator-cli generate -i openapi.yaml -g python-flask -o generated

# Java (Spring Boot)
openapi-generator-cli generate -i openapi.yaml -g spring -o generated
```

### Xem documentation
```bash
# Docker Compose
docker-compose up swagger-ui
# Truy cập http://localhost:8080
```

## 2. API Blueprint

### Cài đặt
```bash
# Cài đặt Drafter (parser)
npm install -g drafter

# Cài đặt Aglio (HTML renderer)
npm install -g aglio
```

### Sinh code từ API Blueprint
```bash
# Parse & validate
drafter api.apib -o api.json

# Generate HTML documentation
aglio -i api.apib -o api.html
```

## 3. RAML

### Cài đặt
```bash
# RAML parser
npm install -g raml2html

# VS Code extension
# Tìm "RAML" trong Extensions marketplace
```

### Sinh code từ RAML
```bash
# Generate HTML
raml2html api.raml > api.html

# Cài thêm RAML JavaScript parser
npm install -g raml-parser
```

## 4. TypeSpec

### Cài đặt
```bash
# Cài đặt TypeSpec compiler
npm install -g @typespec/compiler

# Cài các emitter khác
npm install @typespec/openapi3
npm install @typespec/rest
```

### Sinh code từ TypeSpec
```bash
# Compile TypeSpec
tsp compile . --output-dir dist

# Tạo OpenAPI từ TypeSpec
tsp compile . --option @typespec/openapi3.output-file=openapi.yaml
```

## Công cụ chung

### Postman / Insomnia
- Import OpenAPI JSON → Tận dụng ngay
- Cần convert định dạng khác về OpenAPI hoặc dùng custom scripts

### Validator Online
- https://www.swagger.io/tools/swagger-editor/  (OpenAPI)
- https://apiblueprint.org/ (API Blueprint)
- https://apiworkbench.com/ (RAML)
- https://microsoft.github.io/typespec/playground/ (TypeSpec)

## Quick Test (API Blueprint example)

```bash
# 1. Install dependencies
npm install drafter aglio

# 2. Parse API Blueprint
npx drafter api.apib

# 3. Generate HTML documentation
npx aglio -i api.apib -o api.html -s

# 4. Open in browser
open api.html
```

## Docker Compose (All-in-One)

Xem file `docker-compose.yml` trong parent directory để chạy tất cả các tool cùng lúc.
