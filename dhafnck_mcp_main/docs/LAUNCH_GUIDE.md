# DhafnckMCP MVP Launch Guide

## 🚀 Overview

This guide covers the complete deployment and launch process for the DhafnckMCP MVP, including frontend deployment to Vercel, Docker image publishing, and post-launch activities.

## 📋 Pre-Launch Checklist

### Development Readiness
- [ ] All tests passing (`uv run pytest`)
- [ ] Code quality checks passing (`uv run ruff check`)
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Docker image builds successfully

### Infrastructure Readiness
- [ ] Vercel account set up
- [ ] Docker Hub account set up
- [ ] Supabase project configured
- [ ] Domain name configured (if applicable)

### Security Checklist
- [ ] Environment variables secured
- [ ] No sensitive data in repository
- [ ] Docker image security scan passed
- [ ] Frontend security headers configured

## 🛠️ Deployment Process

### Quick Deployment (Recommended)

```bash
# Preview deployment (recommended for first-time)
./scripts/deploy-mvp.sh preview

# Production deployment
./scripts/deploy-mvp.sh production
```

### Manual Deployment Steps

#### 1. Frontend Deployment

```bash
# Deploy to Vercel preview
./scripts/deploy-frontend.sh

# Deploy to Vercel production
./scripts/deploy-frontend.sh --production
```

#### 2. Docker Image Publishing

```bash
# Build and publish Docker image
./scripts/publish-docker.sh
```

#### 3. Verification

```bash
# Test Docker image locally
docker run -p 8000:8000 dhafnck/mcp-server:latest

# Test frontend deployment
# Visit the Vercel URL provided after deployment
```

## 🌐 Deployment Architecture

### Frontend (Vercel)
- **Platform**: Vercel
- **Framework**: Next.js 14
- **Authentication**: Supabase
- **Environment**: Production/Preview

### Backend (Docker)
- **Registry**: Docker Hub
- **Image**: `dhafnck/mcp-server:latest`
- **Runtime**: Python 3.11
- **Protocols**: MCP over stdio/HTTP

### Database
- **Provider**: Supabase
- **Type**: PostgreSQL
- **Features**: Authentication, real-time subscriptions

## 📊 Monitoring & Health Checks

### Frontend Monitoring
- Vercel Analytics (built-in)
- Error tracking via Vercel
- Performance monitoring

### Backend Monitoring
- Docker health checks
- Application logs
- MCP tool availability

### Health Check Endpoints
```bash
# Docker container health
docker ps --filter "name=dhafnck-mcp"

# MCP server tools
docker exec <container> python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
print(f'Tools available: {len(server.get_tools())}')
"
```

## 🔧 Configuration

### Environment Variables

#### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

#### Backend (Docker)
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
DHAFNCK_TOKEN=your_api_token
FASTMCP_LOG_LEVEL=INFO
```

### Vercel Configuration
- Build command: `npm run build`
- Output directory: `.next`
- Node.js version: 18.x
- Environment variables set in Vercel dashboard

## 🚨 Troubleshooting

### Common Issues

#### Frontend Deployment Fails
```bash
# Check build logs
vercel logs <deployment-url>

# Test build locally
cd frontend && npm run build
```

#### Docker Image Build Fails
```bash
# Check Docker logs
docker build --no-cache -t dhafnck/mcp-server:debug .

# Test dependencies
uv sync --locked
```

#### Authentication Issues
```bash
# Verify Supabase configuration
curl -H "apikey: YOUR_ANON_KEY" \
     -H "Authorization: Bearer YOUR_ANON_KEY" \
     "YOUR_SUPABASE_URL/rest/v1/"
```

### Log Locations
- **Vercel**: Vercel dashboard → Functions → Logs
- **Docker**: `docker logs <container-name>`
- **Local**: `./logs/` directory

## 📈 Post-Launch Activities

### Immediate (Day 1)
- [ ] Verify all services are running
- [ ] Test complete user flow
- [ ] Monitor error rates
- [ ] Check performance metrics

### Short-term (Week 1)
- [ ] Gather user feedback
- [ ] Monitor usage patterns
- [ ] Address any critical issues
- [ ] Update documentation based on learnings

### Medium-term (Month 1)
- [ ] Analyze usage metrics
- [ ] Plan feature improvements
- [ ] Optimize performance
- [ ] Scale infrastructure if needed

## 🔗 Useful Links

### Development
- [Repository](https://github.com/dhafnck/dhafnck_mcp)
- [Documentation](./README.md)
- [Docker Hub](https://hub.docker.com/r/dhafnck/mcp-server)

### Monitoring
- Vercel Dashboard
- Docker Hub Repository
- Supabase Dashboard

### Support
- [GitHub Issues](https://github.com/dhafnck/dhafnck_mcp/issues)
- [Documentation](./docs/)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

## 📞 Support

If you encounter issues during deployment:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Open an issue on GitHub with:
   - Deployment mode (preview/production)
   - Error messages
   - Environment details
   - Steps to reproduce

---

**Happy Launching! 🚀** 