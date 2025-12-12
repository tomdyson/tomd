# Consolidation Plan: Headless → Monolithic Wagtail Site

## Overview
Consolidate the headless Wagtail + Nuxt.js architecture into a single monolithic Wagtail site with server-rendered Django templates, while migrating from Tachyons to Tailwind CSS and upgrading to modern Django/Wagtail versions.

## Current State
- **Backend**: Django 4.0.7 + Wagtail 3.0.2 (outdated, no security support)
- **Frontend**: Nuxt 2 with Tailwind CSS 3.2.0
- **Styling**: Backend uses Tachyons CSS, frontend uses Tailwind CSS
- **Architecture**: Headless with REST API, CORS, preview functionality
- **Content**: HomePage (blog listing) + BlogPage (with StreamField)
- **Deployment**: Fly.io (backend), separate Nuxt frontend

## Target State
- **Single app**: Django 5.1 + Wagtail 6.3 + Python 3.12
- **Styling**: Tailwind CSS throughout (matching current Nuxt design)
- **Architecture**: Traditional server-rendered templates (no API)
- **Deployment**: Single Fly.io deployment

## Key Decisions
✅ Remove API completely (django-cors-headers, djangorestframework, wagtail-headless-preview)
✅ About page already exists as BlogPage with slug 'about' - will work with updated templates
✅ Direct cutover deployment (no parallel staging)

---

## Implementation Plan

### Phase 0: Setup

#### 0.1 Create git branch
```bash
cd tomd
git checkout -b monolith
```

### Phase 1: Dependency Upgrades & Cleanup

#### 1.1 Update requirements.txt
**File**: `tomd/requirements.txt`

**Remove these packages**:
```
django-cors-headers
djangorestframework
wagtail-headless-preview
wagtailnetlify
wagtail-bakery
```

**Update to latest versions**:
```
Django==5.1.4
wagtail==6.3.1
Python 3.12 (in Dockerfile)
Pillow==11.0.0
psycopg2-binary==2.9.10
whitenoise==6.8.2
django-storages==1.14.4
boto3==1.35.90
sentry-sdk==2.19.2
```

#### 1.2 Update settings
**File**: `tomd/tomd/settings/base.py`

**Remove from INSTALLED_APPS**:
- `"corsheaders"`
- `"rest_framework"`
- `"wagtail.api.v2"`
- `"wagtail_headless_preview"`
- `"wagtailnetlify"`

**Remove from MIDDLEWARE**:
- `"corsheaders.middleware.CorsMiddleware"`

**Fix Wagtail 3→6 namespace change**:
- Change `"wagtail.core"` → `"wagtail"`

**Remove settings**:
- `CORS_ORIGIN_ALLOW_ALL`
- `HEADLESS_PREVIEW_CLIENT_URLS`
- `NETLIFY_API_TOKEN`, `NETLIFY_BUILD_HOOK`, `NETLIFY_SITE_ID`

#### 1.3 Update URLs
**File**: `tomd/tomd/urls.py`

**Remove**:
- Import of `blog.api.api_router`
- Import of `wagtailnetlify.urls`
- API route: `re_path(r"^api/v2/", api_router.urls)`
- Netlify route: `re_path(r"^netlify/", include(netlify_urls))`

#### 1.4 Simplify models
**File**: `tomd/blog/models.py`

**Changes**:
- Remove `from wagtail_headless_preview.models import HeadlessPreviewMixin`
- Remove `HeadlessPreviewMixin` from `BlogPage` parent classes
- Remove `api_fields` attribute
- Remove custom `get_api_representation` methods from `ImageChooserBlock`, `EmbedBlock`, `RichTextBlock`
- Keep `smartypants` functionality for text formatting
- Fix imports: `wagtail.core` → `wagtail` throughout

**File**: `tomd/home/models.py`
- Fix imports: `wagtail.core` → `wagtail`

#### 1.5 Delete API files
**File to delete**: `tomd/blog/api.py`

---

### Phase 2: Tailwind CSS Integration

