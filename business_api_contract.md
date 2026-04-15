# API Contract for Business Listing Owner Endpoints

## Table of Contents

1. [Field Specifications and Choices](#field-specifications-and-choices)
   - [Business Category Options](#business-category-options)
   - [Status Options](#status-options)
   - [Tier Options](#tier-options)

2. [Common Response Fields](#common-response-fields)
   - [Business Listing Object Fields](#business-listing-object-fields)
   - [Business Listing Image Fields (nested object)](#business-listing-image-fields-nested-object)
   - [Tab item fields (nested object)](#tab-item-fields-nested-object)
   - [Business Review Fields (nested object)](#business-review-fields-nested-object)
   - [Review Image Fields (nested object)](#review-image-fields-nested-object)

3. [Authentication & Authorization](#authentication--authorization)

4. [Error Responses](#error-responses)

5. [Notes](#notes)

6. [Business Registration API](#business-registration-api)
   - [POST /api/business-listing/register](#post-apibusiness-listingregister)

7. [Business Profile APIs](#business-profile-apis)
   - [GET /api/business-listing/me](#get-apibusiness-listingme)
   - [PATCH /api/business-listing/me](#patch-apibusiness-listingme)
   - [GET /api/business-listing/me/reviews](#get-apibusiness-listingmereviews)

8. [Business hours APIs](#business-hours-apis)
   - [GET /api/business-listing/me/business-hours](#get-apibusiness-listingmebusiness-hours)
   - [POST /api/business-listing/me/business-hours](#post-apibusiness-listingmebusiness-hours)
   - [PUT /api/business-listing/me/business-hours](#put-apibusiness-listingmebusiness-hours)

9. [Business bookings (owner)](#business-bookings-owner)
   - [GET /api/business-listing/me/bookings](#get-apibusiness-listingmebookings)

10. [Business tab APIs](#business-tab-apis)
   - [GET /api/business-listing/me/tab](#get-apibusiness-listingmetab)
   - [POST /api/business-listing/me/tab](#post-apibusiness-listingmetab)
   - [PATCH /api/business-listing/me/tab](#patch-apibusiness-listingmetab)
   - [DELETE /api/business-listing/me/tab](#delete-apibusiness-listingmetab)
   - [GET /api/business-listing/me/tab/items](#get-apibusiness-listingmetabitems)
   - [POST /api/business-listing/me/tab/items](#post-apibusiness-listingmetabitems)
   - [GET /api/business-listing/me/tab/items/{id}](#get-apibusiness-listingmetabitemsid)
   - [PATCH /api/business-listing/me/tab/items/{id}](#patch-apibusiness-listingmetabitemsid)
   - [DELETE /api/business-listing/me/tab/items/{id}](#delete-apibusiness-listingmetabitemsid)

---

## Field Specifications and Choices

### Business Category Options
- `restaurant`: Restaurant
- `cafe`: Cafe
- `hotel`: Hotel
- `health and wellness`: Health and Wellness
- `entertainment`: Entertainment
- `personal care`: Personal Care
- `retail`: Retail

### Status Options
- `approved`: Approved
- `pending`: Pending
- `rejected`: Rejected

### Tier Options
- `basic_business_listing`: Basic Business Listing
- `premium_business_listing`: Premium Business Listing

---

## Common Response Fields

### Business Listing Object Fields
- `id`: UUID (Primary Key)
- `business_name`: string (max 255 chars, unique)
- `business_category`: string (choice) - see [Business Category Options](#business-category-options)
- `year_established`: date (ISO format)
- `description`: text
- `phone_number`: string (max 20 chars, unique)
- `whatsapp_number`: string (max 20 chars, unique)
- `email`: string (email format)
- `website_url`: string (URL, optional)
- `instagram`: string (max 255 chars)
- `twitter`: string (max 255 chars)
- `tiktok`: string (max 255 chars)
- `facebook`: string (max 255 chars, optional)
- `address`: string (max 255 chars)
- `geo_coordinates`: object - GPS location with `latitude` and `longitude` fields
- `city`: string (max 255 chars)
- `region`: string (max 255 chars)
- `business_hours`: array - one row per configured weekday; see [Business hours row fields](#business-hours-row-fields). Returned on **read** (`GET`); not accepted on `POST /register` or `PATCH /me` (manage hours via [Business hours APIs](#business-hours-apis)).
- `status`: string (choice, read-only) - see [Status Options](#status-options)
- `tier`: string (choice) - see [Tier Options](#tier-options)
- `images`: array - see [Business Listing Image Fields](#business-listing-image-fields-nested-object)
- `gallery_images`: array - same shape as `images` (max 5 on create/update)
- `avg_rating`: number (computed field, average of all review ratings)
- `review_count`: integer (computed field, total number of reviews)
- `created_at`: string (ISO datetime, read-only)
- `updated_at`: string (ISO datetime, read-only)

### Business Listing Image Fields (nested object)
- `id`: UUID (Primary Key, read-only)
- `image`: string (URL)
- `created_at`: string (ISO datetime, read-only)
- `updated_at`: string (ISO datetime, read-only)

### Tab item fields (nested object)
- `id`: UUID (Primary Key, read-only)
- `name`: string
- `image`: string (URL)
- `price`: string or number (decimal, non-negative)
- `created_at`: string (ISO datetime, read-only)
- `updated_at`: string (ISO datetime, read-only)

**Tier limits (authenticated owner):** Listings on the **basic** tier (`basic_business_listing`) may have at most **5** tab items per tab when creating a tab, replacing `tab_items` on PATCH, or POSTing a new item. **Premium** tier (`premium_business_listing`) has no such limit in the API. Exceeding the basic limit returns `400 Bad Request` with a `tier` field (see [Business tab APIs](#business-tab-apis)).

### Business Review Fields (nested object)
- `id`: UUID (Primary Key, read-only)
- `rating`: integer (1-5)
- `comment`: text
- `full_name`: string (denormalized user data, read-only)
- `profile_picture`: string (URL, optional, read-only)
- `images`: array - see [Review Image Fields](#review-image-fields-nested-object)
- `created_at`: string (ISO datetime, read-only)
- `updated_at`: string (ISO datetime, read-only)

### Review Image Fields (nested object)
- `id`: UUID (Primary Key, read-only)
- `image`: string (URL)
- `created_at`: string (ISO datetime, read-only)
- `updated_at`: string (ISO datetime, read-only)

### Business hours row fields
Each element describes one day for the listing (stored in `BusinessHours`; unique per `(business_listing, day_of_week)`).

- `day_of_week`: string — `monday` … `sunday`
- `open_time`: string — time (`HH:MM:SS` in JSON)
- `close_time`: string — time (`HH:MM:SS`)
- `slot_duration`: integer — minutes per bookable slot (**omitted** in API responses for **basic** tier listings; still used server-side when applicable)
- `capacity`: integer — max concurrent bookings per slot (**omitted** for **basic** tier in responses)
- `status`: string — `active` or `inactive` (only **active** days participate in availability and booking)

### Booking object fields (read)
Returned by owner and customer booking endpoints (shape from `BookingSerializer` / related serializers).

- `id`: UUID (Primary Key)
- `full_name`: string — denormalized from user profile at creation time
- `profile_picture`: string (URL) or empty — from user profile at creation time
- `email`: string — contact email supplied by the customer when booking
- `phone_number`: string — contact phone supplied when booking
- `start_time`: string (ISO datetime) — start of the reserved slot
- `end_time`: string (ISO datetime) — end of the slot (derived from `slot_duration` for that day)

---

## Authentication & Authorization

### Authentication
All endpoints except registration require Bearer token authentication with business role:
- `Authorization: Bearer <access_token>`

### Roles & Permissions
- **Authenticated User**: `/business-listing/register` (POST) — any authenticated user may submit a listing (subject to uniqueness constraints)
- **Business Role (`basic_business_listing` or `premium_business_listing`)**: `/business-listing/me` (GET, PATCH), `/business-listing/me/reviews` (GET), `/business-listing/me/business-hours` (GET, POST, PUT), `/business-listing/me/tab` and `/business-listing/me/tab/items` (GET, POST, PATCH, DELETE) — manage the optional **tab** (e.g. menu-style items). **Basic** tier is limited to **5** tab items per tab; **premium** tier is not.
- **Premium Business Role (`premium_business_listing`)**: `/business-listing/me/bookings` (GET) — list customer bookings for the authenticated **premium** listing (see [Business bookings (owner)](#business-bookings-owner)).

---

## Error Responses
- `400 Bad Request`: Invalid input data, validation errors.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Insufficient permissions (user does not have required role).
- `404 Not Found`: Resource does not exist.
- `409 Conflict`: Resource already exists (duplicate registration).
- `500 Internal Server Error`: Unexpected server error.

---

## Notes
- All endpoints use JSON request/response format.
- Business registration creates an unapproved listing pending admin approval. **`business_hours` are not set at registration**; they are stored in separate `BusinessHours` rows and are created or replaced via `/business-listing/me/business-hours` after the listing exists (typically once **approved**).
- Registration sends a confirmation email to the provided business email.
- Profile images and gallery images are limited to a maximum of 5 each (`images` and `gallery_images`).
- Each listing may have at most one **tab**; creating a second tab returns a validation error.
- **Basic** tier: at most **5** tab items per tab (enforced on tab create, tab `tab_items` replace, and adding an item). **Premium** tier: no item-count cap in the API.
- HTML content in text fields is sanitized using bleach.
- UUIDs must be valid for endpoints requiring `<uuid:id>`.

---

## Business Registration API

POST /api/business-listing/register
---
**Description**
Allows authenticated users to register a new business listing by providing business information. Creates a business listing application pending admin approval.

**Frontend usage**
Used in the business listing onboarding flow where users can apply to list their business by filling out registration forms.

- URL Parameters
  - None

- Available Query Parameters
  - None

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *authenticated user*

- **Request body:**

```json
{
  "business_name": "The Coffee House",
  "business_category": "cafe",
  "year_established": "2020-03-15",
  "description": "A cozy coffee shop offering premium locally-sourced coffee and fresh pastries in the heart of Osu.",
  "phone_number": "+233244123456",
  "whatsapp_number": "+233244123457",
  "email": "contact@thecoffeehouse.com",
  "website_url": "https://thecoffeehouse.com",
  "instagram": "thecoffeehouse_gh",
  "twitter": "thecoffeehousegh",
  "tiktok": "@thecoffeehouse",
  "facebook": "",
  "address": "15 Oxford Street, Osu, Accra",
  "geo_coordinates": {
    "latitude": 5.5560,
    "longitude": -0.1870
  },
  "city": "Accra",
  "region": "Greater Accra",
  "tier": "premium_business_listing",
  "images": [
    {"image": "https://example.com/coffee-house-main.jpg"},
    {"image": "https://example.com/coffee-house-interior.jpg"}
  ],
  "gallery_images": [
    {"image": "https://example.com/coffee-house-gallery-1.jpg"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `business_name` | string | Yes | Name of the business (max 255 chars, unique) |
| `business_category` | string | Yes | Category of the business (see [Business Category Options](#business-category-options)) |
| `year_established` | date | Yes | Date when business was established (ISO format) |
| `description` | text | Yes | Detailed description of the business |
| `phone_number` | string | Yes | Contact phone number (max 20 chars, unique) |
| `whatsapp_number` | string | Yes | WhatsApp contact number (max 20 chars, unique) |
| `email` | string | Yes | Business email address |
| `website_url` | string | No | Business website URL |
| `instagram` | string | Yes | Instagram handle or URL |
| `twitter` | string | Yes | X/Twitter handle or URL |
| `tiktok` | string | Yes | TikTok handle or URL |
| `facebook` | string | No | Facebook URL (may be empty string) |
| `address` | string | Yes | Full street address (max 255 chars) |
| `geo_coordinates` | object | Yes | GPS coordinates with `latitude` and `longitude` |
| `city` | string | Yes | City name (max 255 chars) |
| `region` | string | Yes | Region name (max 255 chars) |
| `tier` | string | No | Business tier (default: `basic_business_listing`) |
| `images` | array | No | Primary listing images (max 5) |
| `gallery_images` | array | No | Additional gallery images (max 5) |

- **Response body:** `201 Created` — created listing (`status` is typically `pending` until admin approves). `business_hours` is always an empty array until configured via [POST /api/business-listing/me/business-hours](#post-apibusiness-listingmebusiness-hours).

```json
{
  "id": "12345678-1234-5678-9012-123456789abc",
  "business_name": "The Coffee House",
  "business_category": "cafe",
  "year_established": "2020-03-15",
  "description": "A cozy coffee shop offering premium locally-sourced coffee and fresh pastries in the heart of Osu.",
  "phone_number": "+233244123456",
  "whatsapp_number": "+233244123457",
  "email": "contact@thecoffeehouse.com",
  "website_url": "https://thecoffeehouse.com",
  "instagram": "thecoffeehouse_gh",
  "twitter": "thecoffeehousegh",
  "tiktok": "@thecoffeehouse",
  "facebook": "",
  "address": "15 Oxford Street, Osu, Accra",
  "geo_coordinates": {
    "latitude": 5.5560,
    "longitude": -0.1870
  },
  "city": "Accra",
  "region": "Greater Accra",
  "business_hours": [],
  "tier": "premium_business_listing",
  "status": "pending",
  "images": [
    {
      "id": "87654321-4321-8765-2109-cba987654321",
      "image": "https://example.com/coffee-house-main.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    },
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "image": "https://example.com/coffee-house-interior.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    }
  ],
  "gallery_images": [
    {
      "id": "33333333-3333-3333-3333-333333333333",
      "image": "https://example.com/coffee-house-gallery-1.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    }
  ],
  "avg_rating": null,
  "review_count": 0,
  "created_at": "2025-09-12T10:30:45.123456Z",
  "updated_at": "2025-09-12T10:30:45.123456Z"
}
```

- **Error Response**
  - `400 Bad Request` — validation errors (DRF format), e.g.:

```json
{
  "phone_number": ["business listing with this phone number already exists."]
}
```

  - `401 Unauthorized`: Missing or invalid token.
  - `500 Internal Server Error` — e.g. email failure:

```json
{
  "error": "<message from exception>"
}
```

---

## Business Profile APIs

GET /api/business-listing/me
---
**Description**
Returns the complete profile information of the authenticated business listing owner, including business details, images, and review statistics.

**Frontend usage**
Used in business dashboard to display the business owner's own listing information and profile.

- URL Parameters
  - None

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — full listing for the authenticated owner (must be `approved`).

```json
{
  "id": "12345678-1234-5678-9012-123456789abc",
  "business_name": "The Coffee House",
  "business_category": "cafe",
  "year_established": "2020-03-15",
  "description": "A cozy coffee shop offering premium locally-sourced coffee and fresh pastries in the heart of Osu.",
  "phone_number": "+233244123456",
  "whatsapp_number": "+233244123457",
  "email": "contact@thecoffeehouse.com",
  "website_url": "https://thecoffeehouse.com",
  "instagram": "thecoffeehouse_gh",
  "twitter": "thecoffeehousegh",
  "tiktok": "@thecoffeehouse",
  "facebook": "",
  "address": "15 Oxford Street, Osu, Accra",
  "geo_coordinates": {
    "latitude": 5.5560,
    "longitude": -0.1870
  },
  "city": "Accra",
  "region": "Greater Accra",
  "business_hours": [
    {
      "day_of_week": "monday",
      "open_time": "08:00:00",
      "close_time": "20:00:00",
      "slot_duration": 30,
      "capacity": 2,
      "status": "active"
    },
    {
      "day_of_week": "tuesday",
      "open_time": "08:00:00",
      "close_time": "20:00:00",
      "slot_duration": 30,
      "capacity": 2,
      "status": "active"
    }
  ],
  "tier": "premium_business_listing",
  "status": "approved",
  "images": [
    {
      "id": "87654321-4321-8765-2109-cba987654321",
      "image": "https://example.com/coffee-house-main.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    },
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "image": "https://example.com/coffee-house-interior.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    }
  ],
  "gallery_images": [],
  "avg_rating": 4.5,
  "review_count": 28,
  "created_at": "2025-09-12T10:30:45.123456Z",
  "updated_at": "2025-09-12T12:15:30.123456Z"
}
```

*(Example truncated: a full listing may include up to seven rows, one per weekday.)* For **basic** tier, `slot_duration` and `capacity` are omitted from each row in responses but still drive scheduling.

- **Error Response**
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have business role.
  - `404 Not Found`: Business listing not found or not approved.


PATCH /api/business-listing/me
---
**Description**
Updates the authenticated business listing owner's profile information. Allows partial updates to business details and images. **`business_hours` is read-only here** — use [Business hours APIs](#business-hours-apis) to create or replace weekly hours.

**Frontend usage**
Used in business profile settings page to update business information, contact details, and images.

- URL Parameters
  - None

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** JSON object; all keys optional (partial update). Send only fields to change.

```json
{
  "business_name": "The Coffee House - Osu Branch",
  "description": "An updated description of the coffee shop with new offerings.",
  "phone_number": "+233244567890",
  "whatsapp_number": "+233244567891",
  "email": "osu@thecoffeehouse.com",
  "website_url": "https://osu.thecoffeehouse.com",
  "instagram": "thecoffeehouse_osu",
  "twitter": "thecoffeehousegh",
  "tiktok": "@thecoffeehouse",
  "facebook": "",
  "address": "22 Oxford Street, Osu, Accra",
  "geo_coordinates": {
    "latitude": 5.5565,
    "longitude": -0.1875
  },
  "city": "Accra",
  "region": "Greater Accra",
  "images": [
    {"image": "https://example.com/coffee-house-new-main.jpg"},
    {"image": "https://example.com/coffee-house-new-interior.jpg"},
    {"image": "https://example.com/coffee-house-menu.jpg"}
  ],
  "gallery_images": [
    {"image": "https://example.com/gallery-1.jpg"}
  ]
}
```

- **Update Behavior**
  - **Basic fields**: Updated individually.
  - **`images` / `gallery_images`**: When provided, existing rows for that collection are replaced; removed images are deleted from S3.
  - **Omitted fields**: Remain unchanged.
  - **Read-only fields**: `id`, `status`, `business_hours`, `created_at`, `updated_at` cannot be modified via this endpoint.

- **Response body:** `200 OK` — full listing after update (same schema as GET `/me`).

```json
{
  "id": "12345678-1234-5678-9012-123456789abc",
  "business_name": "The Coffee House - Osu Branch",
  "business_category": "cafe",
  "year_established": "2020-03-15",
  "description": "An updated description of the coffee shop with new offerings.",
  "phone_number": "+233244567890",
  "whatsapp_number": "+233244567891",
  "email": "osu@thecoffeehouse.com",
  "website_url": "https://osu.thecoffeehouse.com",
  "instagram": "thecoffeehouse_osu",
  "twitter": "thecoffeehousegh",
  "tiktok": "@thecoffeehouse",
  "facebook": "",
  "address": "22 Oxford Street, Osu, Accra",
  "geo_coordinates": {
    "latitude": 5.5565,
    "longitude": -0.1875
  },
  "city": "Accra",
  "region": "Greater Accra",
  "business_hours": [
    {
      "day_of_week": "monday",
      "open_time": "08:00:00",
      "close_time": "20:00:00",
      "slot_duration": 30,
      "capacity": 2,
      "status": "active"
    }
  ],
  "tier": "premium_business_listing",
  "status": "approved",
  "images": [
    {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "image": "https://example.com/coffee-house-new-main.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T14:00:00.123456Z"
    },
    {
      "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "image": "https://example.com/coffee-house-new-interior.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T14:00:00.123456Z"
    },
    {
      "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
      "image": "https://example.com/coffee-house-menu.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T14:00:00.123456Z"
    }
  ],
  "gallery_images": [
    {
      "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
      "image": "https://example.com/gallery-1.jpg",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T14:00:00.123456Z"
    }
  ],
  "avg_rating": 4.5,
  "review_count": 28,
  "created_at": "2025-09-12T10:30:45.123456Z",
  "updated_at": "2025-09-12T14:00:00.123456Z"
}
```

- **Error Response**
  - `400 Bad Request`: Invalid input data or validation errors (e.g., more than 5 images).
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have business role.
  - `404 Not Found`: Business listing not found or not approved.


GET /api/business-listing/me/reviews
---
**Description**
Returns a paginated list of all reviews for the authenticated business listing owner's business.

**Frontend usage**
Used in business dashboard to view customer reviews and feedback for their listing.

- URL Parameters
  - None

- Available Query Parameters
  - `page={int}`: Page number for pagination (default: 1)
  - `page_size={int}`: Number of items per page (default: 20, max: 100)

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — paginated reviews for the caller’s listing.

```json
{
  "count": 28,
  "next": "http://localhost:8000/api/business-listing/me/reviews?page=2",
  "previous": null,
  "results": [
    {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "rating": 5,
      "comment": "Excellent coffee and amazing atmosphere! The staff were very friendly.",
      "full_name": "Jane Doe",
      "profile_picture": "https://example.com/jane-profile.jpg",
      "images": [
        {
          "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
          "image": "https://example.com/review-photo-1.jpg",
          "created_at": "2025-09-15T14:30:00.123456Z",
          "updated_at": "2025-09-15T14:30:00.123456Z"
        }
      ],
      "created_at": "2025-09-15T14:30:00.123456Z",
      "updated_at": "2025-09-15T14:30:00.123456Z"
    },
    {
      "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
      "rating": 4,
      "comment": "Great pastries and comfortable seating. Would recommend!",
      "full_name": "John Smith",
      "profile_picture": "https://example.com/john-profile.jpg",
      "images": [],
      "created_at": "2025-09-14T10:15:00.123456Z",
      "updated_at": "2025-09-14T10:15:00.123456Z"
    },
    ...
  ]
}
```

- **Error Response**
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have business role.
  - `404 Not Found`: Business listing not found.

---

## Business hours APIs

Weekly availability is stored as up to **seven** `BusinessHours` rows per listing (`monday` … `sunday`, unique per day). Owners send **exactly seven** objects in array order for **POST** (create) and **PUT** (replace). Each day can be marked `active` or `inactive`; **inactive** days are ignored for public availability and customer booking (see **Public_API_Contracts.md** — `GET .../availability`, `POST .../bookings`).

For **premium** listings, responses include `slot_duration` (minutes) and `capacity` (bookings allowed per slot). **Basic** tier responses **hide** `slot_duration` and `capacity`, but the server still uses stored values (defaults: 30 minutes, 1 booking per slot) when generating slots.

GET /api/business-listing/me/business-hours
---
**Description**
Returns the authenticated listing’s `BusinessHours` rows, ordered Monday–Sunday.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Response body:** `200 OK`

```json
{
  "results": [
    {
      "day_of_week": "monday",
      "open_time": "08:00:00",
      "close_time": "20:00:00",
      "slot_duration": 30,
      "capacity": 2,
      "status": "active"
    }
  ]
}
```

- **Error Response**
  - `401 Unauthorized` / `403 Forbidden` — not a business user.
  - `404 Not Found` — listing not found or not approved.


POST /api/business-listing/me/business-hours
---
**Description**
Creates weekly hours for the listing. Body must be a **JSON array of exactly seven** day objects.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** Array of seven objects (example shows two entries; the real request must include all seven days):

```json
[
  {
    "day_of_week": "monday",
    "open_time": "08:00:00",
    "close_time": "20:00:00",
    "slot_duration": 30,
    "capacity": 2,
    "status": "active"
  },
  {
    "day_of_week": "tuesday",
    "open_time": "08:00:00",
    "close_time": "20:00:00",
    "slot_duration": 30,
    "capacity": 2,
    "status": "active"
  }
]
```

- **Response body:** `201 Created` — array of created rows (same field shape as input; premium includes `slot_duration` / `capacity` in response).

- **Error Response**
  - `400 Bad Request` — fewer than seven days:

```json
{
  "days_of_week": ["Incomplete. Object should contain all the days of the week"]
}
```

  - `400 Bad Request` — duplicate weekday in payload / DB constraint:

```json
{
  "days_of_week": ["Cannot have duplicate days of the week"]
}
```

  - `401 Unauthorized` / `403 Forbidden`
  - `404 Not Found` — listing not approved


PUT /api/business-listing/me/business-hours
---
**Description**
Replaces **all** existing `BusinessHours` for the listing with the provided seven-day array (delete + bulk create).

- Headers
  - Same as POST.

- **Request body:** Same rules as POST (seven objects).

- **Response body:** `200 OK` — full replaced array.

- **Error Response** — same validation errors as POST.


---

## Business bookings (owner)

### How booking works (end-to-end)

1. **Configure hours** — The business sets seven `BusinessHours` rows (`active`/`inactive`, open/close, `slot_duration`, `capacity` for premium).  
2. **Public availability** — For **premium** listings only, anyone can call `GET /api/business-listing/{id}/availability?date=YYYY-MM-DD` to get remaining **time slots** for that calendar day.  
3. **Create booking** — An authenticated customer posts to `POST /api/business-listing/{id}/bookings` with `email`, `phone_number`, and `start_time` matching an allowed slot string (`YYYY-MM-DD HH:MM`). The server fills `full_name` / `profile_picture` from the user service, computes `end_time` from `slot_duration`, and enforces capacity with row locking.  
4. **Customer history** — `GET /api/users/me/bookings` lists the caller’s bookings (optional `month` / `date` filters).  
5. **Owner inbox** — `GET /api/business-listing/me/bookings` (**premium business role only**) lists bookings for the owner’s listing, with optional `month` or `date` filters.

**Tier rules in code:** Availability lookup and customer `POST` bookings apply only to listings with `tier: premium_business_listing` and `status: approved`. Basic-tier listings use the same `BusinessHours` model for display where exposed, but public booking endpoints reject non-premium listings with `404`.

GET /api/business-listing/me/bookings
---
**Description**
Paginated list of bookings placed against the authenticated **premium** listing.

- Permission: `premium_business_listing` (`IsPremiumBusiness`).

- Headers
  - `Authorization: Bearer <access_token>` *with `premium_business_listing` role*

- **Query parameters**
  - `month` (optional): `YYYY-MM` — filter bookings in that calendar month.
  - `date` (optional): `YYYY-MM-DD` — filter bookings on that local date.
  - `page`, `page_size` — standard pagination when configured.

- **Response body:** `200 OK` — paginated `BookingSerializer` results, or a plain array if pagination not applied.

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "77777777-7777-7777-7777-777777777777",
      "full_name": "Jane Customer",
      "profile_picture": "https://cdn.example.com/u/jane.png",
      "email": "jane@example.com",
      "phone_number": "+233200000000",
      "start_time": "2026-04-15T14:30:00+00:00",
      "end_time": "2026-04-15T15:00:00+00:00"
    }
  ]
}
```

- **Error Response**
  - `400 Bad Request` — invalid `month` / `date` format (message in `error` string).
  - `401 Unauthorized` / `403 Forbidden` — not premium business or not authenticated.
  - `404 Not Found` — approved listing not found for the authenticated user.


---

## Business tab APIs

Approved listings on **either** tier may define one **tab** (e.g. menu) with multiple **tab items**. These routes require a business Keycloak role: `basic_business_listing` or `premium_business_listing` (`IsBusiness`).

**Basic tier (`basic_business_listing`):** at most **5** tab items per tab. This applies when:

- POST `/business-listing/me/tab` — `tab_items` array length must be 1–5.
- PATCH `/business-listing/me/tab` — if `tab_items` is sent, the new list length must be 1–5.
- POST `/business-listing/me/tab/items` — rejected if the tab already has **5** items.

**Premium tier (`premium_business_listing`):** no item-count limit in the API.

**Error shape (tier limit):** `400 Bad Request` with a `tier` field, for example:

```json
{
  "tier": ["basic tier is only allowed 5 items"]
}
```

GET /api/business-listing/me/tab
---
**Description**
Returns the tab display name for the authenticated listing.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK`

```json
{
  "tab name": "Menu"
}
```

- **Error Response** — `404 Not Found`

```json
{
  "error": "Tab does not exist"
}
```


POST /api/business-listing/me/tab
---
**Description**
Creates the single tab for this listing. At least one `tab_items` entry is required. A second tab for the same listing is rejected (integrity / validation). **Basic** tier: at most **5** items in `tab_items`.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:**

```json
{
  "name": "Menu",
  "tab_items": [
    {
      "name": "Cappuccino",
      "image": "https://example.com/cappuccino.jpg",
      "price": "18.00"
    },
    {
      "name": "Espresso",
      "image": "https://example.com/espresso.jpg",
      "price": "12.50"
    }
  ]
}
```

- **Response body:** `201 Created` — tab payload including nested items with server-generated `id` and timestamps.

```json
{
  "name": "Menu",
  "tab_items": [
    {
      "id": "99999999-9999-9999-9999-999999999999",
      "name": "Cappuccino",
      "image": "https://example.com/cappuccino.jpg",
      "price": "18.00",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    },
    {
      "id": "88888888-8888-8888-8888-888888888888",
      "name": "Espresso",
      "image": "https://example.com/espresso.jpg",
      "price": "12.50",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    }
  ]
}
```


PATCH /api/business-listing/me/tab
---
**Description**
Partial update of tab `name` and/or `tab_items`. If `tab_items` is sent, existing items are replaced (same semantics as nested update in serializer). **Basic** tier: the replacement list must have at most **5** items.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** Partial JSON (example renames tab and replaces items).

```json
{
  "name": "Drinks menu",
  "tab_items": [
    {
      "name": "Cappuccino",
      "image": "https://example.com/cappuccino-v2.jpg",
      "price": "19.00"
    }
  ]
}
```

- **Response body:** `200 OK` — same shape as POST response (`name` + `tab_items` with ids).

- **Error Response** — `404 Not Found`

```json
{
  "error": "Tab does not exist"
}
```


DELETE /api/business-listing/me/tab
---
**Description**
Deletes the tab and its items.

- Headers
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** None.

- **Response body:** `204 No Content` — empty body.


GET /api/business-listing/me/tab/items
---
**Description**
Paginated list of tab items for the authenticated listing’s tab.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- Query parameters: `page`, `page_size` (same defaults as other list endpoints)

- **Request body:** None (GET; no body).

- **Response body:** `200 OK`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "99999999-9999-9999-9999-999999999999",
      "name": "Cappuccino",
      "image": "https://example.com/cappuccino.jpg",
      "price": "18.00",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    },
    {
      "id": "88888888-8888-8888-8888-888888888888",
      "name": "Espresso",
      "image": "https://example.com/espresso.jpg",
      "price": "12.50",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T10:30:45.123456Z"
    }
  ]
}
```

- **Error Response** — `404 Not Found`

```json
{
  "error": "Tab does not exist"
}
```


POST /api/business-listing/me/tab/items
---
**Description**
Adds one tab item. **Basic** tier: rejected if the tab already has **5** items.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** JSON array.

```json
{
  "name": "Cold brew",
  "image": "https://example.com/cold-brew.jpg",
  "price": "15.00"
}
```

- **Response body:** `201 Created` — array of created tab items.

```json

{
  "id": "77777777-7777-7777-7777-777777777777",
  "name": "Cold brew",
  "image": "https://example.com/cold-brew.jpg",
  "price": "15.00",
  "created_at": "2025-09-12T11:00:00.123456Z",
  "updated_at": "2025-09-12T11:00:00.123456Z"
}

```

- **Error Response** — `404 Not Found`

```json
{
  "error": "Tab does not exist"
}
```

  - `400 Bad Request` — basic tier at 5 items:

```json
{
  "tier": ["basic tier is only allowed 5 items"]
}
```


GET /api/business-listing/me/tab/items/{id}
---
**Description**
Returns one tab item belonging to the authenticated listing’s tab.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK`

```json
{
  "id": "99999999-9999-9999-9999-999999999999",
  "name": "Cappuccino",
  "image": "https://example.com/cappuccino.jpg",
  "price": "18.00",
  "created_at": "2025-09-12T10:30:45.123456Z",
  "updated_at": "2025-09-12T10:30:45.123456Z"
}
```


PATCH /api/business-listing/me/tab/items/{id}
---
**Description**
Partial update of `name`, `image`, and/or `price`.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** Partial fields.

```json
{
  "price": "20.00",
  "name": "Cappuccino (large)"
}
```

- **Response body:** `200 OK` — updated tab item (full object).

```json
{
  "id": "99999999-9999-9999-9999-999999999999",
  "name": "Cappuccino (large)",
  "image": "https://example.com/cappuccino.jpg",
  "price": "20.00",
  "created_at": "2025-09-12T10:30:45.123456Z",
  "updated_at": "2025-09-12T11:15:00.123456Z"
}
```


DELETE /api/business-listing/me/tab/items/{id}
---
**Description**
Deletes a single tab item.

- Headers
  - `Authorization: Bearer <access_token>` *with `basic_business_listing` or `premium_business_listing` role*

- **Request body:** None.

- **Response body:** `204 No Content` — empty body.

- **Common errors (tab group)**
  - `401 Unauthorized`, `403 Forbidden` (missing business role or not business owner context)
  - `400 Bad Request` (validation, duplicate tab item constraint, empty `tab_items` on create, **basic tier** item limit, etc.)
