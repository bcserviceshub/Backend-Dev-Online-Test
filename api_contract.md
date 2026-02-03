## Database Design

### Product Architecture Overview

The product service uses a **Product-Variant architecture** that separates product metadata from actual sellable units. This design enables:

1. **Single product with multiple variations** (e.g., a T-shirt in different sizes/colors)
2. **Independent inventory tracking per variant**
3. **Flexible pricing models per product** (fixed or tiered)
4. **Granular stock and availability management**

```
┌─────────────────┐
│     Product     │  ← Metadata (name, description, category, brand)
│  (Parent Entity)│
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│ ProductVariant  │  ← Actual sellable unit with attributes
│ (Sellable Unit) │
└────────┬────────┘
         │ 1:1
         ▼
┌─────────────────┐     ┌─────────────────┐
│   FixedPrice    │ OR  │   TieredPrice   │  ← Pricing (mutually exclusive)
└─────────────────┘     └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
              ┌─────────────────┐
              │    Inventory    │  ← Stock management
              └─────────────────┘
```

### Product Model (Metadata)

The **Product** model represents product metadata - shared information that applies to all variants of a product. It is **NOT** directly purchasable; customers purchase **variants**.

#### Product Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | CharField(255) | Product name |
| `description` | TextField | Product description |
| `category` | ForeignKey | Reference to Category (defaults to "Miscellaneous") |
| `brand` | ForeignKey | Reference to Brand (defaults to "Generic") |
| `pricing_model` | CharField | `fixed` or `tiered` - applies to ALL variants (defaults to 'fixed') |
| `sale_type` | CharField | `wholesale` or `retail` (defaults to retail)|
| `vendor_id` | UUID | Reference to vendor |
| `business_name` | CharField | Vendor's business name (denormalized) |
| `status` | CharField | `draft`, `active`, `inactive` (defaults to draft) |

#### Product Status Values

| Status | Description |
|--------|-------------|
| `draft` | Product is being created, not visible to customers |
| `active` | Product is live and can be displayed (if has sellable variants) |
| `inactive` | Product is temporarily hidden |
| `discontinued` | Product is soft-deleted, not retrievable by vendors **(not to be shown on frontend, backend only)** |

#### Key Product Properties

- **`is_available`**: Returns `True` only if product status is `active` AND has at least one sellable variant
- **`is_on_sale`**: Returns `True` if any variant is currently on sale
- **`price`**: Display-only property showing the lowest current price among variants
- **`moq`**: Display-only property showing the minimum order quantity

### ProductVariant Model (Sellable Units)

The **ProductVariant** model represents the actual sellable unit. Each variant has unique attributes (e.g., size: "Large", color: "Blue") and its own inventory, pricing, and images.

#### Variant Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `product` | ForeignKey | Parent product |
| `attributes` | JSONField | Key-value pairs defining the variant (e.g., `{"size": "large", "color": "blue"}`) |
| `condition` | CharField | `new`, `slightly used`, `used` |
| `attribute_signature` | CharField | Computed hash of normalized attributes (for uniqueness) |
| `vendor_id` | UUID | Inherited from product |
| `sku` | CharField(100) | Stock Keeping Unit (unique per vendor) |
| `status` | CharField | `active`, `inactive` (defaults to inactive) |

#### Variant Status Values

| Status | Description |
|--------|-------------|
| `active` | Variant is available for purchase (requires valid pricing and inventory) |
| `inactive` | Variant is temporarily unavailable |
| `discontinued` | Variant is soft-deleted |

#### Key Variant Properties

- **`is_sellable`**: Returns `True` if variant has:
  - Status = `active`
  - Valid pricing (FixedPrice or TieredPrice)
  - Stock >= minimum_order_quantity
  
- **`is_in_stock`**: Returns `True` if stock >= minimum_order_quantity

- **`is_low_stock`**: Returns `True` if stock <= 2 × minimum_order_quantity

- **`is_on_sale`**: Returns `True` if variant is active, in stock, and has a sale price set

- **`price`**: 
  - For fixed pricing: Returns `current_price`
  - For tiered pricing: Returns price range (e.g., "10.00 - 8.00")

#### Variant Uniqueness Constraints

1. **Unique attributes per product per vendor**: No two variants under the same product can have identical attributes
2. **Unique SKU per vendor**: Each vendor must use unique SKUs across all their variants

### Pricing Models

The product service supports two mutually exclusive pricing models. The `pricing_model` is set at the **Product level** and applies to ALL variants under that product.

> **Important**: Once a product has variants with prices, the pricing model CANNOT be changed.

#### Fixed Price Model

Used for standard retail pricing with a single price point.

| Field | Type | Description |
|-------|------|-------------|
| `variant` | OneToOne | Reference to ProductVariant (primary key) |
| `base_price` | Decimal(10,2) | Original price |
| `sale_price` | Decimal(10,2) | Optional discounted price |

**Computed Properties:**
- `current_price`: Returns `sale_price` if set, otherwise `base_price`
- `is_on_sale`: True if `sale_price` exists and is less than `base_price`
- `discount_percentage`: Calculated discount if on sale

**Example:**
```json
{
  "fixed_price": {
    "base_price": "99.99",
    "sale_price": "79.99",
    "current_price": "79.99",
    "is_on_sale": true,
    "discount_percentage": "20.01"
  }
}
```

#### Tiered Price Model