#### 2.1 Set up Tailwind standalone CLI
**Create file**: `tomd/tomd/static/css/input.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .avenir {
    font-family: "avenir next", avenir, -apple-system, BlinkMacSystemFont,
      "helvetica neue", helvetica, ubuntu, roboto, noto, "segoe ui", arial,
      sans-serif;
  }

  .athelas {
    font-family: "Source Serif Pro", athelas, georgia, serif;
  }

  .copy {
    @apply athelas leading-normal text-gray-800 max-w-2xl mt-5;
    font-size: 1.4rem;
  }

  .copy p {
    @apply mt-5;
  }

  .copy p a {
    @apply bg-teal-100;
  }

  .date {
    font-size: 1.4rem;
  }
}
```

**Create file**: `tomd/tailwind.config.js`

```javascript
module.exports = {
  content: [
    './tomd/templates/**/*.html',
    './home/templates/**/*.html',
    './blog/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Create file**: `tomd/build-tailwind.sh`

```bash
#!/bin/bash
# Download Tailwind CLI if not present
if [ ! -f ./tailwindcss ]; then
    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
    chmod +x tailwindcss-linux-x64
    mv tailwindcss-linux-x64 tailwindcss
fi

# Build Tailwind CSS
./tailwindcss -i ./tomd/static/css/input.css -o ./tomd/static/css/tailwind.css --minify
```

#### 2.2 Copy static assets from Nuxt
**Copy fonts**:
- From: `tomd-nuxt-fe/assets/fonts/source-serif-pro-*.woff2` and `*.woff`
- To: `tomd/tomd/static/fonts/`

**Copy favicon**:
- From: `tomd-nuxt-fe/static/favicon.ico`
- To: `tomd/tomd/static/favicon.ico`

**Delete old files**:
- `tomd/tomd/static/css/tachyons.min.css`
- Update `tomd/tomd/static/css/tomd.css` (will be replaced by Tailwind)

---

### Phase 3: Template Migration

#### 3.1 Update base template
**File**: `tomd/tomd/templates/base.html`

**Changes**:
1. Replace Tachyons CSS with Tailwind CSS
2. Remove Google Fonts link, add self-hosted Source Serif Pro
3. Add Umami analytics script
4. Update header HTML with Tailwind classes (matching Nuxt layout)
5. Add date formatting JavaScript
6. Add Stripe link tracking JavaScript
7. Update favicon link

**New header structure**:
```html
<header class="sm:px-16 px-6 pt-8 pb-6 border-b border-gray-200 border-opacity-75">
    <h4 class="text-xl avenir font-normal">
        <a href="/" class="no-underline">tomd.org</a>
        <span class="text-gray-600">~</span>
        <a href="/about/" class="no-underline text-gray-600">about</a>
    </h4>
</header>
```

**Add to head**:
```html
<!-- Tailwind CSS -->
<link rel="stylesheet" type="text/css" href="{% static 'css/tailwind.css' %}">

<!-- Self-hosted fonts -->
<style>
@font-face {
  font-family: "Source Serif Pro";
  font-style: normal;
  font-weight: 400;
  src: url("{% static 'fonts/source-serif-pro-v10-latin-regular.woff2' %}") format("woff2"),
       url("{% static 'fonts/source-serif-pro-v10-latin-regular.woff' %}") format("woff");
}
@font-face {
  font-family: "Source Serif Pro";
  font-style: italic;
  font-weight: 400;
  src: url("{% static 'fonts/source-serif-pro-v10-latin-italic.woff2' %}") format("woff2"),
       url("{% static 'fonts/source-serif-pro-v10-latin-italic.woff' %}") format("woff");
}
</style>

<!-- Umami Analytics -->
<script defer src="https://umami.co.tomd.org/script.js" data-website-id="b05b00e9-e212-4a7d-9ca1-9610308b22fa"></script>

<!-- Favicon -->
<link rel="icon" type="image/x-icon" href="{% static 'favicon.ico' %}">
```

#### 3.2 Update HomePage template
**File**: `tomd/home/templates/home/home_page.html`

**Replace Tachyons classes with Tailwind** (matching Nuxt index.vue):
```django
{% extends "base.html" %}
{% load wagtailcore_tags %}

