# LUMI Gateway Setup

MS Authenticator + Cloudflare Tunnel for secure remote access to LUMI-OS.

## Architecture

```
User (Phone/Browser)
        │
        ▼
┌───────────────────────────────────┐
│  ragnarok.natalie-eiryk.com       │
│  (GitHub Pages)                   │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│  lumi.natalie-eiryk.com           │
│  (Cloudflare Tunnel + Access)     │
│  - MS Entra ID 2FA required       │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│  Your PC (cloudflared service)    │
│  - Bifrost @ localhost:8765       │
│  - Outbound tunnel only           │
│  - No port forwarding needed      │
└───────────────────────────────────┘
```

## Setup Steps

### 1. Install Cloudflared on PC

```powershell
# Option A: winget
winget install Cloudflare.cloudflared

# Option B: Direct download
# https://github.com/cloudflare/cloudflared/releases
```

### 2. Authenticate with Cloudflare

```powershell
cloudflared tunnel login
```

This opens a browser to authenticate with your Cloudflare account.

### 3. Create the Tunnel

```powershell
cloudflared tunnel create lumi-tunnel
```

Save the tunnel ID and credentials file path shown in output.

### 4. Configure DNS

```powershell
# Replace <tunnel-id> with your actual tunnel ID
cloudflared tunnel route dns lumi-tunnel lumi.natalie-eiryk.com
```

### 5. Create Config File

Copy `config.yml.example` to `C:\Users\<you>\.cloudflared\config.yml` and update:
- `tunnel:` with your tunnel ID
- `credentials-file:` with your credentials path

### 6. Test the Tunnel

```powershell
cloudflared tunnel run lumi-tunnel
```

Visit https://lumi.natalie-eiryk.com - should connect to your local Bifrost!

### 7. Install as Windows Service

```powershell
# Run as Administrator
cloudflared service install
net start cloudflared
```

Now the tunnel runs automatically on boot.

---

## Azure AD / MS Entra ID Setup

### 1. Create App Registration

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: `LUMI Remote Access`
4. Supported account types: "Accounts in this organizational directory only" (or Personal if using personal MS account)
5. Redirect URI: `https://<your-team>.cloudflareaccess.com/cdn-cgi/access/callback`
6. Click "Register"

### 2. Get Credentials

From your App Registration:
- **Application (client) ID**: Copy this
- **Directory (tenant) ID**: Copy this

### 3. Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Description: `Cloudflare Access`
4. Expiry: 24 months
5. Copy the **Value** immediately (shown only once)

### 4. API Permissions

1. Go to "API permissions"
2. Add permission → Microsoft Graph → Delegated
3. Add: `openid`, `email`, `profile`
4. Click "Grant admin consent" if you're an admin

---

## Cloudflare Access Setup

### 1. Add Azure AD as Identity Provider

1. Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Settings → Authentication → Login methods
3. Add new → Azure AD
4. Enter:
   - Application ID: (from Azure)
   - Client Secret: (from Azure)
   - Directory ID: (from Azure)
5. Test and Save

### 2. Create Access Application

1. Access → Applications → Add an application
2. Self-hosted application
3. Name: `LUMI Remote`
4. Session Duration: 24 hours
5. Application domain: `lumi.natalie-eiryk.com`
6. Next

### 3. Create Access Policy

1. Policy name: `MS Auth Required`
2. Action: Allow
3. Include:
   - Login Methods → Azure AD
4. Require:
   - Authentication Method → MFA (this enforces MS Authenticator!)
5. Save

---

## Testing

1. Start LUMI-OS on your PC (Bifrost running on 8765)
2. Visit https://lumi.natalie-eiryk.com
3. You should see MS login prompt
4. Complete 2FA with MS Authenticator
5. Cloudflare grants access
6. You're connected to Bifrost!

---

## Troubleshooting

### Tunnel not connecting
```powershell
# Check tunnel status
cloudflared tunnel info lumi-tunnel

# View logs
cloudflared tunnel run --loglevel debug lumi-tunnel
```

### 502 Bad Gateway
- Make sure Bifrost is running: `netstat -an | findstr 8765`
- Check config.yml service URL matches your port

### Access denied after login
- Verify Azure AD is configured correctly in Cloudflare
- Check the policy includes your email/domain
- Ensure MFA is set up on your MS account
