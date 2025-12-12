# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a monolithic Wagtail CMS site for tomd.org. The project was recently consolidated from a headless Wagtail + Nuxt.js architecture into a traditional server-rendered Django/Wagtail application.

**Stack:**
- Django 5.1.4 + Wagtail 6.3.1
- Python 3.12
- PostgreSQL (production) / SQLite (local dev)
- Tailwind CSS (standalone CLI)
- Deployed on Fly.io

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # Use venv/bin/activate if using different venv name

# Install dependencies
pip install -r requirements.txt
```

### Running the Development Server
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run server (uses dev settings by default)
python manage.py runserver

# Server runs at http://127.0.0.1:8000/
```

### Database Operations
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Static Assets

**Building Tailwind CSS:**
```bash
# Download Tailwind CLI (first time only)
# macOS ARM64:
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss

# macOS Intel:
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-x64
chmod +x tailwindcss-macos-x64
mv tailwindcss-macos-x64 tailwindcss

# Linux:
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
mv tailwindcss-linux-x64 tailwindcss

# Build Tailwind CSS (development)
./tailwindcss -i ./tomd/static/css/input.css -o ./tomd/static/css/tailwind.css

# Build Tailwind CSS (production - minified)
./tailwindcss -i ./tomd/static/css/input.css -o ./tomd/static/css/tailwind.css --minify
```

**Collecting Static Files:**
```bash
# Collect static files for deployment
python manage.py collectstatic --noinput
```

### Code Quality
```bash
# Format code with Black
black .

# Run flake8 linter
flake8
```

## Architecture

### Settings Structure
Django settings are split into multiple files:
- `tomd/settings/base.py` - Shared settings
- `tomd/settings/dev.py` - Development (DEBUG=True, simple SECRET_KEY)
- `tomd/settings/production.py` - Production (DEBUG=False, S3 storage)

Default: `tomd.settings.dev` (set in `manage.py`)

### Apps Structure
- **home** - HomePage model, displays blog post listing on the homepage
- **blog** - BlogPage model with StreamField for rich content (headings, paragraphs, images, embeds)
- **search** - Wagtail search functionality (currently basic implementation)
- **tomd** - Main project app (settings, URLs, base templates, static assets)

### Content Models

**HomePage** (`home/models.py`):
- Displays list of blog posts in reverse chronological order
- Filters out pages with `show_in_menus=True` (like the About page)
- No custom fields beyond standard Page fields

**BlogPage** (`blog/models.py`):
- `date` field for post date
- `body` StreamField with these block types:
  - `heading` - CharBlock for headings
  - `paragraph` - Custom RichTextBlock with smartypants formatting (converts straight quotes to smart quotes)
  - `image` - ImageChooserBlock
  - `embed` - EmbedBlock for videos/media
- Custom RichTextBlock applies smartypants typography to convert ASCII quotes/dashes to proper typographic characters

### URL Structure
- `/` - HomePage (blog listing)
- `/about/` - About page (BlogPage with slug "about")
- `/[slug]/` - BlogPage detail pages
- `/admin/` - Wagtail admin
- `/django-admin/` - Django admin
- `/documents/` - Wagtail document serving

### Templates & Styling

**Template Hierarchy:**
- `tomd/templates/base.html` - Base template with header, fonts, analytics
- `home/templates/home/home_page.html` - Homepage blog listing
- `blog/templates/blog/blog_page.html` - Blog post detail page

**Styling:**
- Uses Tailwind CSS (standalone CLI, not npm)
- Input: `tomd/static/css/input.css`
- Output: `tomd/static/css/tailwind.css`
- Config: `tailwind.config.js` in project root
- Custom fonts: Source Serif Pro (self-hosted in `tomd/static/fonts/`)
- Typography: Avenir (headings/nav) + Source Serif Pro (body content)