{% block content %}
<div class="container sm:px-16 px-6 pt-8 max-w-5xl">
    {% for post in blogpages %}
    <div class="pb-4">
        <h2 class="text-5xl avenir font-bold leading-none text-gray-800 pb-6">
            <a href="{% pageurl post %}" class="no-underline">{{ post.title }}</a>
        </h2>
        <p class="date pt-0 pb-4 athelas font-light text-red-400 date-format" data-date="{{ post.specific.date|date:'Y-m-d' }}">
            {{ post.specific.date }}
        </p>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

#### 3.3 Update BlogPage template
**File**: `tomd/blog/templates/blog/blog_page.html`

**Replace Tachyons classes with Tailwind** (matching Nuxt _.vue):
```django
{% extends "base.html" %}
{% load wagtailcore_tags wagtailimages_tags %}

{% block content %}
<div class="container sm:px-16 px-6 pt-8 max-w-5xl">
    <h1 class="text-5xl avenir font-bold leading-none text-gray-800 pb-6">{{ page.title }}</h1>
    <p class="athelas text-xl py-4 text-gray-600 date-format" data-date="{{ page.date|date:'Y-m-d' }}">
        {{ page.date }}
    </p>

    <div class="copy">
        {% for block in page.body %}
            {% if block.block_type == 'heading' %}
                <h2 class="text-xl pb-4 leading-tight">{{ block.value }}</h2>
            {% elif block.block_type == 'paragraph' %}
                {{ block.value|richtext }}
            {% elif block.block_type == 'image' %}
                {% image block.value width-1600 class="my-2 rounded" %}
            {% elif block.block_type == 'embed' %}
                <div class="my-2">
                    {{ block.value }}
                </div>
            {% endif %}
        {% endfor %}
    </div>
</div>
{% endblock %}
```

#### 3.4 Create JavaScript utilities
**File**: `tomd/tomd/static/js/tomd.js`

```javascript
// Date formatting utility (from Nuxt frontend)
function datify(dateString) {
    if (dateString && dateString.length) {
        var d = new Date(Date.parse(dateString));
        var options = { year: "numeric", month: "long", day: "numeric" };
        return d.toLocaleDateString("en-us", options);
    }
    return dateString;
}

// Format dates on page load
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.date-format').forEach(function(el) {
        el.textContent = datify(el.dataset.date);
    });

    trackStripeLinks();

    // Watch for dynamically added content
    const observer = new MutationObserver(trackStripeLinks);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Track Stripe checkout links with Umami (from Nuxt frontend)
function trackStripeLinks() {
    const stripeLinks = document.querySelectorAll('a[href*="book.stripe.com"]');

    stripeLinks.forEach(link => {
        if (link.dataset.umamiTracked) return;

        link.addEventListener('click', () => {
            if (window.umami) {
                window.umami.track('Stripe Checkout Click');
            }
        });

        link.dataset.umamiTracked = 'true';
    });
}
```

---

### Phase 4: Deployment Updates

#### 4.1 Update Dockerfile
**File**: `tomd/Dockerfile`

**Changes**:
- Update Python 3.9.13 → Python 3.12
- Add Tailwind CSS build step

```dockerfile
FROM python:3.12

ENV PYTHONUNBUFFERED 1 \
    WEB_CONCURRENCY=3 \
    GUNICORN_CMD_ARGS="--max-requests 1200 " \
    DJANGO_SETTINGS_MODULE=tomd.settings.production

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
RUN pip install gunicorn

COPY . /code/
WORKDIR /code/

# Build Tailwind CSS
RUN chmod +x build-tailwind.sh && ./build-tailwind.sh

# Collect static files
RUN python manage.py collectstatic --noinput

CMD ["./run.sh"]
```

#### 4.2 No changes needed
**Files that remain the same**:
- `fly.toml` - deployment config is environment-agnostic
- `run.sh` - startup script remains the same
- Environment variables - SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS unchanged

---

### Phase 5: Testing & Deployment

#### 5.1 Local testing checklist
1. ✅ Install Python 3.12
2. ✅ Create virtualenv and install updated requirements
3. ✅ Run migrations: `python manage.py migrate`
4. ✅ Build Tailwind CSS: `./build-tailwind.sh`
5. ✅ Collect static files: `python manage.py collectstatic`
6. ✅ Run local server: `python manage.py runserver`
7. ✅ Test homepage - blog post listing displays correctly
8. ✅ Test blog post page - StreamField renders with proper styling
9. ✅ Test about page - navigates and displays correctly
10. ✅ Test responsive design - check mobile (< 640px) and desktop views
11. ✅ Test date formatting - dates appear as "Month Day, Year"
12. ✅ Test Wagtail admin - can edit and save pages
13. ✅ Test images - display at correct size with rounded corners
14. ✅ Test embeds - video/media embeds work
15. ✅ Verify JavaScript console has no errors

