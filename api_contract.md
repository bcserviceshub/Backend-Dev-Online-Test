POST /api/products
---
**Description**
Creates a new product with all its associated data including images, attributes, and variants.

**Frontend usage**
Can be used by vendors or administrators to add new products to the catalog. Supports creating products with multiple variants, images, and attributes in a single request.

- URL Parameters
  - None

- Available Query Parameters
  - None

- Headers
  - `Content-Type: application/json`

- Data Parameters
```json
{
  "name": "Men's 100% Cotton Casual Crew Neck T-Shirt",
  "sku": "BEA-ESS-ESS-001",
  "description": "Men's 100% Cotton Casual Crew Neck T-Shirt - Regular Fit Short Sleeve with Milano Italy Letter Print, Breathable All-Season Comfort",
  "general_features": {
    "Sheer": "No",
    "Fabric": "Slight stretch",
    "Season": "Summer",
    "Pattern": "Print",
    "Sleeve Type": "Regular Sleeve",
    "Collar Style": "Crew Neck",
    "Sleeve Length": "Short Sleeve",
    "Weaving method": "Knit Fabric"
  },
  "category": "mens-shirts",
  "brand": "milano",
  "base_price": "100.89",
  "sale_price": "78.22",
  "cost_price": "50.00",
  "stock": 20,
  "low_stock_threshold": 10,
  "track_inventory": true,
  "status": "active",
  "weight": null,
  "length": null,
  "width": null,
  "height": null,
  "images": [
    {
      "image": "https://img.kwcdn.com/product/fancy/market/be2dcfae82ee1d0164d6ec6a4123bc5c_tHjErIfrHqVkI.jpg",
      "alt_text": "Primary product image",
      "is_primary": true
    },
    {
      "image": "https://img.kwcdn.com/product/open/7d2f3d6e2c034dfdb4a3e94033a95919-goods.jpeg",
      "alt_text": "Alternative product view",
      "is_primary": false
    }
  ],
  "attributes": [
    {
      "attribute": "color",
      "value": "white"
    },
    {
      "attribute": "size", 
      "value": "small"
    }
  ],
  "variants": [
    {
      "sku": "BEA-ESS-ESS-002",
      "name": "Men's 100% Cotton Casual Crew Neck T-Shirt - Medium White",
      "price": "100.89",
      "sale_price": "78.53",
      "stock": 12,
      "track_inventory": true,
      "is_active": true,
      "weight": null,
      "variant_attributes": [
        {
          "attribute": "color",
          "value": "white"
        },
        {
          "attribute": "size",
          "value": "m"
        }
      ],
      "images": [
        {
          "image": "https://img.kwcdn.com/product/fancy/market/be2dcfae82ee1d0164d6ec6a4123bc5c_tHjErIfrHqVkI.jpg",
          "alt_text": "White medium variant",
          "is_primary": true
        }
      ]
    }
  ]
}
```

- **Required Fields**
  - `name`: Product name (string)
  - `sku`: Stock Keeping Unit (string, max 100 chars)
  - `description`: Product description (text)
  - `base_price`: Base price (decimal, max 10 digits, 2 decimal places)
  - `images`: Array of product images (at least one required)

- **Optional Fields**
  - `general_features`: JSON object for general product features
  - `category`: Category slug (string, references existing category), defaults to `miscellaneous` if not provided
  - `brand`: Brand slug (string, references existing brand), defaults to `generic` if not provided
  - `sale_price`: Sale/discounted price (decimal). Product would go on sale if `sale_price` is provided and is lower than `base_price`.
  - `cost_price`: Cost to vendor (decimal)
  - `stock`: Stock quantity (integer, default 0)
  - `low_stock_threshold`: Minimum stock alert level (integer, default 10)
  - `track_inventory`: Whether to track inventory (boolean, default true)
  - `status`: Product status (`active`, `inactive`, `draft`, `discontinued`, default `draft`)
  - `weight`: Product weight (decimal)
  - `length`: Product length (decimal)
  - `width`: Product width (decimal)  
  - `height`: Product height (decimal)
  - `attributes`: Array of product attributes
  - `variants`: Array of product variants

