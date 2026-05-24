# User Features Documentation

## Overview

A complete set of user-facing features for the X.509 Certificate Authority system, allowing regular users to manage their certificates and account settings through an intuitive Streamlit interface.

## Created User Features

### 1. **request_certificate.py** 📜
**Purpose:** Allow users to submit certificate requests (CSR) to the CA

**Key Features:**
- Submit new certificate requests with CSR (Certificate Signing Request)
- Configure request details: Common Name, Organization, Country, State
- View all past requests with status tracking
- Support for multiple request purposes: Web Server (TLS/SSL), Client Auth, Email (S/MIME), Code Signing
- Mock data generator: `get_mock_user_requests()`
- Tabs: 
  - "📝 New Request" - Submit new certificate request
  - "📋 My Requests" - View all requests with status

**Data Model:**
- `CertificateRequestOut`: id, user_id, csr_pem, status (PENDING/APPROVED/REJECTED), created_at, reason
- `RequestStatus` enum: PENDING, APPROVED, REJECTED

**Session State:**
- `st.session_state.user_requests` - Stores submitted requests

---

### 2. **my_certificates.py** 📋
**Purpose:** Display and manage user's issued certificates

**Key Features:**
- View all user's certificates in table format with filtering
- Display detailed certificate information
- Show certificate validity period and days until expiration
- Download certificate functionality
- Copy PEM format to clipboard
- Statistics dashboard: Active, Expired, Total certificates
- Tabs:
  - "📄 All Certificates" - Table view of all certificates
  - "🔍 Details" - Detailed view with PEM display

**Data Model:**
- `CertificateOut`: id, serial_number, subject_dn, cert_pem, status (ACTIVE/REVOKED/EXPIRED), valid_from, valid_to, created_at

**Features:**
- Real-time validity tracking
- Color-coded status indicators
- PEM display in styled code block
- Quick actions: Download, Copy, Renew buttons

---

### 3. **profile.py** 👤
**Purpose:** Manage user account information, security, and preferences

**Key Features:**

**Tab 1: Profile**
- View user account information (username, email, organization, country, role)
- Edit profile details (full name, email, organization, country)
- Account status and creation/login timestamps

**Tab 2: Security**
- Change password with strength indicator
- Two-factor authentication (2FA) setup
- Active sessions management
- Password validation (minimum 8 characters, strength color indicators)

**Tab 3: Preferences**
- Notification preferences (email, certificate alerts, approvals, rejections)
- Display settings (theme, items per page)
- Language preferences

**Data Model:**
- `UserProfile`: id, username, email, full_name, organization, country, role, is_active, created_at, last_login

**Features:**
- Password strength indicator (🔴 Weak, 🟡 Medium, 🟢 Strong)
- Comprehensive notification controls
- Theme selector (Dark, Light, Auto)
- Multi-language support

---

### 4. **revoke_certificate.py** 🚫
**Purpose:** Request revocation of user's own certificates

**Key Features:**
- Select certificate to revoke from active certificates
- Choose revocation reason from standardized list
- Add optional notes/comments
- Confirmation warning (irreversible action)
- View revocation request history
- Statistics on revocation requests
- Tabs:
  - "📋 Request Revocation" - Submit new revocation request
  - "📊 Revocation History" - View all revocation requests

**Data Model:**
- `RevocationRequest`: id, certificate_id, serial_number, reason, status, created_at
- `RevocationStatus` enum: PENDING, APPROVED, REJECTED
- `RevocationReason` enum: Key Compromise, Affiliation Changed, Superseded, etc.

**Features:**
- Standardized revocation reasons
- Permanent action warning with confirmation
- Request tracking with timestamps
- Status indicators (🟢 Approved, 🟠 Pending, 🔴 Rejected)

---

### 5. **renew_certificate.py** 🔄
**Purpose:** Renew expiring or expired certificates

**Key Features:**
- Select expiring certificate to renew
- Configure renewal parameters:
  - Validity period (30-3650 days)
  - Hash algorithm (SHA-256, SHA-384, SHA-512)
  - Key size (2048, 3072, 4096)
  - Optional: Use existing CSR
- View renewal history
- Statistics on renewals
- Tabs:
  - "📝 Renew Certificate" - Configure and submit renewal
  - "📊 Renewal History" - View all renewals

**Data Model:**
- `CertificateOut`: id, serial_number, subject_dn, status, valid_from, valid_to

**Features:**
- Automatic expiry date calculation
- Renewal summary before confirmation
- Renewal history tracking with timestamps
- Statistics dashboard

---

