# Email Setup Guide for R.I.T.H.M

## Using Resend (Recommended)

Resend is a modern email API with a generous free tier (3,000 emails/month).

### Step 1: Create Resend Account

1. Go to **https://resend.com**
2. Click **"Get Started"** / Sign up (GitHub login is easiest)
3. Verify your email

### Step 2: Get Your API Key

1. Once logged in, go to **API Keys** in the sidebar
2. Click **"Create API Key"**
3. Name it `rithm-production`
4. Copy the key (starts with `re_`)
5. **Save it securely** - you won't see it again!

### Step 3: Add Domain (Optional but Recommended)

For better deliverability and professional appearance:

1. Go to **Domains** → **Add Domain**
2. Add your domain (e.g., `rithm.app`)
3. Add the DNS records they provide:
   - **SPF record** (TXT)
   - **DKIM record** (TXT)
   - **Optional:** DMARC record
4. Wait for verification (usually a few minutes)

**Skip for testing:** Resend lets you send from `onboarding@resend.dev` without domain setup.

### Step 4: Configure Railway Environment Variables

In your Railway **rithm app** → **Variables** tab, add:

```
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=re_YOUR_API_KEY_HERE
DEFAULT_FROM_EMAIL=R.I.T.H.M <onboarding@resend.dev>
```

**Replace:**
- `re_YOUR_API_KEY_HERE` → Your actual Resend API key
- `onboarding@resend.dev` → Your verified domain email (e.g., `noreply@rithm.app`) once domain is set up

### Step 5: Test Email

1. Deploy the app (Railway auto-deploys on env var change)
2. Try registering a new account
3. Check your email for the verification link

---

## Alternative Email Providers

### SendGrid
```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_api_key
```

### Mailgun
```
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your_mailgun_password
```

### Gmail (for low volume)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```
Note: Gmail requires an [App Password](https://support.google.com/accounts/answer/185833)

### Amazon SES
```
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_ses_smtp_username
EMAIL_HOST_PASSWORD=your_ses_smtp_password
```

---

## Troubleshooting

### Emails not sending?
1. Check Railway logs for error messages
2. Verify API key is correct
3. Make sure EMAIL_USE_SSL=True and EMAIL_USE_TLS=False for Resend

### Emails going to spam?
1. Set up a custom domain with SPF/DKIM
2. Use a professional "from" address
3. Avoid spam trigger words in subject/body

### Testing locally?
The default `console.EmailBackend` prints emails to terminal instead of sending.
Set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` for local dev.

---

## Current Django Settings

Located in `rithm/settings.py`:

```python
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'R.I.T.H.M <noreply@rithm.app>')

# Auto-switches to SMTP if credentials provided
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.SMTPBackend'
```

---

*Last updated: 2026-02-03*
