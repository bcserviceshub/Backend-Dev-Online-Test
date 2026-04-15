# API Contract for Business Listing Public Endpoints

## Table of Contents

1. [Field Specifications and Choices](#field-specifications-and-choices)
   - [Business Category Options](#business-category-options)
   - [Status Options](#status-options)
   - [Tier Options](#tier-options)

2. [Common Response Fields](#common-response-fields)
   - [Business Listing Object Fields](#business-listing-object-fields)
   - [Business Listing Summary Fields](#business-listing-summary-fields)
   - [Business Listing Image Fields (nested object)](#business-listing-image-fields-nested-object)
   - [Business Review Fields (nested object)](#business-review-fields-nested-object)
   - [Review Image Fields (nested object)](#review-image-fields-nested-object)
   - [Business hours row fields (read)](#business-hours-row-fields-read)
   - [Booking feature (overview)](#booking-feature-overview)

3. [Authentication & Authorization](#authentication--authorization)

4. [Error Responses](#error-responses)

5. [Notes](#notes)

6. [Public APIs](#public-apis)
   - [GET /api/business-listing](#get-apibusiness-listing)
   - [GET /api/business-listing/{id}](#get-apibusiness-listingid)
   - [POST /api/business-listing/{id}/enquiry](#post-apibusiness-listingidenquiry)
   - [GET /api/business-listing/{id}/reviews](#get-apibusiness-listingidreviews)
   - [POST /api/business-listing/{id}/reviews](#post-apibusiness-listingidreviews)
   - [GET /api/business-listing/{id}/availability](#get-apibusiness-listingidavailability)
   - [POST /api/business-listing/{id}/bookings](#post-apibusiness-listingidbookings)
   - [GET /api/users/me/bookings](#get-apiusersmebookings)
   - [GET /api/business-listing/{id}/tab](#get-apibusiness-listingidtab)
   - [GET /api/business-listing/{id}/tab/items](#get-apibusiness-listingidtabitems)
   - [GET /api/business-listing/{id}/tab/items/{item_id}](#get-apibusiness-listingidtabitemsitem_id)

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
- `business_name`: string (max 255 chars)
- `business_category`: string (choice) - see [Business Category Options](#business-category-options)
- `year_established`: date (ISO format)
- `description`: text
- `phone_number`: string (max 20 chars)
- `whatsapp_number`: string (max 20 chars)
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
- `business_hours`: array — see [Business hours row fields (read)](#business-hours-row-fields-read) (detail `GET`). Replaces the former single JSON object on `BusinessListing`.
- `status`: string (choice) - see [Status Options](#status-options)
- `tier`: string (choice) - see [Tier Options](#tier-options)
- `images`: array - see [Business Listing Image Fields](#business-listing-image-fields-nested-object)
- `gallery_images`: array - same shape as listing images; optional extra gallery (max 5 on write)
- `avg_rating`: number (computed field, average of all review ratings)
- `review_count`: integer (computed field, total number of reviews)
- `created_at`: string (ISO datetime)
- `updated_at`: string (ISO datetime)

### Business Listing Summary Fields
- `id`: UUID (Primary Key)
- `business_name`: string
- `address`: string
- `business_hours`: string or null — short human-readable summary of **active** days (e.g. `Mon—Fri: 08:00 AM — 08:00 PM`) derived from `BusinessHours`, or `null` if none configured
- `primary_image`: object (first image from images array) or null
- `business_category`: string
- `tier`: string
- `status`: string
- `created_at`: string (ISO datetime)
- `avg_rating`: number
- `review_count`: integer

### Business Listing Image Fields (nested object)
- `id`: UUID (Primary Key)
- `image`: string (URL)
- `created_at`: string (ISO datetime)
- `updated_at`: string (ISO datetime)

### Business Review Fields (nested object)
- `id`: UUID (Primary Key)
- `rating`: integer (1-5)
- `comment`: text
- `full_name`: string (denormalized user data)
- `profile_picture`: string (URL, optional)
- `images`: array - see [Review Image Fields](#review-image-fields-nested-object)
- `created_at`: string (ISO datetime)
- `updated_at`: string (ISO datetime)

### Review Image Fields (nested object)
- `id`: UUID (Primary Key)
- `image`: string (URL)
- `created_at`: string (ISO datetime)
- `updated_at`: string (ISO datetime)

### Tab item fields (public read)
- `id`: UUID (Primary Key)
- `name`: string
- `image`: string (URL)
- `price`: string or number (decimal, non-negative)
- `created_at`: string (ISO datetime)
- `updated_at`: string (ISO datetime)

Basic-tier listings may expose up to **5** items; premium listings may expose more. Public read shape is unchanged.

### Business hours row fields (read)
Same meaning as in **Business_API_Contracts.md** — each object is one weekday configuration. On **public detail** `GET`, **premium** listings include `slot_duration` and `capacity`; **basic** listings omit those two keys in JSON.

### Booking feature (overview)
Bookings apply to **premium** (`premium_business_listing`), **approved** listings that have **active** `BusinessHours` for the requested day.

- **Slots** — For a given date, open/close times and `slot_duration` split the day into fixed windows (e.g. 30-minute steps).  
- **Capacity** — Each window accepts up to `capacity` bookings; when full, the slot is omitted from availability and rejected on booking.  
- **Customer** — Must be authenticated. Sends contact details + a `start_time` string that matches an allowed slot.  
- **Discovery** — `GET /availability` returns remaining slots; `POST /bookings` creates the reservation.

See endpoint sections below for request/response and errors.

---

## Authentication & Authorization

### Authentication
- **List and Detail endpoints**: No authentication required (public access)
- **Review endpoints**: 
  - GET: No authentication required (public read)
  - POST: Bearer token authentication required
- **Enquiry endpoint**: POST requires Bearer token authentication (inherits project default permission)
- **Availability**: `GET /business-listing/{id}/availability` — **no** authentication (`AllowAny`)
- **Bookings**: `POST /business-listing/{id}/bookings` and `GET /users/me/bookings` — **Bearer token required** (`IsAuthenticated` default)

### Roles & Permissions
- **Public Access**: `/business-listing` (GET), `/business-listing/{id}` (GET), `/business-listing/{id}/reviews` (GET), `/business-listing/{id}/availability` (GET), `/business-listing/{id}/tab` (GET), `/business-listing/{id}/tab/items` (GET), `/business-listing/{id}/tab/items/{item_id}` (GET)
- **Authenticated User**: `/business-listing/{id}/enquiry` (POST) - Submit an enquiry email to the listing’s contact address; `/business-listing/{id}/reviews` (POST) - Any authenticated user can post reviews; `/business-listing/{id}/bookings` (POST) - Create a booking at a premium listing; `/users/me/bookings` (GET) - List the caller’s bookings

---

## Error Responses
- `400 Bad Request`: Invalid input data, validation errors, or business reviewing own listing.
- `401 Unauthorized`: Missing or invalid authentication token (for POST reviews and POST enquiry).
- `404 Not Found`: Resource does not exist or is not approved.
- `500 Internal Server Error`: Unexpected server error.

---

## Notes
- All endpoints use JSON request/response format.
- Only approved business listings are returned in public endpoints.
- Listings on **basic** or **premium** tier may expose a single **tab** (name + items) for public read; if no tab exists, tab endpoints return `404` with `{"error": "Tab does not exist"}`. Basic-tier tabs have at most **5** items when edited by the owner (see business owner API contract).
- Businesses cannot review their own listings.
- Review comments are sanitized using bleach to prevent XSS attacks.
- User profile data (full_name, profile_picture) is fetched from the user service when creating reviews.
- UUIDs must be valid for endpoints requiring `<uuid:id>`.
- Pagination is available for list endpoints.
- Enquiry submissions are sent with Django `send_mail` to the listing’s `email` when configured on the server.
- **Booking** and **availability** APIs apply only to **`premium_business_listing`** listings with **`approved`** status. Configure weekly hours via owner **Business_API_Contracts** (`/business-listing/me/business-hours`) before expecting non-empty `time_slots`.

---

## Public APIs

GET /api/business-listing
---
**Description**
Returns a paginated list of all approved business listings with summary information. Public endpoint for browsing available businesses.

**Frontend usage**
Used on the public business directory page to display a list of approved business listings with basic information and primary images.

- URL Parameters
  - None

- Available Query Parameters
  - `q={string}`: Search across business fields (full-text / trigram search; only `approved` listings)
  - `category={string}`: Filter by `business_category` (see [Business Category Options](#business-category-options))
  - `min_rating={number}`: Minimum average review rating (annotated average; listings with no reviews are treated as 0)
  - `page={int}`: Page number for pagination (default: 1)
  - `page_size={int}`: Number of items per page (default: 20, max: 100)

- Headers
  - `Content-Type: application/json`

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — paginated list (`count`, `next`, `previous`, `results`). Each element matches [Business Listing Summary Fields](#business-listing-summary-fields).

```json
{
  "count": 50,
  "next": "http://localhost:8000/api/business-listing?page=2",
  "previous": null,
  "results": [
    {
      "id": "12345678-1234-5678-9012-123456789abc",
      "business_name": "The Coffee House",
      "address": "15 Oxford Street, Osu, Accra",
      "business_hours": "Mon—Fri: 08:00 AM — 08:00 PM ",
      "primary_image": {
        "id": "87654321-4321-8765-2109-cba987654321",
        "image": "https://example.com/coffee-house-main.jpg"
      },
      "business_category": "cafe",
      "tier": "premium_business_listing",
      "status": "approved",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "avg_rating": 4.5,
      "review_count": 28
    },
    {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "business_name": "Zen Spa & Wellness",
      "address": "10 Ring Road East, Osu, Accra",
      "business_hours": "Mon—Sat: 09:00 AM — 07:00 PM ",
      "primary_image": {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "image": "https://example.com/zen-spa-main.jpg"
      },
      "business_category": "health and wellness",
      "tier": "basic_business_listing",
      "status": "approved",
      "created_at": "2025-09-10T09:00:00.123456Z",
      "avg_rating": 4.8,
      "review_count": 42
    },
    ...
  ]
}
```

- **Error Response**
  - `400 Bad Request`: Invalid query parameters.


GET /api/business-listing/{id}
---
**Description**
Returns detailed information about a specific approved business listing by their UUID. Public endpoint for viewing individual business details.

**Frontend usage**
Used on the business detail page to display comprehensive information about a specific business including all images, contact details, and location.

- URL Parameters
  - *Required: id=[uuid]*

- Headers
  - `Content-Type: application/json`

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — full listing; see [Business Listing Object Fields](#business-listing-object-fields).

```json
{
  "id": "12345678-1234-5678-9012-123456789abc",
  "business_name": "The Coffee House",
  "business_category": "cafe",
  "year_established": "2020-03-15",
  "description": "A cozy coffee shop offering premium locally-sourced coffee and fresh pastries in the heart of Osu. We pride ourselves on creating a welcoming atmosphere for both work and relaxation.",
  "phone_number": "+233244123456",
  "whatsapp_number": "+233244123457",
  "email": "contact@thecoffeehouse.com",
  "website_url": "https://thecoffeehouse.com",
  "instagram": "thecoffeehouse_gh",
  "twitter": "thecoffeehousegh",
  "tiktok": "@thecoffeehouse",
  "facebook": "https://facebook.com/thecoffeehouse",
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
    },
    {
      "id": "22222222-2222-2222-2222-222222222222",
      "image": "https://example.com/coffee-house-menu.jpg",
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
  "avg_rating": 4.5,
  "review_count": 28,
  "created_at": "2025-09-12T10:30:45.123456Z",
  "updated_at": "2025-09-12T12:15:30.123456Z"
}
```

- **Error Response**
  - `404 Not Found`: Business listing does not exist or is not approved.


POST /api/business-listing/{id}/enquiry
---
**Description**
Submits a business enquiry for an approved listing. The server emails the listing’s `email` address (when present) with the sender details and message body. Requires authentication.

**Frontend usage**
Used on the business detail or contact flow so a signed-in user can message the business; the business receives a plain-text email.

- URL Parameters
  - *Required: id=[uuid]*

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *required*

- **Request body:** JSON object with optional string fields (all omitted keys default to empty strings server-side):

```json
{
  "email": "visitor@example.com",
  "number": "+233241234567",
  "message": "Do you take reservations for Saturday evening?"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | No | Visitor contact email |
| `number` | string | No | Visitor phone or WhatsApp number |
| `message` | string | No | Enquiry message |

- **Response body:** `200 OK`

```json
{
  "success": "Enquiry sent"
}
```

- **Error Response**
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `404 Not Found`: Business listing does not exist or is not approved.
  - `500 Internal Server Error`: Email delivery failed or server error; response may include `{"error": "<message>"}`.


GET /api/business-listing/{id}/reviews
---
**Description**
Returns a paginated list of all reviews for a specific approved business listing. Public endpoint for viewing customer feedback.

**Frontend usage**
Used on the business detail page to display customer reviews and ratings for a specific business listing.

- URL Parameters
  - *Required: id=[uuid]*

- Available Query Parameters
  - `page={int}`: Page number for pagination (default: 1)
  - `page_size={int}`: Number of items per page (default: 20, max: 100)

- Headers
  - `Content-Type: application/json`

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — paginated reviews (`count`, `next`, `previous`, `results`). Each review matches [Business Review Fields](#business-review-fields-nested-object).

```json
{
  "count": 28,
  "next": "http://localhost:8000/api/business-listing/12345678-1234-5678-9012-123456789abc/reviews?page=2",
  "previous": null,
  "results": [
    {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "rating": 5,
      "comment": "Excellent coffee and amazing atmosphere! The staff were very friendly and the pastries were fresh.",
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
      "comment": "Great pastries and comfortable seating. Would definitely recommend for a quiet work session.",
      "full_name": "John Smith",
      "profile_picture": "https://example.com/john-profile.jpg",
      "images": [],
      "created_at": "2025-09-14T10:15:00.123456Z",
      "updated_at": "2025-09-14T10:15:00.123456Z"
    },
    {
      "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
      "rating": 5,
      "comment": "Best coffee in Osu! Love the ambiance.",
      "full_name": "Mary Johnson",
      "profile_picture": null,
      "images": [],
      "created_at": "2025-09-13T16:45:00.123456Z",
      "updated_at": "2025-09-13T16:45:00.123456Z"
    },
    ...
  ]
}
```

- **Error Response**
  - `404 Not Found`: Business listing does not exist or is not approved.


POST /api/business-listing/{id}/reviews
---
**Description**
Creates a new review for a specific approved business listing. Authenticated users can leave reviews with ratings, comments, and optional images. Businesses cannot review their own listings.

**Frontend usage**
Used on the business detail page to allow authenticated users to submit reviews for a business they have visited.

- URL Parameters
  - *Required: id=[uuid]*

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *authenticated user*

- **Request body:**

```json
{
  "rating": 5,
  "comment": "Excellent coffee and amazing atmosphere! The staff were very friendly and the pastries were fresh. Highly recommend the cappuccino!",
  "images": [
    {"image": "https://example.com/my-coffee-photo.jpg"},
    {"image": "https://example.com/pastry-photo.jpg"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rating` | integer | Yes | Rating score from 1 to 5 |
| `comment` | text | Yes | Review comment (HTML is sanitized) |
| `images` | array | No | Array of objects with `image` (URL). Omit or use `[]` for text-only reviews |

Minimal example (no photos):

```json
{
  "rating": 4,
  "comment": "Great service and atmosphere."
}
```

- **Response body:** `201 Created` — created review; `full_name` / `profile_picture` are populated from the user service.

```json
{
  "id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
  "rating": 5,
  "comment": "Excellent coffee and amazing atmosphere! The staff were very friendly and the pastries were fresh. Highly recommend the cappuccino!",
  "full_name": "Current User",
  "profile_picture": "https://example.com/current-user-profile.jpg",
  "images": [
    {
      "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
      "image": "https://example.com/my-coffee-photo.jpg",
      "created_at": "2025-09-18T12:00:00.123456Z",
      "updated_at": "2025-09-18T12:00:00.123456Z"
    },
    {
      "id": "11111111-2222-3333-4444-555555555555",
      "image": "https://example.com/pastry-photo.jpg",
      "created_at": "2025-09-18T12:00:00.123456Z",
      "updated_at": "2025-09-18T12:00:00.123456Z"
    }
  ],
  "created_at": "2025-09-18T12:00:00.123456Z",
  "updated_at": "2025-09-18T12:00:00.123456Z"
}
```

- **Error Response**
  - `400 Bad Request` — business cannot review itself:

```json
{
  "error": "Businesses cannot review their own account"
}
```

  - `400 Bad Request` — validation (DRF field errors), e.g. missing `rating`:

```json
{
  "rating": ["This field is required."]
}
```

  - `401 Unauthorized`: Invalid or missing authentication token.
  - `404 Not Found`: Business listing does not exist or is not approved.


GET /api/business-listing/{id}/availability
---
**Description**
Returns bookable **time slots** for a **premium**, **approved** listing on a specific **calendar date**. Slots are generated from the `BusinessHours` row for that weekday (`status` must be `active`). Each slot is `slot_duration` minutes long, from `open_time` up to `close_time`. A slot is included only if the number of existing bookings with that `start_time` is strictly **below** `capacity`.

**Permission:** Public (`AllowAny`) — no `Authorization` header required.

- **URL Parameters**
  - *Required: `id=[uuid]`* — business listing id

- **Query parameters**
  - *Required:* `date=YYYY-MM-DD` — local calendar day to inspect.

- **Headers**
  - `Content-Type: application/json`

- **Response body:** `200 OK`

```json
{
  "time_slots": [
    { "start": "08:00:00", "end": "08:30:00" },
    { "start": "08:30:00", "end": "09:00:00" }
  ]
}
```

If the listing is not premium, not approved, or missing active hours for that weekday, the handler returns **`404`** (listing lookup fails the premium filter). If `date` is missing:

```json
{
  "error": "`date` query parameter required"
}
```

Invalid date format:

```json
{
  "error": "date query parameter '...' does not match format '%Y-%m-%d'"
}
```

If the day is inactive or has no hours, `time_slots` is an empty array `[]`.


POST /api/business-listing/{id}/bookings
---
**Description**
Creates a **Booking** for the authenticated user at an **approved**, **premium** listing. The server copies `full_name` and `profile_picture` from the user profile service, validates that `start_time` matches a legal slot on that day, and enforces **capacity** (row-level lock). **`end_time`** is computed and stored; clients do not send it.

**Permission:** Authenticated user (`IsAuthenticated`).

- **URL Parameters**
  - *Required: `id=[uuid]`* — listing id

- **Headers**
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>`

- **Request body:**

```json
{
  "email": "customer@example.com",
  "phone_number": "+233200000000",
  "start_time": "2026-04-15 14:30"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Customer contact email |
| `phone_number` | string | Yes | Customer phone (max length enforced by model) |
| `start_time` | string | Yes | Must parse as `"%Y-%m-%d %H:%M"` and match a generated slot for that listing/day |

- **Response body:** `201 Created`

```json
{
  "id": "77777777-7777-7777-7777-777777777777",
  "full_name": "Jane Customer",
  "profile_picture": "https://cdn.example.com/u/jane.png",
  "email": "customer@example.com",
  "phone_number": "+233200000000",
  "start_time": "2026-04-15T14:30:00+00:00",
  "end_time": "2026-04-15T15:00:00+00:00"
}
```

- **Error Response**
  - `400 Bad Request` — validation / business rules:

```json
{
  "business": ["business has no Active hours"]
}
```

```json
{
  "start_time": ["Invalid time slot selected"]
}
```

```json
{
  "start_time": ["This time slot is fully booked"]
}
```

  - `400 Bad Request` — unparsable `start_time` (exception message from `strptime`).
  - `401 Unauthorized` — missing/invalid token.
  - `404 Not Found` — listing not **approved** or not **premium** (same queryset as availability).


GET /api/users/me/bookings
---
**Description**
Returns the authenticated user’s bookings across all businesses, newest first. Optional filters match the owner endpoint: `month=YYYY-MM` and/or `date=YYYY-MM-DD`.

**Permission:** Authenticated user.

- **Headers**
  - `Authorization: Bearer <access_token>`

- **Query parameters**
  - `month`, `date`, `page`, `page_size` — same semantics as owner `GET /api/business-listing/me/bookings` in **Business_API_Contracts.md** (invalid formats return `400` with `{ "error": "..." }`).

- **Response body:** `200 OK` — paginated or plain list. Each item includes listing id and business contact fields; `start_time` / `end_time` are **formatted strings** (not ISO) in the default serializer:

```json
{
  "business_listing": "12345678-1234-5678-9012-123456789abc",
  "business_name": "The Coffee House",
  "business_number": "+233244123456",
  "business_email": "contact@thecoffeehouse.com",
  "business_website": "https://thecoffeehouse.com",
  "start_time": "Wednesday 2026-04-15 02:30 PM",
  "end_time": "Wednesday 2026-04-15 03:00 PM"
}
```

- **Error Response**
  - `400 Bad Request` — bad `month` / `date` string.
  - `401 Unauthorized`


GET /api/business-listing/{id}/tab
---
**Description**
Returns the display name of the business’s optional tab (read-only). If the listing has no tab, the response is `404`.

**Frontend usage**
Used on the public business profile to show the tab title when the listing has configured tab content (any tier).

- URL Parameters
  - *Required: id=[uuid]*

- Headers
  - `Content-Type: application/json`

- **Request body:** None (GET; no body).

- **Response body:** `200 OK`

```json
{
  "tab name": "Menu"
}
```

- **Error Response**
  - `404 Not Found` — response body:

```json
{
  "error": "Tab does not exist"
}
```


GET /api/business-listing/{id}/tab/items
---
**Description**
Returns a paginated list of tab items for the business’s tab (menu-style items with name, image, price).

- URL Parameters
  - *Required: id=[uuid]*

- Available Query Parameters
  - `page={int}`: Page number for pagination (default: 1)
  - `page_size={int}`: Number of items per page (default: 20, max: 100)

- Headers
  - `Content-Type: application/json`

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — paginated tab items; each object matches [Tab item fields (public read)](#tab-item-fields-public-read).

```json
{
  "count": 12,
  "next": "http://localhost:8000/api/business-listing/12345678-1234-5678-9012-123456789abc/tab/items?page=2",
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

- **Error Response**
  - `404 Not Found` — e.g. missing tab:

```json
{
  "error": "Tab does not exist"
}
```


GET /api/business-listing/{id}/tab/items/{item_id}
---
**Description**
Returns a single tab item by id for an approved listing.

- URL Parameters
  - *Required: id=[uuid]* (listing id)
  - *Required: item_id=[uuid]*

- Headers
  - `Content-Type: application/json`

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — single tab item.

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

- **Error Response**
  - `404 Not Found`: Item or listing not found, or listing not approved.
