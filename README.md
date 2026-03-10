# tomd.org

A personal blog and website built with [Wagtail CMS](https://wagtail.org/) and deployed on Coolify.

## Tech Stack

- **Backend**: Django 5.1.15 + Wagtail 7.3.1
- **Python**: 3.12
- **Styling**: Tailwind CSS (standalone CLI)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Media Storage**: AWS S3 (production) / Local filesystem (development)
- **Static Files**: WhiteNoise
- **CMS Extensions**: wagtail-ai, wagtailmedia
- **Deployment**: Coolify with Docker
- **Monitoring**: Sentry
- **Analytics**: Umami (self-hosted)

## Project Structure

```
tomd/
├── blog/              # Blog post model and templates
├── home/              # Homepage model and templates
├── search/            # Wagtail search functionality
├── tomd/              # Main Django project
│   ├── settings/      # Split settings (base, dev, production)
│   ├── static/        # CSS, fonts, JavaScript
│   └── templates/     # Base templates
├── tailwind.config.js # Tailwind configuration
└── build-tailwind.sh  # Tailwind CSS build script
```

## Local Development

### Prerequisites

- Python 3.12
- Git

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd tomd

# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Development Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Run migrations
python manage.py migrate

# Create a superuser (first time only)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Visit http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ for the Wagtail admin.

### Building Tailwind CSS

The project uses Tailwind CSS with the standalone CLI (no npm required).

```bash
# Download Tailwind CLI (macOS ARM64)
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss

# macOS Intel: use tailwindcss-macos-x64
# Linux: use tailwindcss-linux-x64

# Build CSS (development)
./tailwindcss -i ./tomd/tailwind/input.css -o ./tomd/static/css/tailwind.css

# Build CSS (production, minified)
./tailwindcss -i ./tomd/tailwind/input.css -o ./tomd/static/css/tailwind.css --minify

# Or use the helper script used in Docker builds
./build-tailwind.sh
```

## Content Management

### Page Types

- **HomePage**: Displays live blog posts marked for menus, in reverse chronological order
- **BlogPage**: Individual blog posts with rich content via StreamField
  - Supports headings, paragraphs (with smart typography), images, and embeds

### URL Structure

| Path | Description |
|------|-------------|
| `/` | Homepage (blog listing) |
| `/about/` | About page |
| `/[slug]/` | Individual blog posts |
| `/admin/` | Wagtail admin panel |
| `/django-admin/` | Django admin panel |
| `/documents/` | Wagtail document serving |
| `/x/[path]` | Redirects to the S3 share bucket |

### Adding a New Blog Post

1. Go to `/admin/`
2. Navigate to Pages → Home
3. Click "Add Child Page"
4. Select "Blog Page"
5. Fill in title, date, and body content
6. Save and Publish

## Deployment

### Environment Variables

Required for production:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket for media files |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |

Optional:

| Variable | Description |
|----------|-------------|
| `SENTRY_DSN` | Sentry error tracking DSN |
| `AWS_S3_CUSTOM_DOMAIN` | CloudFront/CDN domain for media |
| `MEDIA_URL` | Custom media URL |

### Deploy to Coolify

Deployments are triggered automatically on push to the `master` branch via Coolify's GitHub integration.

The container startup command also runs database migrations and `collectstatic` before starting Gunicorn.

### Docker Build

The Dockerfile:
1. Installs Python dependencies
2. Downloads Tailwind CLI and builds CSS
3. Collects static files
4. Runs gunicorn via `run.sh`

## Development Notes

### Smart Typography

The blog uses the [smartypants](https://pypi.org/project/smartypants/) library to automatically convert:
- Straight quotes ("") → curly quotes ("")
- Dashes (--) → em-dashes (—)
- Apostrophes (') → curly apostrophes (')

### Settings

- Development: `tomd.settings.dev` (DEBUG=True, SQLite, simple SECRET_KEY)
- Production: `tomd.settings.production` (PostgreSQL, S3 storage)

### Code Quality

```bash
# Format with Black
black .

# Lint with flake8
flake8
```

## Production URLs

- **Main site**: https://tomd.org
- **Admin**: https://tomd.org/admin/

## Documentation

- `CLAUDE.md` - Detailed development guide for AI assistants
- `TEST.md` - Comprehensive testing procedures
- `MIGRATION_PLAN.md` - Architecture migration documentation
- `MIGRATED.md` - Migration completion report

## Notes

- `fly.toml` remains in the repository as legacy infrastructure config, but the active deployment target is Coolify.

## License

Copyright © Tom Dyson