
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
│ (Sellable Unit) │ ----------------------------------------------------------
└────────┬────────┘                                                           |
         │ 1:1                                                                |
         ▼                                                                    |
┌─────────────────┐     ┌─────────────────┐                                   |
│   FixedPrice    │ OR  │   TieredPrice   │  ← Pricing (mutually exclusive)   | 1:1
└─────────────────┘     └─────────────────┘                                   |
         │                       │                                            ▼
         └───────────┬───────────┘         
                     ▼                                              ┌──────────────┐     
              ┌─────────────────┐                                   |  Dimensions  | 
              │    Inventory    │  ← Stock management               └──────────────┘            
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
| `origin_scope` | CharField | `global`, `ghana-made`, or `foreign` (defaults to 'ghana-made') - indicates product origin |
| `vendor_id` | UUID | Reference to vendor |
| `business_name` | CharField | Vendor's business name (denormalized) |
| `lead_time` | PositiveIntegerfield | Vendor's estimated time for product readiness in days |
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

#### Product Unique Constraints

1. **Unique name sale_type, status per vendor**: No two products of a vendor with the same name, and sale_type should have identical statuses.
   -  and yes, that means a vendor can have two active products with the same name, as long as they don't have the same sale_type.
   -  *a vendor's products' shouldn't have an identical combination of (name, sale_type and status), every other combination is fine*

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

1. **Unique attributes per product per vendor**: No two variants under the same product can have identical attributes and status
   - *a vendor's product's variant should not have an identical combination of (attributes and status) every other combo is fine*
2. **Unique SKU per vendor**: Each vendor must use unique SKUs across all their variants
   - *a vendor's variant should not have an identical combination of (sku and status), every other combination is fine*

### Pricing Models

The product service supports two mutually exclusive pricing models. The `pricing_model` is set at the **Product level** and applies to ALL variants under that product.

> **Important**:
> - Once a product has non-discontinued variants with prices, the pricing model CANNOT be changed directly.
> - For a vendor to change a product's pricing model, **all its non-discontinued variants must first be deleted (set to `discontinued`)**.
> - A deleted (`discontinued`) variant cannot be reactivated (set to `active` or `inactive`), even by admin, as doing so would cause database inconsistencies with attribute/SKU uniqueness constraints.
> - A vendor can have multiple variants under a product with the same sku/attributes, as long as their statuses are not the same.

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

**Constraints:**
- `low_stock_threshold` must be >= `minimum_order_quantity`

**MOQ Rules by Sale Type:**
- **Retail Products**: MOQ must be exactly `1` (cannot be greater than 1)
- **Wholesale Products**: MOQ must be greater than `1`

**Stock Status Logic:**
- **In Stock**: `stock >= minimum_order_quantity`
- **Low Stock**: `stock <= (2 × minimum_order_quantity)`
- **Out of Stock**: `stock < minimum_order_quantity`

### Dimensions
Each variant has a one-to-one relationship with an Dimensions.

| Field | Type | Description |
|-------|------|-------------|
| `variant` | OneToOne | Reference to ProductVariant (primary key) |
| `lenth` | Decimal(10,2) | Length of variant (defaults to `0.00`) |
| `width` | Decimal(10,2) | Width of variant (defaults to `0.00`)|
| `height` | Decimal(10,2) | Height of variant (defaults to `0.00`)|
| `weight` | Decimal(10,2) | Weight of variant (**required**) |

### Validation Logic

The product service implements validation at multiple layers for data integrity.

#### Model-Level Validation (models.py)

**Product Model:**
- Cannot change `pricing_model` after non-discontinued variants with prices exist
- Products with `origin_scope: global` must have `sale_type: wholesale`

**ProductVariant Model:**
- `attributes` must be a JSON object with string keys and values
- Attributes are normalized (lowercase, trimmed) before storage
- **Attribute consistency**: All variants under a product must have the same set of attribute keys (e.g., if first variant has `{size, color}`, all subsequent variants must also have exactly `{size, color}`)
- Unique constraint: No duplicate `(vendor_id, product, attribute_signature, status)` combinations
- Unique constraint: No duplicate `(vendor_id, sku, status)` combinations

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
- **Retail products**: MOQ must be exactly 1 (cannot exceed 1)
- **Wholesale products**: MOQ must be greater than 1

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

## Business Rules

This section consolidates the key business rules enforced by the product service.

### Pricing Model Change Rules

| Rule | Description |
|------|-------------|
| **Pricing Model Immutability** | A product's `pricing_model` (fixed/tiered) cannot be changed while it has non-discontinued variants with pricing attached |
| **Changing Pricing Model** | To change a product's pricing model, the vendor must first delete (set to `discontinued`) **all** its non-discontinued variants |
| **Pricing Consistency** | All variants under a product must use the same pricing model - you cannot mix `FixedPrice` and `TieredPrice` under the same product |