## Integration with Main App

### Updated Files

#### **user_dashboard.py** (Enhanced)
- Added imports for all user feature modules
- Integrated navigation buttons with `st.session_state.current_feature`
- Updated button handlers to trigger feature routing
- Features organized in 3 tabs:
  - "⚙️ Account & Keys" - Profile, Password, Import Key
  - "📜 Certificates" - Request, View, Revoke, Download, Renew
  - "🔍 Search & CRL" - Search, View CRL
- Statistics dashboard showing: Active Certificates, Pending Requests, Revoked, Key Pairs
- Back button to login

#### **app.py** (Updated Routing)
```python
from views.user_features import request_certificate, my_certificates, profile, revoke_certificate as user_revoke_certificate, renew_certificate

# User routing logic added:
if st.session_state.current_feature == "request_certificate":
    request_certificate()
elif st.session_state.current_feature == "my_certificates":
    my_certificates()
elif st.session_state.current_feature == "profile":
    profile()
elif st.session_state.current_feature == "revoke_certificate":
    user_revoke_certificate()
elif st.session_state.current_feature == "renew_certificate":
    renew_certificate()
else:
    user_dashboard()
```

---

## Data Models Used

All models based on provided Pydantic schemas:

```python
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: Role
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
```

---

## UI Patterns & Styling

### Consistent Pattern Across All Pages:
1. **Back Button** - Returns to dashboard
2. **Divider & Header** - Clear page title and description
3. **Statistics Dashboard** - Key metrics displayed prominently
4. **Tabs** - Organize related functionality
5. **Form Inputs** - Consistent styling and validation
6. **Summary Boxes** - Color-coded information display
7. **Statistics at Bottom** - Summary metrics footer

### Color Scheme:
- **Primary (Blue):** `#4299e1` - Main actions, info boxes
- **Success (Green):** `#48bb78` - Positive actions, approved status
- **Warning (Orange):** `#ed8936` - Caution, pending status
- **Error (Red):** `#f56565` - Revoked status, errors
- **Background:** `#2d3748`, `#1a1a1a` - Dark theme

### Mock Data Pattern:
Each feature includes:
- `@dataclass` models for mock data
- `get_mock_*()` generator functions
- Realistic data with timestamps and relationships
- Consistent with admin_features structure

---

## Session State Management

Features use session state for:
- `st.session_state.current_feature` - Current page routing
- `st.session_state.user_requests` - User certificate requests
- `st.session_state.revoked_certs` - Revocation tracking
- `st.session_state.renewed_certificates` - Renewal history
- `st.session_state.username`, `.role`, `.user_id` - User info

---

## Testing & Mock Data

All features include realistic mock data:

**Request Certificate:**
- 3 sample requests in PENDING, APPROVED, REJECTED states
- Sample CSR in PEM format

**My Certificates:**
- 3 sample certificates with ACTIVE, EXPIRED statuses
- Realistic validity periods and serial numbers

**Profile:**
- Mock user profile with full details
- Sample password strength calculations

**Revoke Certificate:**
- 2 active certificates available for revocation
- 2 sample revocation requests with timestamps

**Renew Certificate:**
- 2 expiring certificates
- Automatic expiry date calculations

---

## Navigation Flow

```
User Dashboard (Main Hub)
├── Request Certificate
│   ├── New Request
│   └── My Requests
├── My Certificates
│   ├── All Certificates (Table)
│   └── Details (Detailed View)
├── Profile & Settings
│   ├── Profile (Account Info)
│   ├── Security (Password, 2FA)
│   └── Preferences (Notifications, Display)
├── Revoke Certificate
│   ├── Request Revocation
│   └── Revocation History
└── Renew Certificate
    ├── Renew Certificate
    └── Renewal History
```

---

## Features Implemented

- ✅ Certificate request submission with CSR
- ✅ View user's issued certificates
- ✅ Certificate validity tracking
- ✅ Download certificate functionality
- ✅ Profile management
- ✅ Password change with strength indicator
- ✅ Two-factor authentication setup
- ✅ Notification preferences
- ✅ Certificate revocation requests
- ✅ Certificate renewal with configuration
- ✅ Request status tracking
- ✅ Statistics dashboards
- ✅ Session state persistence
- ✅ Back navigation to dashboard
- ✅ Error handling and validation

---

## Ready for Integration

All user features are:
- ✅ Fully functional with mock data
- ✅ Integrated into app.py routing
- ✅ Connected to user_dashboard.py
- ✅ Consistent with admin_features style
- ✅ Properly documented
- ✅ Ready for backend API integration
