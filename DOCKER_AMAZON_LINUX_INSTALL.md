# 🐳 Install Docker on Amazon Linux - Quick Guide

## ⚡ Quick Install (Copy & Paste)

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Add ec2-user to docker group (to run without sudo)
sudo usermod -aG docker ec2-user

# Verify Docker is running
sudo systemctl status docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

## 🔄 Important: Reconnect After Installation

**You MUST disconnect and reconnect SSH** for the docker group to take effect:

```bash
# Disconnect
exit

# Reconnect
ssh -i "tu-key.pem" ec2-user@IP

# Now test (should work without sudo)
docker ps
```

---

## 📝 Step-by-Step

### 1. Update System
```bash
sudo yum update -y
```

### 2. Install Docker
```bash
sudo yum install -y docker
```

### 3. Start Docker Service
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### 4. Add User to Docker Group
```bash
sudo usermod -aG docker ec2-user
```

### 5. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 6. Verify Installation
```bash
docker --version
docker-compose --version
```

### 7. Test Docker
```bash
# This should work after reconnecting SSH
docker ps
```

---

## ⚠️ If "Permission denied" After Reconnect

```bash
# Give yourself permissions
sudo chmod 666 /var/run/docker.sock

# Or run with sudo temporarily
sudo docker ps
```

---

## 🚀 Quick Deployment After Installation

```bash
# Clone your project
cd ~
git clone TU_REPO
cd Hackmty_Smart_Intelligence

# Copy .env from your local machine or create it
nano .env  # Add your API keys

# Start the app
docker-compose up -d --build
```

---

## 📊 Check Resources

```bash
# See Docker disk usage
docker system df

# See running containers
docker ps

# See logs
docker-compose logs -f
```

---

## 🆘 Troubleshooting

### Docker daemon not running
```bash
sudo systemctl start docker
sudo systemctl status docker
```

### Cannot connect to Docker daemon
```bash
# Add user to group
sudo usermod -aG docker $USER
# Then logout and login again
```

### Out of disk space
```bash
# Check disk
df -h

# Clean Docker
docker system prune -a
```

### Build fails
```bash
# See detailed logs
docker-compose up --build -d
docker-compose logs -f
```

---

## ✅ Complete Setup Script

```bash
#!/bin/bash
# Complete Docker setup for Amazon Linux

echo "📦 Updating system..."
sudo yum update -y

echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

echo "👤 Adding user to docker group..."
sudo usermod -aG docker ec2-user

echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "✅ Verification..."
docker --version
docker-compose --version

echo "⚠️ IMPORTANT: You must disconnect and reconnect SSH for permissions to work"
echo "Then run: docker ps (should work without sudo)"
```

Save as `install-docker.sh` and run:
```bash
chmod +x install-docker.sh
./install-docker.sh
```

---

## 🎯 Next Steps

After installing Docker:

1. **Reconnect SSH** (IMPORTANT!)
2. Verify Docker works: `docker ps`
3. Clone your repo
4. Run: `docker-compose up -d`

---

## 📚 Alternative: Amazon Linux 2023

If using Amazon Linux 2023 with dnf:

```bash
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```

Then install Docker Compose as above.