#### 5.2 Deployment steps
1. ✅ Commit all changes with descriptive message
2. ✅ Test Docker build locally: `docker build -t tomd-test .`
3. ✅ Run Docker container locally: `docker run -p 8000:8000 tomd-test`
4. ✅ Verify functionality in Docker environment
5. ✅ Push to git: `git push origin monolith`
6. ✅ Deploy to Fly.io: `fly deploy`
7. ✅ Monitor deployment logs
8. ✅ Test production site:
   - Homepage loads and displays posts
   - Blog posts render correctly
   - About page works
   - Analytics tracking active
   - No console errors
9. ✅ Monitor Sentry for errors
10. ✅ Merge to main branch

#### 5.3 Rollback plan (if issues arise)
1. Keep old deployment running until verification complete
2. If problems detected: `fly releases` → `fly releases rollback <release-id>`
3. DNS/CDN: No changes needed (same Fly.io app)

---

## Critical Files Summary

### Files to modify:
1. `tomd/requirements.txt` - Update dependencies, remove headless packages
2. `tomd/tomd/settings/base.py` - Remove API/CORS config, fix namespace
3. `tomd/tomd/urls.py` - Remove API routes
4. `tomd/blog/models.py` - Remove headless mixins, fix namespace
5. `tomd/home/models.py` - Fix namespace
6. `tomd/tomd/templates/base.html` - Migrate to Tailwind, add fonts/analytics
7. `tomd/home/templates/home/home_page.html` - Migrate to Tailwind
8. `tomd/blog/templates/blog/blog_page.html` - Migrate to Tailwind
9. `tomd/tomd/static/js/tomd.js` - Add date formatting & analytics
10. `tomd/Dockerfile` - Update Python 3.12, add Tailwind build

### Files to create:
1. `tomd/tomd/static/css/input.css` - Tailwind input file
2. `tomd/tailwind.config.js` - Tailwind configuration
3. `tomd/build-tailwind.sh` - Tailwind build script

### Files to delete:
1. `tomd/blog/api.py` - API endpoints no longer needed
2. `tomd/tomd/static/css/tachyons.min.css` - Replaced by Tailwind

### Assets to copy from Nuxt:
1. `tomd-nuxt-fe/assets/fonts/*.woff2` → `tomd/tomd/static/fonts/`
2. `tomd-nuxt-fe/assets/fonts/*.woff` → `tomd/tomd/static/fonts/`
3. `tomd-nuxt-fe/static/favicon.ico` → `tomd/tomd/static/favicon.ico`

---

## Risk Mitigation

### Low Risk ✅
- Template structure already exists - just updating classes
- About page already exists as BlogPage - will work automatically
- Deployment infrastructure unchanged (Fly.io)
- Content/database unchanged

### Medium Risk ⚠️
- Django/Wagtail major version jump (4.0→5.1, 3.0→6.3)
  - **Mitigation**: Test locally thoroughly, incremental upgrade possible if issues
- Namespace changes throughout codebase
  - **Mitigation**: Search/replace for `wagtail.core` → `wagtail`

### Estimated Time: 4-6 hours
- Phase 1 (Upgrades): 1-2 hours
- Phase 2 (Tailwind): 1 hour
- Phase 3 (Templates): 1-2 hours
- Phase 4 (Deployment): 30 minutes
- Phase 5 (Testing): 1 hour

---

## Success Criteria
✅ Site renders identically to current Nuxt frontend
✅ All blog posts display correctly with proper styling
✅ Responsive design works (mobile & desktop)
✅ Date formatting matches Nuxt format
✅ Analytics tracking functional
✅ Wagtail admin fully functional
✅ No API endpoints or headless dependencies
✅ Django 5.1 + Wagtail 6.3 + Python 3.12 running
✅ Single Fly.io deployment serving entire site
