# API Contract for Business Listing Admin Endpoints

## Table of Contents

1. [Field Specifications and Choices](#field-specifications-and-choices)
   - [Business Category Options](#business-category-options)
   - [Status Options](#status-options)
   - [Tier Options](#tier-options)

2. [Common Response Fields](#common-response-fields)
   - [Business Listing Object Fields](#business-listing-object-fields)
   - [Business Listing Image Fields (nested object)](#business-listing-image-fields-nested-object)
   - [Business Review Fields (nested object)](#business-review-fields-nested-object)
   - [Review Image Fields (nested object)](#review-image-fields-nested-object)
   - [Tab item fields (nested object)](#tab-item-fields-nested-object)

3. [Authentication & Authorization](#authentication--authorization)

4. [Error Responses](#error-responses)

5. [Notes](#notes)

6. [Admin APIs](#admin-apis)
   - [GET /api/admin/business-listing](#get-apiadminbusiness-listing)
   - [GET /api/admin/business-listing/{id}](#get-apiadminbusiness-listingid)
   - [PATCH /api/admin/business-listing/{id}/approve](#patch-apiadminbusiness-listingidapprove)
   - [PATCH /api/admin/business-listing/{id}/reject](#patch-apiadminbusiness-listingidreject)
   - [GET /api/admin/business-listing/{id}/reviews](#get-apiadminbusiness-listingidreviews)

7. [Admin tab APIs (approved listings)](#admin-tab-apis-approved-listings)
   - [GET /api/admin/business-listing/{id}/tab](#get-apiadminbusiness-listingidtab)
   - [PATCH /api/admin/business-listing/{id}/tab](#patch-apiadminbusiness-listingidtab)
   - [DELETE /api/admin/business-listing/{id}/tab](#delete-apiadminbusiness-listingidtab)
   - [GET /api/admin/business-listing/{id}/tab/items](#get-apiadminbusiness-listingidtabitems)
   - [GET /api/admin/business-listing/{id}/tab/items/{item_id}](#get-apiadminbusiness-listingidtabitemsitem_id)
   - [PATCH /api/admin/business-listing/{id}/tab/items/{item_id}](#patch-apiadminbusiness-listingidtabitemsitem_id)
   - [DELETE /api/admin/business-listing/{id}/tab/items/{item_id}](#delete-apiadminbusiness-listingidtabitemsitem_id)

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
- `business_hours`: array (detail) or summary string (list views) — weekly `BusinessHours` rows; see **Business_API_Contracts.md** / **Public_API_Contracts.md**
- `status`: string (choice) - see [Status Options](#status-options)
- `tier`: string (choice) - see [Tier Options](#tier-options)
- `images`: array - see [Business Listing Image Fields](#business-listing-image-fields-nested-object)
- `gallery_images`: array - same shape as listing images
- `avg_rating`: number (computed field, average of all review ratings)
- `review_count`: integer (computed field, total number of reviews)
- `created_at`: string (ISO datetime)
- `updated_at`: string (ISO datetime)

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

### Tab item fields (nested object)
- `id`: UUID (Primary Key)
- `name`: string
- `image`: string (URL)
- `price`: string or number (decimal, non-negative)
- `created_at`: string (ISO datetime)
- `updated_at`: string (ISO datetime)

Owner flows enforce **5** tab items max for **basic** tier. Admin routes reuse the same serializers; the **5-item** rule applies when the **authenticated admin user’s** Keycloak realm roles include `basic_business_listing` (unusual). Typical admin accounts without that role are not limited by this check when patching `tab_items`.

---

## Authentication & Authorization

### Authentication
All admin endpoints require Bearer token authentication with admin role:
- `Authorization: Bearer <access_token>`

### Roles & Permissions
- **Admin Role (`admin`)**: Required for all endpoints in this contract

---

## Error Responses
- `400 Bad Request`: Invalid input data, validation errors.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Insufficient permissions (user does not have admin role).
- `404 Not Found`: Resource does not exist.
- `500 Internal Server Error`: Unexpected server error.
- `503 Service Unavailable`: External service (Keycloak) unavailable.

---

## Notes
- All endpoints use JSON request/response format.
- Business approval assigns Keycloak role and sends notification email.
- Business rejection sends notification email with optional custom message.
- Successful approve/reject responses use the JSON key `detial` (not `detail`).
- **`business_hours`** were moved off `BusinessListing` into the `BusinessHours` table; owners manage them via `/business-listing/me/business-hours`. **Bookings** (premium listings) are created by customers via public APIs; there are no admin booking routes in this service.
- **Admin tab routes** (`/admin/business-listing/{id}/tab` and sub-paths) apply only to listings with `status: "approved"`. There is no admin `POST` to create a tab; owners create tabs via `/business-listing/me/tab` (basic and premium tiers; basic tier limited to **5** items per tab on owner APIs). Admins may **read**, **patch**, **delete** a tab and **read/patch/delete** tab items for moderation or support.
- UUIDs must be valid for endpoints requiring `<uuid:id>`.
- Pagination is available for list endpoints.

---

## Admin APIs

GET /api/admin/business-listing
---
**Description**
Returns a paginated list of all business listings with summary information. Admin-only endpoint for managing business listing applications.

**Frontend usage**
Used in admin dashboard to view all business listing applications and manage approvals.

- URL Parameters
  - None

- Available Query Parameters
  - `q={string}`: Search across business fields (same search as public list; all statuses)
  - `category={string}`: Filter by `business_category`
  - `min_rating={number}`: Minimum average review rating
  - `status={string}`: Filter listings by status (`approved`, `pending`, `rejected`)
    - Ex: `/api/admin/business-listing?status=pending` (pending approvals)
    - Ex: `/api/admin/business-listing?status=approved` (approved listings)
  - `page={int}`: Page number for pagination (default: 1)
  - `page_size={int}`: Number of items per page (default: 20, max: 100)

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — paginated summaries (`count`, `next`, `previous`, `results`). Each result matches the business listing summary fields (includes `status` for pending/rejected/approved).

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/admin/business-listing?page=2",
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
      "status": "pending",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "avg_rating": 4.5,
      "review_count": 28
    },
    ...
  ]
}
```

- **Error Response**
  - `400 Bad Request`: Invalid query parameters.
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have admin role.


GET /api/admin/business-listing/{id}
---
**Description**
Returns detailed information about a specific business listing by their UUID. Admin-only endpoint for individual business review.

**Frontend usage**
Used in admin panel to review individual business listing applications and view complete business profiles for approval decisions.

- URL Parameters
  - *Required: id=[uuid]*

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — full listing (any status); same schema as the public detail response, plus admin may see non-approved listings.

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
    }
  ],
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
  "gallery_images": [],
  "avg_rating": 4.5,
  "review_count": 28,
  "created_at": "2025-09-12T10:30:45.123456Z",
  "updated_at": "2025-09-12T10:30:45.123456Z"
}
```

- **Error Response**
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have admin role.
  - `404 Not Found`: Business listing does not exist.


PATCH /api/admin/business-listing/{id}/approve
---
**Description**
Approves a business listing application and assigns the appropriate tier role in Keycloak. Sends approval notification email to the business.

**Frontend usage**
Used in admin dashboard's business listing approval workflow to approve pending applications.

- URL Parameters
  - *Required: id=[uuid]*

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None (empty body; do not send JSON).

- **Response body:** `200 OK` — approval confirmation.

```json
{
  "detial": "Business 'The Coffee House' has successfully been approved"
}
```

- **Error Response**
  - `200 OK`: Business already approved — response body:

```json
{
  "detail": "Business 'The Coffee House' is already approved"
}
```

  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have admin role.
  - `404 Not Found` — e.g. Keycloak user missing:

```json
{
  "error": "User not Found"
}
```

  - `500 Internal Server Error` — e.g. email or internal error:

```json
{
  "error": "Internal Server Error"
}
```

  - `503 Service Unavailable` — Keycloak unavailable:

```json
{
  "error": "Service unavailable"
}
```


PATCH /api/admin/business-listing/{id}/reject
---
**Description**
Rejects a business listing application and notifies the business via email. Admin-only endpoint for declining business applications with optional rejection message.

**Frontend usage**
Used in admin dashboard's business listing management workflow to reject pending applications with custom rejection reasons.

- URL Parameters
  - *Required: id=[uuid]*

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** Optional fields (JSON object). Omit body or send `{}` to use the default email body server-side.

```json
{
  "message": "Your application was rejected due to incomplete documentation. Please resubmit with all required documents."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | No | Custom rejection message to include in the notification email |

Empty / omitted body is valid:

```json
{}
```

- **Response body:** `200 OK` — rejection confirmation.

```json
{
  "detial": "Business 'The Coffee House' has successfully been rejected"
}
```

- **Error Response**
  - `200 OK`: Business already approved (cannot reject approved business).
```json
{
  "detail": "Business 'The Coffee House' is already approved"
}
```
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have admin role.
  - `404 Not Found`: Business listing does not exist.
  - `500 Internal Server Error`: Error during email sending.


GET /api/admin/business-listing/{id}/reviews
---
**Description**
Returns a paginated list of all reviews for a specific business listing. Admin-only endpoint for reviewing business feedback.

**Frontend usage**
Used in admin panel to view customer reviews for a specific business listing.

- URL Parameters
  - *Required: id=[uuid]*

- Available Query Parameters
  - `page={int}`: Page number for pagination (default: 1)
  - `page_size={int}`: Number of items per page (default: 20, max: 100)

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — paginated reviews for the listing (same review object shape as public reviews).

```json
{
  "count": 28,
  "next": "http://localhost:8000/api/admin/business-listing/12345678-1234-5678-9012-123456789abc/reviews?page=2",
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
    ...
  ]
}
```

- **Error Response**
  - `401 Unauthorized`: Invalid or missing authentication token.
  - `403 Forbidden`: User does not have admin role.
  - `404 Not Found`: Business listing does not exist.


---

## Admin tab APIs (approved listings)

These routes are prefixed with `/api` (e.g. `GET /api/admin/business-listing/{id}/tab`). They require the **admin** role. The path `{id}` is the **business listing UUID**. Tab operations only apply when the listing exists and `status` is **`approved`** (otherwise the server responds with `404`). Tab payloads are the same as owner-facing tab APIs; listings may be basic or premium tier (public tab read applies to either).


GET /api/admin/business-listing/{id}/tab
---
**Description**
Returns the tab display name for an **approved** listing (basic or premium tier).

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

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

Also `404` if the listing is not found or not approved (same lookup rules as the implementation).


PATCH /api/admin/business-listing/{id}/tab
---
**Description**
Partial update of the tab’s `name` and/or `tab_items` (same `TabSerializer` semantics as the owner flow: sending `tab_items` replaces items and may delete unused images from storage). If `tab_items` is provided and the request user has the `basic_business_listing` realm role, at most **5** items are allowed (same as owner **basic** tier rule).

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** JSON object (partial).

```json
{
  "name": "Menu (updated)",
  "tab_items": [
    {
      "name": "Cappuccino",
      "image": "https://example.com/cappuccino.jpg",
      "price": "18.00"
    }
  ]
}
```

- **Response body:** `200 OK` — serialized tab (`name` and `tab_items` with ids and timestamps).

```json
{
  "name": "Menu (updated)",
  "tab_items": [
    {
      "id": "99999999-9999-9999-9999-999999999999",
      "name": "Cappuccino",
      "image": "https://example.com/cappuccino.jpg",
      "price": "18.00",
      "created_at": "2025-09-12T10:30:45.123456Z",
      "updated_at": "2025-09-12T12:00:00.123456Z"
    }
  ]
}
```

- **Error Response**
  - `400 Bad Request` — validation errors (field keys from serializer).
  - `404 Not Found` — `{"error": "Tab does not exist"}` or listing not approved / missing.


DELETE /api/admin/business-listing/{id}/tab
---
**Description**
Deletes the tab and all its items for the given **approved** listing.

- Headers
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None.

- **Response body:** `204 No Content` — empty body.

- **Error Response** — `404 Not Found` if no tab or listing not approved.


GET /api/admin/business-listing/{id}/tab/items
---
**Description**
Paginated list of tab items for the listing’s tab.

- Available Query Parameters
  - `page={int}`, `page_size={int}` (defaults: 20 per page, max 100)

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — paginated list.

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
    }
  ]
}
```

If the request is not paginated and all items fit on one page, the implementation may return a **plain JSON array** of tab item objects instead of the paginated wrapper.

- **Error Response** — `404 Not Found` — `{"error": "Tab does not exist"}` or listing not approved.


GET /api/admin/business-listing/{id}/tab/items/{item_id}
---
**Description**
Returns a single tab item for an approved listing.

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None (GET; no body).

- **Response body:** `200 OK` — one [tab item object](#tab-item-fields-nested-object).

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

- **Error Response** — `404 Not Found`


PATCH /api/admin/business-listing/{id}/tab/items/{item_id}
---
**Description**
Partial update of a tab item (`name`, `image`, `price`).

- Headers
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:**

```json
{
  "price": "20.00",
  "name": "Cappuccino (large)"
}
```

- **Response body:** `200 OK` — full updated tab item object.

- **Error Response** — `400 Bad Request` (validation) or `404 Not Found`.


DELETE /api/admin/business-listing/{id}/tab/items/{item_id}
---
**Description**
Deletes one tab item.

- Headers
  - `Authorization: Bearer <access_token>` *with `admin` role*

- **Request body:** None.

- **Response body:** `204 No Content` — empty body.

- **Error Response** — `404 Not Found`
