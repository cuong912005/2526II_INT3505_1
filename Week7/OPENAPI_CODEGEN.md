# OpenAPI Code Generation Guide

## Yêu cầu
- Java JDK 8+
- openapi-generator CLI

## Cài đặt openapi-generator
```bash
# Trên Windows
npm install -g @openapitools/openapi-generator-cli

# Hoặc dùng Homebrew (Mac/Linux)
brew install openapi-generator
```

## Gen Python Server
```bash
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python-flask \
  -o generated-server
```

## Gen Client
```bash
# Python client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o generated-client

# JavaScript client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g javascript \
  -o generated-client-js
```

## Chạy Generated Server
```bash
cd generated-server
pip install -r requirements.txt
python -m openapi_server
```

## Lưu ý
- Sửa `host` và `basePath` trong openapi.yaml nếu cần
- Check `openapitools.json` để custom config
