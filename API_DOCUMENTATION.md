# Warranties App - API Documentation

## Base URL

```
http://dev.localhost:8000/api/method/warranties.api
```

For production, replace with your production domain.

---

## Authentication

All API calls require authentication using Frappe API keys:

```
Authorization: token api_key:api_secret
```

To generate API keys:
1. Go to User Settings in Frappe
2. Generate API Key and API Secret
3. Include in request headers

---

## Endpoints

### 1. Create Equipment Registration

Creates a new equipment registration record.

**Endpoint:** `POST /api/method/warranties.api.create_equipment_registration`

**Request Body:**
```json
{
  "data": {
    "job_asset_id": 77848,
    "job_number": 155548,
    "job_address": "1268 Point Prim Road, Belfast, PE, Canada",
    "city": "Belfast",
    "province": "PE",
    "postal_code": "C0A 1T0",
    "brand": "QBH",
    "indoor_model": "ASYW12PRDWB",
    "indoor_serial": "DT004958C",
    "outdoor_model": "ASH112PRDBWA",
    "outdoor_serial": "DT005447C",
    "install_date": "2025-05-01",
    "asset_type": "HVAC",
    "customer_first_name": "Winston",
    "customer_last_name": "Murchison",
    "customer_email": "customer@example.com",
    "customer_phone": "902-659-2284",
    "contact_role": "Job Contact"
  }
}
```

**Field Mappings:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| job_asset_id | Int | Yes | Unique asset ID from source system |
| job_number | Int | No | Job reference number |
| job_address | String | No | Full installation address |
| city | String | No | City |
| province | Select | No | NB, NS, PE, BC, NL, ON, QC, AB (uppercase) |
| postal_code | String | No | Postal code |
| brand | Link | No | Must match existing HVAC Manufacturer |
| indoor_model | String | No | Indoor unit model number |
| indoor_serial | String | No | Indoor unit serial number |
| outdoor_model | String | No | Outdoor unit model number |
| outdoor_serial | String | No | Outdoor unit serial number |
| install_date | Date | No | Format: YYYY-MM-DD |
| asset_type | Select | No | "HVAC", "Heat Pump", "Ventilation" |
| customer_first_name | String | No | Customer first name |
| customer_last_name | String | No | Customer last name |
| customer_email | String | No | Customer email |
| customer_phone | String | No | Customer phone |
| contact_role | Select | No | "Job Contact", "Property Owner" |

**Response:**
```json
{
  "message": {
    "success": true,
    "name": "EQR-00001",
    "message": "Equipment Registration created successfully"
  }
}
```

---

### 2. Create Warranty Registration

Queues a new warranty for automated processing.

**Endpoint:** `POST /api/method/warranties.api.create_warranty_registration`

**Request Body:**
```json
{
  "data": {
    "registering_as": "Contractor",
    "install_date": "2025-05-01",
    "installation_type": "New Installation",
    "purchase_date": "2025-04-15",
    "dealer_id": "DEALER123",
    "brand": "Fantech",
    "model": "FTX12NMVJUA",
    "serial": "E016399",
    "model1": "RXL12WMVJU9",
    "serial1": "E010330",
    "owner_first_name": "John",
    "owner_last_name": "Smith",
    "owner_email": "john.smith@example.com",
    "owner_phone": "902-555-1234",
    "owner_address": "123 Main St",
    "owner_city": "Halifax",
    "owner_state": "NS",
    "owner_zip": "B3H 1A1",
    "contractor_name": "HVAC Pro Inc",
    "contractor_email": "info@hvacpro.com",
    "contractor_phone": "902-555-5678",
    "contractor_address": "456 Industrial Ave",
    "contractor_city": "Dartmouth",
    "contractor_state": "NS",
    "contractor_zip": "B3B 1A1"
  }
}
```

**Response:**
```json
{
  "message": {
    "success": true,
    "name": "WRG-00001",
    "message": "Warranty Registration queued for processing"
  }
}
```

---

### 3. Update Warranty Status (AWS Step Function Callback)

Updates warranty processing status after Step Function completes.

**Endpoint:** `POST /api/method/warranties.api.update_warranty_status`

**Request Body (Success):**
```json
{
  "name": "WRG-00001",
  "status": "Completed",
  "pdf_url": "https://s3.amazonaws.com/bucket/warranty-certificate.pdf"
}
```

**Request Body (Failure):**
```json
{
  "name": "WRG-00001",
  "status": "Failed",
  "error": "Manufacturer portal returned error: Invalid serial number"
}
```

**Valid Status Values:**
- `Processing` - Currently being processed
- `Completed` - Successfully registered with manufacturer
- `Failed` - Registration failed

**Response:**
```json
{
  "message": {
    "success": true,
    "name": "WRG-00001",
    "status": "Completed",
    "message": "Warranty Registration status updated to Completed"
  }
}
```

---

### 4. Get Manufacturer Configuration

Retrieves manufacturer registration configuration for automation.

**Endpoint:** `GET /api/method/warranties.api.get_manufacturer_config`

**Query Parameters:**
```
?brand=Fantech
```

