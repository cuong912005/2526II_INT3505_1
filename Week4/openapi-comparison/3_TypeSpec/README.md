# TypeSpec - Book Management API

## Installation & Code Generation

### Windows (PowerShell)

```powershell
# Cài TypeSpec compiler
npm install -g @typespec/compiler

# Cài OpenAPI emitter
npm install @typespec/openapi3

# Sinh OpenAPI 3.0 từ TypeSpec
tsp compile . --option @typespec/openapi3.output-file=openapi.yaml

# Lúc này có thể dùng OpenAPI Generator để sinh server code
npm install -g @openapitools/openapi-generator-cli
openapi-generator-cli generate -i openapi.yaml -g nodejs-express-server -o ./generated-server
```

### Linux/Mac (Bash)

```bash
# Cài TypeSpec compiler
npm install -g @typespec/compiler

# Cài OpenAPI emitter
npm install @typespec/openapi3

# Sinh OpenAPI 3.0 từ TypeSpec
tsp compile . --option @typespec/openapi3.output-file=openapi.yaml

# Lúc này có thể dùng OpenAPI Generator để sinh server code
npm install -g @openapitools/openapi-generator-cli
openapi-generator-cli generate \
  -i openapi.yaml \
  -g nodejs-express-server \
  -o ./generated-server
```
