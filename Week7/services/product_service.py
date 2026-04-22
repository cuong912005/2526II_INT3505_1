from repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    def _format_product(self, product):
        """Chuyển đổi ObjectId và Datetime sang định dạng JSON cho API."""
        if not product:
            return None
        product['id'] = str(product.pop('_id'))
        if 'createdAt' in product:
            product['createdAt'] = product['createdAt'].isoformat() + 'Z'
        if 'updatedAt' in product:
            product['updatedAt'] = product['updatedAt'].isoformat() + 'Z'
        return product

    def _validate_input(self, data):
        """Validate body dữ liệu theo file OpenAPI."""
        required_fields = ['name', 'description', 'price', 'quantity']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(data['name'], str) or len(data['name'].strip()) < 1 or len(data['name']) > 255:
            raise ValueError("Name must be a string between 1 and 255 characters")
        if not isinstance(data.get('price', 0), (int, float)) or data['price'] < 0:
            raise ValueError("Price must be a non-negative number")
        if not isinstance(data.get('quantity', 0), int) or data['quantity'] < 0:
            raise ValueError("Quantity must be a non-negative integer")

    def get_products(self, skip, limit, search):
        try:
            skip = int(skip)
            limit = int(limit)
        except ValueError:
            raise ValueError("skip and limit must be integers")
            
        products = self.repository.get_all(skip, limit, search)
        return [self._format_product(p) for p in products]

    def get_product(self, product_id):
        product = self.repository.get_by_id(product_id)
        if not product:
            raise KeyError("Product not found")
        return self._format_product(product)

    def create_product(self, data):
        self._validate_input(data)
        product = self.repository.create(data)
        return self._format_product(product)

    def update_product(self, product_id, data):
        self._validate_input(data)
        product = self.repository.update(product_id, data)
        if not product:
            raise KeyError("Product not found")
        return self._format_product(product)

    def delete_product(self, product_id):
        deleted = self.repository.delete(product_id)
        if not deleted:
            raise KeyError("Product not found")
        return True