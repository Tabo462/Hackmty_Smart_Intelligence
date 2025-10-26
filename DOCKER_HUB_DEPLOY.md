# 🐳 Deploy Docker Hub Image on EC2 (No Git Needed)

## ✅ What You Need

- Docker Hub image already built and pushed
- EC2 instance with Docker installed
- Your API keys

## 🚀 Quick Deploy (3 Steps)

### Step 1: Connect to EC2
```bash
ssh -i "tu-key.pem" ec2-user@TU_IP
```

### Step 2: Create docker-compose.yml
```bash
cd ~
nano docker-compose.yml
```

Paste this (update with YOUR Docker Hub image name and credentials):

```yaml
services:
  smart-intelligence-api:
    image: TU_USERNAME/hackmty_smart_intelligence:latest
    container_name: smart-intelligence-api
    ports:
      - "8001:8001"
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
      - GEMINI_API_KEY=AIzaSyDYrBDDTEXVzbb2xAlr2NxZDY4Fqoh4ORw
      - ELEVENLABS_API_KEY=sk_9d1375e7e03e0c325429bf29ac55ee9e8b7d1c932a13cd77
      - SNOWFLAKE_ACCOUNT=HQVIWDY-CG89891
      - SNOWFLAKE_USER=DIEGOGM
      - SNOWFLAKE_PASSWORD=Diegogallo12001
      - SNOWFLAKE_WAREHOUSE=SNOWFLAKE_LEARNING_WH
      - SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
      - SNOWFLAKE_SCHEMA=PUBLIC
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  default:
    name: smart-intelligence-network
```

Press `Ctrl+O` → Enter → `Ctrl+X` to save

### Step 3: Run the Application
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

## 🎉 Done!

Your app is running at: `http://TU_IP:8001`

---

## 🔧 Alternative: Using .env File (Optional)

If you prefer to use an .env file:

### Create .env file:
```bash
nano .env
```

Paste:
```env
GEMINI_API_KEY=AIzaSyDYrBDDTEXVzbb2xAlr2NxZDY4Fqoh4ORw
ELEVENLABS_API_KEY=sk_9d1375e7e03e0c325429bf29ac55ee9e8b7d1c932a13cd77
SNOWFLAKE_ACCOUNT=HQVIWDY-CG89891
SNOWFLAKE_USER=DIEGOGM
SNOWFLAKE_PASSWORD=Diegogallo12001
SNOWFLAKE_WAREHOUSE=SNOWFLAKE_LEARNING_WH
SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

### Modify docker-compose.yml to use .env:
```yaml
services:
  smart-intelligence-api:
    image: TU_USERNAME/hackmty_smart_intelligence:latest
    container_name: smart-intelligence-api
    ports:
      - "8001:8001"
    env_file:
      - .env
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    # ... rest of config
```

---

## 📦 Pull Image from Docker Hub

```bash
# Pull your image
docker pull TU_USERNAME/hackmty_smart_intelligence:latest

# Verify
docker images | grep hackmty
```

---

## 🎯 Complete Setup Script (No Git)

```bash
#!/bin/bash
# Complete deployment WITHOUT git

cd ~

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  smart-intelligence-api:
    image: TU_USERNAME/hackmty_smart_intelligence:latest
    container_name: smart-intelligence-api
    ports:
      - "8001:8001"
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
      - GEMINI_API_KEY=AIzaSyDYrBDDTEXVzbb2xAlr2NxZDY4Fqoh4ORw
      - ELEVENLABS_API_KEY=sk_9d1375e7e03e0c325429bf29ac55ee9e8b7d1c932a13cd77
      - SNOWFLAKE_ACCOUNT=HQVIWDY-CG89891
      - SNOWFLAKE_USER=DIEGOGM
      - SNOWFLAKE_PASSWORD=Diegogallo12001
      - SNOWFLAKE_WAREHOUSE=SNOWFLAKE_LEARNING_WH
      - SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_DB
      - SNOWFLAKE_SCHEMA=PUBLIC
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  default:
    name: smart-intelligence-network
EOF

# Edit to update YOUR Docker Hub image name
nano docker-compose.yml

# Pull and run
docker-compose pull
docker-compose up -d
docker-compose logs -f
```

---

## 🔐 Security: Protecting Your API Keys

### Option A: Use Docker Secrets (More Secure)
```bash
# Create .env file
nano .env

# In docker-compose.yml, use env_file:
env_file:
  - .env

# Protect the file
chmod 600 .env
```

### Option B: Use AWS Secrets Manager (Production)
```bash
# Store secrets in AWS
aws secretsmanager create-secret --name smart-intelligence --secret-string file://.env

# Retrieve in docker-compose
environment:
  - GEMINI_API_KEY=${AWS_SECRET_GEMINI}
```

---

## ✅ Advantages of Using Docker Hub Image

✅ **No Git needed** - Just Docker and Docker Compose  
✅ **Faster deployment** - Image already built  
✅ **Consistent environment** - Same image everywhere  
✅ **Easy updates** - Just pull new image  
✅ **Environment variables** - Pass them directly  

---

## 📋 Common Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Update to new version
docker-compose pull
docker-compose up -d

# Check status
docker-compose ps

# Check logs of specific service
docker-compose logs smart-intelligence-api -f
```

---

## 🎯 Summary

**You DON'T need Git!**

Just:
1. Create `docker-compose.yml` with your env vars
2. Run `docker-compose up -d`
3. Done!