**Response:**
```json
{
  "message": {
    "success": true,
    "brand": "Fantech",
    "type": "Mini-Split Heat Pump",
    "registration_url": "https://fantech.net/warranty",
    "fields_needed": [
      {
        "field_name": "serial_number",
        "field_type": "text",
        "required": true
      },
      {
        "field_name": "install_date",
        "field_type": "date",
        "required": true
      }
    ],
    "markdown_guide": "## Fantech Warranty Registration\n\n1. Navigate to portal..."
  }
}
```

---

### 5. Get Pending Warranties

Retrieves all warranties pending processing.

**Endpoint:** `GET /api/method/warranties.api.get_pending_warranties`

**Response:**
```json
{
  "message": [
    {
      "name": "WRG-00001",
      "brand": "Fantech",
      "model": "FTX12NMVJUA",
      "serial": "E016399",
      "owner_first_name": "John",
      "owner_last_name": "Smith",
      "owner_email_address": "john@example.com",
      "install_date": "2025-05-01"
    }
  ]
}
```

---

### 6. Bulk Import Equipment Registrations

Bulk import multiple equipment registrations.

**Endpoint:** `POST /api/method/warranties.api.bulk_import_equipment`

**Request Body:**
```json
{
  "registrations": [
    {
      "job_asset_id": 77848,
      "job_number": 155548,
      "brand": "QBH",
      "indoor_model": "ASYW12PRDWB",
      "install_date": "2025-05-01",
      "asset_type": "HVAC"
    },
    {
      "job_asset_id": 77849,
      "job_number": 155549,
      "brand": "Fantech",
      "indoor_model": "FTX12NMVJUA",
      "install_date": "2025-05-02",
      "asset_type": "HVAC"
    }
  ]
}
```

**Response:**
```json
{
  "message": {
    "success": true,
    "created_count": 2,
    "error_count": 0,
    "created": ["EQR-00001", "EQR-00002"],
    "errors": []
  }
}
```

---

### 7. Log Agent Activity

Logs agent processing activity for audit trail.

**Endpoint:** `POST /api/method/warranties.api.log_agent_activity`

**Request Body:**
```json
{
  "task": "Fantech Warranty Registration",
  "status": "Success",
  "details": {
    "warranty_id": "WRG-00001",
    "manufacturer_confirmation": "CONF-12345",
    "processing_time_seconds": 45
  }
}
```

**Valid Status Values:**
- `In Progress`
- `Success`
- `Failed`

**Response:**
```json
{
  "message": {
    "success": true,
    "name": "LOG-00001"
  }
}
```

---

## Data Migration Endpoints

Additional endpoints in `warranties.migrate_from_supabase`:

### Import Equipment Batch

**Endpoint:** `POST /api/method/warranties.migrate_from_supabase.import_equipment_batch`

**Request Body:**
```json
{
  "records": [
    {
      "job_asset_id": 77848,
      "job_number": 155548,
      "asset_type": 1,
      "contact_role": "Job Contact",
      ...
    }
  ]
}
```

Note: This endpoint handles automatic mapping:
- `asset_type`: 1 → "HVAC", 2 → "Heat Pump", 8 → "Ventilation"
- `contact_role`: Normalizes various roles to "Job Contact" or "Property Owner"
- `province`: Auto-uppercased

---

### Import Warranty Batch

**Endpoint:** `POST /api/method/warranties.migrate_from_supabase.import_warranty_batch`

---

### Get Migration Status

**Endpoint:** `GET /api/method/warranties.migrate_from_supabase.get_migration_status`

**Response:**
```json
{
  "message": {
    "equipment_registrations": 1071,
    "warranty_registrations": 11,
    "hvac_manufacturers": 19,
    "agent_logs": 0
  }
}
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "exc_type": "ValidationError",
  "exc": "...",
  "_server_messages": "[{\"message\": \"Error description\"}]"
}
```

HTTP Status Codes:
- `200` - Success
- `403` - Authentication required
- `404` - Resource not found
- `417` - Validation error
- `500` - Server error

---

## cURL Examples

### Create Equipment Registration
```bash
curl -X POST "http://dev.localhost:8000/api/method/warranties.api.create_equipment_registration" \
  -H "Authorization: token api_key:api_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "job_asset_id": 77848,
      "brand": "QBH",
      "install_date": "2025-05-01",
      "asset_type": "HVAC"
    }
  }'
```

### Update Warranty Status (AWS Step Function callback)
```bash
curl -X POST "http://dev.localhost:8000/api/method/warranties.api.update_warranty_status" \
  -H "Authorization: token api_key:api_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WRG-00001",
    "status": "Completed",
    "pdf_url": "https://s3.amazonaws.com/bucket/cert.pdf"
  }'
```

---

## Valid HVAC Manufacturers (Brands)

The following brands are configured in the system:

| Brand | Type |
|-------|------|
| Fantech | Mini-Split Heat Pump |
| QBH | Mini-Split Heat Pump |
| Eaton | Mini-Split Heat Pump |
| Square D | Central Heat Pump |
| Schneider | Central Heat Pump |
| Siemens | Mini-Split Heat Pump |
| Federal Pioneer | Central Heat Pump |
| Blue line | Mini-Split Heat Pump |
| General Electric | Mini-Split Heat Pump |
| Leviton | Mini-Split Heat Pump |

---

## Supabase Data Counts (Reference)

| Table | Record Count |
|-------|-------------|
| equipment_registrations | 1,071 |
| warranty_registrations | 11 |
| manufacturers | 19 |