**JavaScript:**
- `tomd/static/js/tomd.js` - Date formatting and Umami analytics tracking
- Formats dates from YYYY-MM-DD to "Month Day, Year" format
- Tracks clicks on Stripe checkout links via Umami

### Database

**Local Development:**
- SQLite database (`db.sqlite3` in project root)
- Automatically used when `DATABASE_URL` is not set

**Production:**
- PostgreSQL via `DATABASE_URL` environment variable
- Configured through `dj-database-url` package

### Media Storage

**Local Development:**
- Files stored in `media/` directory
- Served by Django when DEBUG=True

**Production:**
- AWS S3 via `django-storages` and `boto3`
- Configured through environment variables:
  - `AWS_STORAGE_BUCKET_NAME`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_S3_CUSTOM_DOMAIN` (optional)

## Important Context

### Recent Migration
This site was recently consolidated from a headless architecture. The following have been removed:
- Django REST Framework API endpoints
- django-cors-headers
- wagtail-headless-preview
- wagtailnetlify
- All API-related code from `blog/api.py`

If you see references to these in old documentation or git history, they are no longer used.

### StreamField JSON Storage
BlogPage uses `use_json_field=True` for StreamField, which is required for Wagtail 6.x. This stores StreamField data as native PostgreSQL JSON rather than the old text-based format.

### Smart Typography
The custom `RichTextBlock` in `blog/models.py` uses the `smartypants` library to automatically convert:
- Straight quotes ("") to curly quotes ("")
- Dashes (--) to em-dashes (—)
- Apostrophes (') to proper curly apostrophes (')

This is applied during rendering, not storage.

## Deployment

### Environment Variables (Production)
Required:
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `ALLOWED_HOSTS` - Comma-separated allowed hosts
- `AWS_STORAGE_BUCKET_NAME` - S3 bucket name
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

Optional:
- `SENTRY_DSN` - Sentry error tracking DSN
- `AWS_S3_CUSTOM_DOMAIN` - Custom CloudFront/CDN domain
- `MEDIA_URL` - Custom media URL

### Fly.io Deployment
```bash
# Deploy to Fly.io
fly deploy

# View logs
fly logs

# SSH into container
fly ssh console
```

### Docker Build
The Dockerfile:
1. Installs Python 3.12 dependencies
2. Downloads and runs Tailwind CLI to build CSS
3. Collects static files
4. Runs via `run.sh` with gunicorn

## Common Tasks

### Adding a New Blog Post
1. Go to `/admin/`
2. Navigate to Pages
3. Click on the homepage
4. Click "Add Child Page"
5. Choose "Blog Page"
6. Fill in title, date, and body content using StreamField blocks
7. Save and publish

### Updating Styles
1. Edit `tomd/static/css/input.css` for custom CSS
2. Rebuild Tailwind: `./tailwindcss -i ./tomd/static/css/input.css -o ./tomd/static/css/tailwind.css`
3. Refresh browser (collectstatic not needed for local dev with DEBUG=True)

### Working with Tailwind Classes in Templates
Tailwind scans these paths (defined in `tailwind.config.js`):
- `./tomd/templates/**/*.html`
- `./home/templates/**/*.html`
- `./blog/templates/**/*.html`

When you add Tailwind classes to templates, rebuild the CSS to include those utilities.

## Testing

Refer to `TEST.md` for comprehensive local testing procedures including:
- Visual testing checklist
- Responsive design verification
- Browser console checks
- Admin functionality testing
- Database integrity checks

## Git Workflow

**Main branch:** `master`
**Current branch:** `monolith` (consolidation work)

When ready to deploy changes:
1. Test locally thoroughly
2. Commit changes with descriptive messages
3. Push to branch: `git push origin monolith`
4. Deploy and verify on staging/production
5. Merge to master: `git checkout master && git merge monolith`

## Additional Documentation

- `MIGRATION_PLAN.md` - Detailed plan for the headless-to-monolithic migration
- `TEST.md` - Comprehensive local testing procedures
- `README.md` - Basic project information and deployment keys
