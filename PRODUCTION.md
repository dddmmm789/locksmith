# Production Configuration

## Environment Variables
Required environment variables:
- FLASK_APP=run.py
- FLASK_ENV=production
- SECRET_KEY=<secure-key>
- DATABASE_URL=postgresql://user:pass@localhost/db
- GOOGLE_MAPS_API_KEY=<api-key>
- TWILIO_ACCOUNT_SID=<sid>
- TWILIO_AUTH_TOKEN=<token>
- TWILIO_PHONE_NUMBER=<number>

## Database
- PostgreSQL 12+
- Regular backups
- Connection pooling recommended

## Server
- Nginx + Gunicorn
- SSL/TLS required
- Rate limiting configured
- Regular security updates

## Monitoring
- Error logging
- Performance monitoring
- Backup verification
- SSL certificate monitoring