Used for wholesale/bulk pricing where price per unit decreases with quantity.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `variant` | ForeignKey | Reference to ProductVariant |
| `min_quantity` | PositiveInt | Minimum quantity for this tier |
| `max_quantity` | PositiveInt | Maximum quantity for this tier |
| `base_price_per_unit` | Decimal(10,2) | Original price per unit |
| `sale_price_per_unit` | Decimal(10,2) | Optional discounted price per unit |

**Tier Rules:**
1. Tiers must be **contiguous** - no gaps between ranges
2. First tier must start at the variant's MOQ (minimum_order_quantity)
3. Tiers cannot **overlap**
4. Different tiers must have different base prices
5. `min_quantity` must be less than `max_quantity`

**Example:**
```json
{
  "tiered_price": [
    {
      "id": "tier-uuid-1",
      "min_quantity": 10,
      "max_quantity": 49,
      "base_price_per_unit": "15.00",
      "sale_price_per_unit": null,
      "current_price_per_unit": "15.00",
      "is_on_sale": false,
      "discount_percentage": 0
    },
    {
      "id": "tier-uuid-2",
      "min_quantity": 50,
      "max_quantity": 99,
      "base_price_per_unit": "12.00",
      "sale_price_per_unit": "10.00",
      "current_price_per_unit": "10.00",
      "is_on_sale": true,
      "discount_percentage": "16.67"
    },
    {
      "id": "tier-uuid-3",
      "min_quantity": 100,
      "max_quantity": 500,
      "base_price_per_unit": "9.00",
      "sale_price_per_unit": null,
      "current_price_per_unit": "9.00",
      "is_on_sale": false,
      "discount_percentage": 0
    }
  ]
}
```

### Inventory Management

Each variant has a one-to-one relationship with an Inventory record.

| Field | Type | Description |
|-------|------|-------------|
| `variant` | OneToOne | Reference to ProductVariant (primary key) |
| `stock` | PositiveInt | Current stock quantity |
| `minimum_order_quantity` | PositiveInt | Minimum units that can be ordered (MOQ) |
| `low_stock_threshold` | PositiveInt | Alert threshold for low stock |
| `track_inventory` | Boolean | Whether to track inventory for this variant |

**Constraint**: `low_stock_threshold` must be >= `minimum_order_quantity`

**Stock Status Logic:**
- **In Stock**: `stock >= minimum_order_quantity`
- **Low Stock**: `stock <= (2 × minimum_order_quantity)`
- **Out of Stock**: `stock < minimum_order_quantity`

### Validation Logic

The product service implements validation at multiple layers for data integrity.

#### Model-Level Validation (models.py)

**Product Model:**
- Cannot change `pricing_model` after variants with prices exist

**ProductVariant Model:**
- `attributes` must be a JSON object with string keys and values
- Attributes are normalized (lowercase, trimmed) before storage
- Unique constraint: No duplicate `(vendor_id, product, attribute_signature)` combinations
- Unique constraint: No duplicate `(vendor_id, sku)` combinations

**FixedPrice Model:**
- `base_price` must be a Decimal > 0 if variant is active
- Cannot create FixedPrice if product's pricing_model is `tiered`
- Cannot have both FixedPrice and TieredPrice for same variant
- `sale_price` cannot exceed `base_price`

**TieredPrice Model:**
- `base_price_per_unit` must be a Decimal > 0 if variant is active
- Cannot create TieredPrice if product's pricing_model is `fixed`
- Price ranges cannot overlap
- Tiers must be contiguous (start at MOQ, each tier starts where previous ended)
- Different tiers must have different base prices
- `min_quantity` must be >= variant's MOQ
- `sale_price_per_unit` cannot exceed `base_price_per_unit`

**Inventory Model:**
- `low_stock_threshold` cannot be lower than `minimum_order_quantity`
- Cannot set MOQ lower than existing tier minimum quantities

#### Serializer-Level Validation (serializers.py)

**ProductVariantSerializer Validation:**
```
If status == 'active':
  ├── inventory is REQUIRED
  │   ├── stock must be > 0
  │   ├── minimum_order_quantity must be > 0
  │   ├── moq cannot exceed stock
  │   └── low_stock_threshold must be >= moq
  │
  ├── exactly ONE pricing model required (fixed OR tiered, not both)
  │
  └── For tiered pricing:
      ├── min_quantity >= moq
      ├── max_quantity <= stock
      └── min_quantity < max_quantity
```

**ProductCreateSerializer Validation:**
- Images are required
- If status == `active`, variants are required
- Vendor must have completed their storefront profile
- HTML content is sanitized using bleach

**CreateReviewSerializer Validation:**
- User must be authenticated
- User can only submit one review per product

---


## Notes

### Products vs Variants
- **Products** hold shared metadata (name, description, category, brand, images)
- **Variants** are the actual purchasable items with specific attributes, pricing, and inventory
- Customers purchase **variants**, not products directly

### Pricing Model Immutability
- Once a product has variants with prices attached, the pricing model cannot be changed
- All variants under a product must use the same pricing model (fixed OR tiered)

### Soft Delete Pattern
- Products and variants are not permanently deleted
- Status is set to `discontinued` which hides them from vendor views
- Admin can still see all products/variants regardless of status

### Stock and Availability
- A variant is "in stock" when `stock >= minimum_order_quantity`
- A product is "available" when it's active AND has at least one sellable variant
- Sellable = active status + valid pricing + sufficient stock

### HTML Sanitization
- Product names, descriptions, and alt text are sanitized using bleach
- Allowed tags: `b`, `i`, `u`, `em`, `strong`, `a`, `p`, `ul`, `li`, `br`
- All other HTML is stripped
