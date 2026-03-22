# Authentication

HallMaster uses cookie-based ASP.NET session authentication with anti-forgery token protection.

## Login Flow

### Step 1: Get the Login Page

```http
GET /Account/Login
```

Parse the response HTML to extract the `__RequestVerificationToken` from:

```html
<input name="__RequestVerificationToken" type="hidden" value="TOKEN_VALUE" />
```

### Step 2: Submit Login

```http
POST /Account/Login
Content-Type: application/x-www-form-urlencoded

Email=user@example.com&Password=yourpassword&__RequestVerificationToken=TOKEN_VALUE
```

On success, the server returns a **302 redirect** to the dashboard. The response sets ASP.NET session cookies.

On failure, the server returns **200** with the URL still containing `/Account/Login`.

### Step 3: Store Cookies

Save the session cookies for subsequent requests. All authenticated endpoints require these cookies.

## Anti-Forgery Tokens

POST requests require a `__RequestVerificationToken`. There are two ways to include it:

### JSON API Posts

Include the token as a request header:

```http
POST /api/Bookings/CheckAvailability
RequestVerificationToken: TOKEN_VALUE
Content-Type: application/json
```

### MVC Form Posts

Include the token as a form field:

```http
POST /Admin/Bookings/Create
Content-Type: application/x-www-form-urlencoded

__RequestVerificationToken=TOKEN_VALUE&BookingName=Test&...
```

### Getting a Fresh Token

Fetch any authenticated page (e.g., the admin dashboard) and extract the token from the HTML:

```http
GET /Admin/Dashboard/Index/{hall_id}
```

## Session Keepalive

Check if the session is still valid:

```http
GET /api/Scheduler/HasJustLoggedIn
```

Returns **200** if authenticated, or redirects if the session has expired.

## Credentials

HallMaster uses email + password authentication. There are no API keys, OAuth, or Bearer tokens.
