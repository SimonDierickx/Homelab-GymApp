# sdckx-gym

Personal gym tracking PWA for iPhone. Built for sdckx.be infrastructure.

## Stack
- **Frontend**: Vanilla JS PWA — installable on iPhone home screen
- **Backend**: FastAPI on Claude VM (port 8081)
- **Deploy**: GitHub Actions → webhosting VM via SCP

## Setup

### 1. Config
Copy `config.example.js` → `config.js` and fill in real values.
`config.js` is gitignored and must be deployed manually to `/var/www/sdckx/app/`.

### 2. Backend (Claude VM)
```bash
mkdir -p ~/projects/gym_receiver
cp backend/gym_receiver.py ~/projects/gym_receiver/
cd ~/projects/gym_receiver
python3 -m venv venv
./venv/bin/pip install -r /path/to/backend/requirements.txt
# Add GYM_API_KEY to /opt/claude-coach/.env
sudo cp systemd/gym-receiver.service /etc/systemd/system/
sudo systemctl enable --now gym-receiver
```

### 3. Webhosting VM (nginx)
See nginx block in README — add to `/etc/nginx/sites-available/sdckx`.
Run certbot for `app.sdckx.be`.

### 4. DNS
Add A record `app` → webhosting VM IP in Cloudflare.

### 5. GitHub Actions secrets
- `SSH_HOST`: webhosting VM IP
- `SSH_USER`: webmaster
- `SSH_PRIVATE_KEY`: deploy private key

## Icons
Generate icons at https://realfavicongenerator.net using a barbell SVG.
Place `icon-192.png` and `icon-512.png` in the repo root.