**Images field**
- **Required fields**
  - `image`: Image url
- **Optional fields**
  - `is_primary`: Specifies which image would be used as the thumbnail (boolean, default false). Should only be true for one image.
  - `alt_text`: Text describing the image.


**Variant fields**
- **Required fields**
  - `sku`: Stock Keeping Unit (string, max 100 chars)
  - `variant_attributes`: Array of variant's attributes
  - `images`: Array of variants images
- **Optional fields**
  - `name`: Variant's name
  - `price`: Variant's base price (decimal, max 10 digits, 2 decimal places), uses main product's `base_price` if not provided.
  - `sale_price`: Variant's sale/discounted price (decimal), uses main product's `sale_price` if not provided.
  - `stock`: Stock quantity (integer, default 0), uses main product's `stock` if not provided.
  - `is_active`: Variants status (boolean, default true)
  - `track_inventory`: Whether to track inventory (boolean, default true)

**Validation Rules**
  - If `status` is `active`, `stock` must be greater than 0
  - `category` must reference an existing category slug
  - `brand` must reference an existing brand slug
  - Each image in `images` array must have `image` URL
  - Variant attributes must be valid attribute-value pairs
  - For variants, `stock` must be greater than 0 if `is_active` is true.

**Explaining pricing**
- `cost_price`: the amount of money it costs the vendor to produce or acquire the product
- `base_price`: the starting selling price before discounts, taxes, or promotional adjustments
- `sale_price`: (a.k.a. selling price) the price the customer actually pays after:
  - discounts
  - coupons
  - seasonal promotions
  - flash sales
  - clearance markdowns
- If there are no discounts, then `sale_price` == `base_price`

**Example**
- you buy a pair of knock off sneakers from a supplier in kanta.
  - `cost_price` = ₵60
- you want 100% profit margin on that
  - `base_price` = ₵120
- you are running a 20% off summer sale
  - `base_price` = ₵120
  - `discount` = 20% = ₵24
  - `sale_price` = ₵120 - ₵24 = ₵96