### Minimum Order Quantity (MOQ) Rules

| Sale Type | MOQ Requirement | Description |
|-----------|-----------------|-------------|
| **Retail** | MOQ = 1 | Retail products are for individual consumers; MOQ cannot exceed 1 |
| **Wholesale** | MOQ > 1 | Wholesale products are for bulk purchases; MOQ must be greater than 1 |

### Origin Scope Rules

| Origin Scope | Description | Sale Type Restriction |
|--------------|-------------|----------------------|
| **global** | Products imported from international markets | Must be `wholesale` only |
| **ghana-made** | Products manufactured and sold in Ghana | Can be `retail` or `wholesale` |
| **foreign** | Products imported from outside but sold in Ghana | Can be `retail` or `wholesale` |

> **Rule**: Products with `origin_scope: global` can only have `sale_type: wholesale`. Global products cannot be sold as retail.

### Variant Attribute Rules

| Rule | Description |
|------|-------------|
| **Attribute Key Consistency** | All variants under a product must have the **same set of attribute keys**. For example, if the first variant has `{"size": "large", "color": "red"}`, all subsequent variants must also have exactly `size` and `color` attributes |
| **No Missing Attributes** | A new variant cannot be missing any attribute keys that exist on other variants of the same product |
| **No Extra Attributes** | A new variant cannot have attribute keys that don't exist on other variants of the same product |

> **Example**: If a product has a variant with `{"size": "M", "color": "blue"}`, you:
> - Can add: `{"size": "L", "color": "red"}`
> - Cannot add: `{"size": "L"}` (missing `color`)
> - Cannot add: `{"size": "L", "color": "red", "material": "cotton"}` (extra `material`)

### Variant Status Rules

| Rule | Description |
|------|-------------|
| **Discontinued Variants Cannot Be Reactivated** | Once a variant is set to `discontinued`, it cannot be changed to `active` or `inactive` status, even by admin. This prevents database inconsistencies with attribute/SKU uniqueness constraints since discontinued variants are excluded from uniqueness checks |
| **Discontinued Variants Excluded from Constraints** | Discontinued variants do not count against uniqueness constraints, allowing vendors to create new variants with the same attributes/SKU as previously discontinued ones |

### Why These Rules Exist

1. **Pricing Model Immutability**: Changing pricing models mid-lifecycle could break existing cart items, orders, or analytics tied to the old pricing structure.

2. **MOQ by Sale Type**: Retail is consumer-facing (single unit purchases), while wholesale is business-facing (bulk purchases). The MOQ rule enforces this distinction.

3. **Global Origin Scope Restriction**: Global products are imported from international markets which typically involve bulk B2B transactions, not individual consumer sales. Restricting global products to wholesale ensures proper fulfillment logistics and pricing structures for cross-border commerce.

4. **Variant Attribute Consistency**: Ensures a uniform product structure for frontend display and filtering. If variants have inconsistent attribute keys, the UI cannot reliably show attribute selectors (e.g., size/color dropdowns) and comparison becomes impossible.

5. **Discontinued Variant Immutability**: When a variant is discontinued, it's excluded from uniqueness checks (`attribute_signature`, `sku`). If it could be reactivated, it might conflict with a newer variant that was created with the same attributes/SKU after the original was discontinued.

---

## Notes

### Products vs Variants
- **Products** hold shared metadata (name, description, category, brand, images)
- **Variants** are the actual purchasable items with specific attributes, pricing, and inventory
- Customers purchase **variants**, not products directly

### Pricing Model Immutability
- Once a product has non-discontinued variants with prices attached, the pricing model cannot be changed directly
- To change the pricing model, all non-discontinued variants must first be deleted (set to `discontinued`)
- All variants under a product must use the same pricing model (fixed OR tiered)

### Soft Delete Pattern
- Products and variants are not permanently deleted
- Status is set to `discontinued` which hides them from vendor views
- Admin can still see all products/variants regardless of status
- **Discontinued variants cannot be reactivated** (status cannot be changed from `discontinued` to `active` or `inactive`), even by admin, as this would cause database inconsistencies with attribute/SKU uniqueness constraints

### Stock and Availability
- A variant is "in stock" when `stock >= minimum_order_quantity`
- A product is "available" when it's active AND has at least one sellable variant
- Sellable = active status + valid pricing + sufficient stock

### HTML Sanitization
- Product names, descriptions, and alt text are sanitized using bleach
- Allowed tags: `b`, `i`, `u`, `em`, `strong`, `a`, `p`, `ul`, `li`, `br`
- All other HTML is stripped
