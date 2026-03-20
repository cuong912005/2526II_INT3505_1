# OpenAPI 3.0 - Book Management API

## Installation & Code Generation

```bash
# Cài OpenAPI Generator CLI
npm install -g @openapitools/openapi-generator-cli

# Sinh Node.js/Express server code
openapi-generator-cli generate \
  -i openapi.yaml \
  -g nodejs-express-server \
  -o ./generated-server

# Hoặc sinh Python Flask code
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python-flask \
  -o ./generated-server

# Hoặc sinh TypeScript client code
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-fetch \
  -o ./generated-client
```
