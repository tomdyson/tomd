# tomd.org

A personal blog and website built with [Wagtail CMS](https://wagtail.org/) and deployed on Coolify.

## Tech Stack

- **Backend**: Django 5.2.19 + Wagtail 8.1
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

# Install dependencies (production packages plus black, flake8 and faker)
pip install -r requirements-dev.txt
```

### Dependencies

Direct dependencies are listed in `requirements.in` and development tools in `requirements-dev.in`. `requirements.txt` and `requirements-dev.txt` are lock files generated from them with [uv](https://docs.astral.sh/uv/), so don't edit them by hand. The Docker image installs only `requirements.txt`.

After changing an `.in` file, or to upgrade a package, regenerate both lock files:

```bash
uv pip compile requirements.in -o requirements.txt --python-version 3.12 --universal --upgrade-package <package>
```

```bash
uv pip compile requirements-dev.in -o requirements-dev.txt --python-version 3.12 --universal
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
# Downloads the CLI on first run, then builds minified CSS
./build-tailwind.sh

# Build unminified CSS while developing
./tailwindcss -i ./tomd/tailwind/input.css -o ./tomd/static/css/tailwind.css
```

The CLI version is pinned by `TAILWIND_VERSION` in `build-tailwind.sh`. After changing it, delete your local `./tailwindcss` so the script downloads the new one.

### Running the Tests

```bash
python manage.py test
```

GitHub Actions runs the system check, a missing-migrations check, `collectstatic` with production settings and the tests on every pull request and on pushes to `master`. Dependabot opens weekly update PRs for Python packages and GitHub Actions.

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

The container startup command also runs database migrations before starting Gunicorn.

### Docker Build

The Dockerfile:
1. Starts from `python:3.12-slim` and installs the `requirements.txt` lock file
2. Downloads the pinned Tailwind CLI and builds CSS
3. Collects static files
4. Runs gunicorn via `run.sh` as the non-root `app` user

## Development Notes

### Smart Typography

The blog uses the [smartypants](https://pypi.org/project/smartypants/) library to automatically convert:
- Straight quotes ("") → curly quotes ("")
- Dashes (--) → em-dashes (—)
- Apostrophes (') → curly apostrophes (')

### Settings

- Development: `tomd.settings.dev` (DEBUG=True, SQLite, simple SECRET_KEY)
- Production: `tomd.settings.production` (DEBUG=False, PostgreSQL, S3 storage, secure cookies)

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

## License

Copyright © Tom Dyson