**Explaining Variation**:
- If the product has a property/attribute that would cause it to have a variation, that property/attribute is stored in the ProductAttribute model (in the case of the API, that would be the `attributes` array/section of the product)
- When creating the variants, the attribute/property of the product which varies to cause the variant is stored in the VariantAttribute model (in the case of the API, that would be the `variant_attributes` array/section of the product's variant) for that specific variant.
- A product's `attributes` are properties/attributes that vary accross variants (e.g., color, size, RAM, cpu speed, etc).
- A product's variants are specific combinations of those variable `attributes`.
- `variant_attributes` are the actual properties/attributes of that variant which causes it to differ from the main product.
- *NB*: `attributes` is only used when a product has a variation.

**Example**:
- If a vendor is selling two Stanley cups of varying colors, red and white, with the red cup being his main product.
- the `attributes` sectiton of the product is populated with the *red* attribute, with its accompanying data.
- a variant is created with its `variant_attribute` populated with the *white* attribute, with its accompanying data.
- POST request then becomes:
  ```json
  {
      "name": "Stanley Quencher H2.0 Tumbler",
      "base_price": "...",
      "general_features": "...",
      "attributes": [
        {
          "attribute": "color",
          "value": "red"
        }
      ],
      "variants": [
        {
          "name": "...",
          "price": "...",
          "variant_attributes": [
            {
              "attribute": "color",
              "value": "white"
            }
          ]
        }
      ]
  ```

- **Success Response**
  - `201 Created`: Product created successfully

```json
{
  "id": "77b44a6a-1c22-40a2-99a1-0b073ffa488b",
  "name": "Men's 100% Cotton Casual Crew Neck T-Shirt",
  "sku": "BEA-ESS-ESS-001",
  "description": "Men's 100% Cotton Casual Crew Neck T-Shirt - Regular Fit Short Sleeve with Milano Italy Letter Print, Breathable All-Season Comfort",
  "general_features": {
    "Sheer": "No",
    "Fabric": "Slight stretch",
    "Season": "Summer",
    "Pattern": "Print",
    "Sleeve Type": "Regular Sleeve",
    "Collar Style": "Crew Neck",
    "Sleeve Length": "Short Sleeve",
    "Weaving method": "Knit Fabric"
  },
  "category": "mens-shirts",
  "brand": "milano",
  "vendor": "77b44a6a-1c22-40a2-99a1-0b073ffa488b",
  "base_price": "100.89",
  "sale_price": "78.22",
  "cost_price": "50.00",
  "stock": 20,
  "low_stock_threshold": 10,
  "track_inventory": true,
  "status": "active",
  "weight": null,
  "length": null,
  "width": null,
  "height": null,
  "images": [
    {
      "id": "c16f71bf-9810-4026-bb9e-1f0922f7b718",
      "image": "https://img.kwcdn.com/product/fancy/market/be2dcfae82ee1d0164d6ec6a4123bc5c_tHjErIfrHqVkI.jpg",
      "alt_text": "Primary product image",
      "is_primary": true,
      "created_at": "2025-08-03T21:21:09.025422Z",
      "updated_at": "2025-08-03T21:21:09.025422Z"
    },
    {
      "id": "fe856ea7-94d6-4ace-8863-35f6f24a1dae",
      "image": "https://img.kwcdn.com/product/open/7d2f3d6e2c034dfdb4a3e94033a95919-goods.jpeg",
      "alt_text": "Alternative product view",
      "is_primary": false,
      "created_at": "2025-08-03T21:21:09.021015Z",
      "updated_at": "2025-08-03T21:21:09.021015Z"
    }
  ],
  "attributes": [
    {
      "id": "32bb1058-7141-4bf4-b469-623d7a89afb7",
      "attribute": "color",
      "value": "white",
      "created_at": "2025-08-03T21:21:09.015600Z",
      "updated_at": "2025-08-03T21:21:09.015600Z"
    },
    {
      "id": "5d5a7791-c497-428a-a4c6-27ab666fba0b",
      "attribute": "size",
      "value": "small", 
      "created_at": "2025-08-03T21:21:09.015600Z",
      "updated_at": "2025-08-03T21:21:09.015600Z"
    }
  ],
  "variants": [
    {
      "id": "2688442f-f216-45ad-bae0-58ea3d81e293",
      "sku": "BEA-ESS-ESS-002",
      "name": "Men's 100% Cotton Casual Crew Neck T-Shirt - Medium White",
      "price": "100.89",
      "sale_price": "78.53",
      "current_price": "78.53",
      "stock": 12,
      "track_inventory": true,
      "is_in_stock": true,
      "weight": null,
      "dimensions": null,
      "is_active": true,
      "variant_attributes": [
        {
          "id": "ca85444c-f5f6-4322-b76c-fd58f69d79d0",
          "attribute": "color",
          "value": "white",
          "created_at": "2025-08-03T21:21:09.029101Z",
          "updated_at": "2025-08-03T21:21:09.029101Z"
        },
        {
          "id": "b585afae-752f-46a7-b983-b3ee5b7a788d",
          "attribute": "size",
          "value": "m",
          "created_at": "2025-08-03T21:21:09.033036Z",
          "updated_at": "2025-08-03T21:21:09.033036Z"
        }
      ],
      "images": [
        {
          "id": "abc12345-1234-5678-9012-123456789012",
          "image": "https://img.kwcdn.com/product/fancy/market/be2dcfae82ee1d0164d6ec6a4123bc5c_tHjErIfrHqVkI.jpg",
          "alt_text": "White medium variant",
          "is_primary": true,
          "created_at": "2025-08-03T21:21:09.025422Z",
          "updated_at": "2025-08-03T21:21:09.025422Z"
        }
      ],
      "created_at": "2025-08-03T21:21:09.025422Z",
      "updated_at": "2025-08-03T21:21:09.025422Z"
    }
  ]
}
```

**Error Responses**
- `400 Bad Request`: Invalid input, validation errors, or missing required fields

```json
{
  "stock": ["Stock must be greater than one if status is active"],
  "category": ["Invalid slug 'invalid-category' - object does not exist."],
  "base_price": ["This field is required."],
  "images": ["This field is required."]
}
```
