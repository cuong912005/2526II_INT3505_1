# RAML 1.0 - Book Management API

## Installation

```bash
# Cài RAML parser
npm install -g raml-parser

# Parse RAML file
raml-parser api.raml

# Convert RAML to OpenAPI
npm install -g raml-to-openapi
raml-to-openapi api.raml > openapi.json
```

**Note**: RAML không có code generator riêng. Convert sang OpenAPI để sinh code.
