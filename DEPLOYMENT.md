# Production RAG System - Deployment Guide

Complete guide to deploy the Production RAG System to production.

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose
- OpenAI API key
- Pinecone API key

### Run Locally

```bash
# Clone repository
git clone https://github.com/saisrikolanu/production-rag-system.git
cd production-rag-system

# Create .env file with your API keys
cp backend/.env.example backend/.env

# Edit backend/.env
# - OPENAI_API_KEY=your_key
# - PINECONE_API_KEY=your_key
# - POSTGRES_PASSWORD=your_password

# Start with Docker Compose
docker-compose up -d
```

Services will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- API Docs: http://localhost:8000/docs

---

## Production Deployment

### Option 1: AWS (Recommended)

#### Architecture

#### Steps

**1. Push to ECR (Elastic Container Registry)**

```bash
# Create ECR repositories
aws ecr create-repository --repository-name rag-backend --region us-east-1
aws ecr create-repository --repository-name rag-frontend --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -t rag-backend ./backend
docker tag rag-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest

# Build and push frontend
docker build -t rag-frontend ./frontend
docker tag rag-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-frontend:latest
```

**2. Create RDS PostgreSQL**

```bash
aws rds create-db-instance \
  --db-instance-identifier rag-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password <strong-password> \
  --allocated-storage 20 \
  --publicly-accessible false
```

**3. Create ECS Cluster**

```bash
# Create cluster
aws ecs create-cluster --cluster-name rag-production

# Create task definitions (use AWS Console or CLI)
# - rag-backend task definition
# - rag-frontend task definition
```

**4. Create Application Load Balancer**

```bash
# Create target groups
aws elbv2 create-target-group --name rag-backend-tg --protocol HTTP --port 8000 --vpc-id <vpc-id>
aws elbv2 create-target-group --name rag-frontend-tg --protocol HTTP --port 3000 --vpc-id <vpc-id>

# Create load balancer
aws elbv2 create-load-balancer --name rag-alb --subnets <subnet-1> <subnet-2>
```

**5. Setup Auto Scaling**

```bash
# Create auto-scaling group for backend
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name rag-backend-asg \
  --launch-template LaunchTemplateName=rag-backend \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2
```

**6. Setup CloudFront**

```bash
# Point to ALB
# Set up origin: ALB endpoint
# Cache behavior: /api/* → backend
# Cache behavior: /* → frontend
```

---

### Option 2: Railway.app (Simplest)

Railway handles containerization and deployment automatically.

**Steps:**

1. Push code to GitHub
2. Go to https://railway.app
3. Click "New Project"
4. Connect GitHub repository
5. Add services:
   - Backend (Docker service from `./backend`)
   - Frontend (Docker service from `./frontend`)
   - PostgreSQL (Railway native)
6. Set environment variables
7. Deploy

**Estimated cost:** $5-20/month for small-medium usage

---

### Option 3: Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create apps
heroku create rag-backend
heroku create rag-frontend

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key -a rag-backend
heroku config:set PINECONE_API_KEY=your_key -a rag-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev -a rag-backend

# Deploy
git push heroku main:main
```

**Cost:** Free tier available, production ~$50+/month

---

## Environment Variables (Production)

### Backend

```env
# API
DEBUG=False
OPENAI_API_KEY=<your-key>
PINECONE_API_KEY=<your-key>

# Database
POSTGRES_HOST=<rds-endpoint>
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=rag_db

# Logging
LOG_LEVEL=INFO
```

### Frontend

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Monitoring & Logging

### CloudWatch (AWS)

```bash
# View logs
aws logs tail /ecs/rag-backend --follow
aws logs tail /ecs/rag-frontend --follow

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name rag-backend-errors \
  --alarm-description "High error rate" \
  --metric-name ErrorCount \
  --namespace AWS/ECS \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### Application Monitoring

The system logs JSON-formatted events to PostgreSQL and stdout:

```bash
# View backend logs
docker logs rag-backend

# Monitor metrics
curl http://localhost:8000/metrics
```

---

## Scaling Strategies

### Horizontal Scaling

```bash
# Increase ECS task count
aws ecs update-service \
  --cluster rag-production \
  --service rag-backend-service \
  --desired-count 5
```

### Vertical Scaling

```bash
# Upgrade RDS instance
aws rds modify-db-instance \
  --db-instance-identifier rag-db \
  --db-instance-class db.t3.small \
  --apply-immediately
```

### Caching Layer

Add Redis for:
- Query result caching
- Rate limiting
- Session management

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

---

## Backups & Disaster Recovery

### Database Backups

```bash
# AWS RDS automated backups
aws rds modify-db-instance \
  --db-instance-identifier rag-db \
  --backup-retention-period 30

# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier rag-db \
  --db-snapshot-identifier rag-db-backup-$(date +%Y%m%d)
```

### Vector Store Backup

```bash
# Pinecone automatically backs up
# Manual export
curl -X GET "https://api.pinecone.io/indexes/production-rag/vectors" \
  -H "Api-Key: $PINECONE_API_KEY" > backup.json
```

---

## Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Set strong database password
- [ ] Rotate API keys regularly
- [ ] Enable database encryption at rest
- [ ] Use VPC security groups
- [ ] Enable VPC logging
- [ ] Set up WAF (Web Application Firewall)
- [ ] Use IAM roles (not static credentials)
- [ ] Enable audit logging
- [ ] Set up DDoS protection

---

## Cost Estimation (AWS)

| Service | Usage | Cost/Month |
|---------|-------|-----------|
| ECS (Backend) | 2-10 tasks | $20-50 |
| ECS (Frontend) | 2-5 tasks | $15-30 |
| RDS PostgreSQL | db.t3.micro | $15-30 |
| ALB | 1 ALB | $20 |
| Data transfer | ~10GB | $5-20 |
| **Total** | | **$75-150** |

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker logs rag-backend

# Check database connection
docker exec rag-backend psql -h postgres -U postgres -d rag_db -c "SELECT 1"

# Check API keys
docker exec rag-backend env | grep OPENAI
```

### Frontend can't reach backend

```bash
# Check CORS headers
curl -H "Origin: http://localhost:3000" http://localhost:8000/health -v

# Check environment variable
docker exec rag-frontend env | grep NEXT_PUBLIC_API_URL
```

### Database connection issues

```bash
# Test connection
psql -h localhost -U postgres -d rag_db -c "SELECT version()"

# Check connections
psql -h localhost -U postgres -d rag_db -c "SELECT count(*) FROM pg_stat_activity"
```

---

## Support & Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **Pinecone Docs**: https://docs.pinecone.io
- **AWS ECS Guide**: https://docs.aws.amazon.com/ecs
- **Railway Docs**: https://docs.railway.app
- **Heroku Docs**: https://devcenter.heroku.com

---

**Need help?** Check logs and API documentation at `/docs`