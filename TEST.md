# Local Testing Plan - Monolithic Wagtail Migration

This document outlines the testing steps to verify the consolidation from headless architecture to monolithic Wagtail site.

## Prerequisites

- Python 3.12 installed
- Git on `monolith` branch
- Access to existing database (or test with SQLite locally)

---

## Phase 1: Environment Setup

### 1.1 Create Virtual Environment
```bash
cd /Users/tom/Documents/code/python/wagtail-tomd-redux/tomd
python3.12 -m venv venv
source venv/bin/activate
```

### 1.2 Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected result:** All packages install without errors. Pay attention to Django 5.1.4 and Wagtail 6.3.1 versions.

**Troubleshooting:**
- If Python 3.12 not found: `brew install python@3.12` (macOS) or install from python.org
- If pip issues: `python -m pip install --upgrade pip`

---

## Phase 2: Database Migration

### 2.1 Run Migrations
```bash
python manage.py migrate
```

**Expected result:** All migrations apply successfully. Key migrations to watch for:
- Django 4.0 → 5.1 migrations
- Wagtail 3.0 → 6.3 migrations
- StreamField changes (use_json_field=True)

**Troubleshooting:**
- If migration errors: Check for custom migrations that need updating
- If SQLite version errors: Upgrade SQLite or use PostgreSQL

### 2.2 Create Superuser (if needed for fresh database)
```bash
python manage.py createsuperuser
```

---

## Phase 3: Build Static Assets

### 3.1 Download Tailwind CLI (macOS version)
```bash
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss
```

**Note:** If you're on Intel Mac, use `tailwindcss-macos-x64` instead.

### 3.2 Build Tailwind CSS
```bash
./tailwindcss -i ./tomd/static/css/input.css -o ./tomd/static/css/tailwind.css --minify
```

**Expected result:** `tailwind.css` file created in `tomd/static/css/`

**Verify:** Check file size - should be around 10-20KB (minified)

### 3.3 Collect Static Files
```bash
python manage.py collectstatic --noinput
```

**Expected result:** Files copied to `static/` directory including:
- Tailwind CSS
- Fonts (source-serif-pro woff/woff2 files)
- favicon.ico
- tomd.js

---

## Phase 4: Start Development Server

### 4.1 Run Server
```bash
python manage.py runserver
```

**Expected result:** Server starts on http://127.0.0.1:8000/

**Check console for:**
- No import errors
- No template errors
- Server starts successfully

---

## Phase 5: Visual & Functional Testing

### 5.1 Homepage Testing
**URL:** http://127.0.0.1:8000/

**Visual Checks:**
- [ ] Header displays with "tomd.org ~ about" navigation
- [ ] Navigation uses Avenir font (sans-serif)
- [ ] Blog post titles display in large text (text-5xl)
- [ ] Blog post dates display in red below titles
- [ ] Dates are formatted as "Month Day, Year" (e.g., "December 11, 2025")
- [ ] Links have no underline
- [ ] Page has proper padding (more on desktop, less on mobile)

**Responsive Design:**
- [ ] Desktop (>640px): Content has `px-16` padding
- [ ] Mobile (<640px): Content has `px-6` padding
- [ ] Resize browser to test breakpoints

**Compare with:** Nuxt frontend at current tomd.org site

---

### 5.2 Blog Post Page Testing
**URL:** http://127.0.0.1:8000/[any-blog-post-slug]/

**Visual Checks:**
- [ ] Post title displays in large Avenir font
- [ ] Date displays below title, formatted as "Month Day, Year"
- [ ] Body content uses Source Serif Pro font (serif)
- [ ] Headings (h2) display in proper size
- [ ] Paragraphs have proper spacing
- [ ] Links in content have teal background (bg-teal-100)
- [ ] Images display with rounded corners
- [ ] Images are properly sized (not too large)
- [ ] Embeds (videos/media) display correctly

**Content Testing:**
- [ ] Rich text formatting works (bold, italic, links)
- [ ] Internal links work
- [ ] External links work
- [ ] Smart quotes display correctly (not ASCII quotes)

**Responsive Design:**
- [ ] Content max-width is 896px (max-w-5xl)
- [ ] Images scale properly on mobile
- [ ] Text is readable on all screen sizes

---

### 5.3 About Page Testing
**URL:** http://127.0.0.1:8000/about/

**Checks:**
- [ ] About page loads successfully
- [ ] Uses same styling as other blog pages
- [ ] Navigation link works from header

**Note:** The about page is a regular BlogPage with slug "about"

---

### 5.4 Wagtail Admin Testing
**URL:** http://127.0.0.1:8000/admin/

**Login:**
- Username: [your-username]
- Password: [your-password]

**Admin Checks:**
- [ ] Admin login works
- [ ] Dashboard loads without errors
- [ ] Can view pages list
- [ ] Can edit a blog page
- [ ] StreamField editor works:
  - [ ] Can add heading blocks
  - [ ] Can add paragraph blocks
  - [ ] Can add image blocks
  - [ ] Can add embed blocks
- [ ] Can save changes
- [ ] Preview works in admin
- [ ] No JavaScript console errors

---

### 5.5 JavaScript Functionality Testing

**Date Formatting:**
- [ ] Open browser console (F12 or Cmd+Option+I)
- [ ] Check for JavaScript errors
- [ ] Verify dates are formatted (should change from YYYY-MM-DD to "Month Day, Year")

**Umami Analytics:**
- [ ] Check Network tab for request to `umami.co.tomd.org`
- [ ] Verify analytics script loads

**Stripe Link Tracking (if applicable):**
- [ ] If any blog posts contain Stripe checkout links (book.stripe.com)
- [ ] Click should trigger Umami tracking event
- [ ] Check console: `window.umami` should exist

---

### 5.6 Browser Console Check

**Open Developer Tools:**
- Chrome/Edge: Cmd+Option+I (Mac) or F12 (Windows)
- Firefox: Cmd+Shift+I (Mac) or F12 (Windows)
- Safari: Cmd+Option+I (need to enable Developer menu first)

**Console Tab:**
- [ ] No red errors
- [ ] No yellow warnings (minor warnings OK)
- [ ] Date formatting function executes

**Network Tab:**
- [ ] All static assets load (200 status)
- [ ] tailwind.css loads successfully
- [ ] Fonts load successfully (woff2 files)
- [ ] favicon loads
- [ ] tomd.js loads
- [ ] Umami script loads

**Elements/Inspector Tab:**
- [ ] Inspect an element - Tailwind classes are applied
- [ ] Check computed styles - fonts render correctly
- [ ] Verify responsive styles change at 640px breakpoint

---

### 5.7 Font Rendering Check

**Visual Verification:**
- [ ] Headings use Avenir/sans-serif font family
- [ ] Body text uses Source Serif Pro/serif font family
- [ ] Fonts look crisp and load correctly
- [ ] No FOUT (Flash of Unstyled Text)

**Console Check:**
```javascript
// Paste in browser console
document.fonts.check('1em "Source Serif Pro"')
```
Should return `true` when font is loaded.

---

### 5.8 Performance Check

**Lighthouse Audit (Optional but Recommended):**
1. Open Chrome DevTools
2. Go to "Lighthouse" tab
3. Run audit for:
   - Performance
   - Accessibility
   - Best Practices
   - SEO

**Expected Scores:**
- Performance: >80
- Accessibility: >90
- Best Practices: >90
- SEO: >90

---

## Phase 6: Comparison with Nuxt Frontend

### 6.1 Side-by-Side Visual Comparison

**Open both:**
- Current production site (Nuxt frontend)
- Local Django site (http://127.0.0.1:8000/)

**Compare:**
- [ ] Typography matches (sizes, weights, colors)
- [ ] Spacing matches (padding, margins)
- [ ] Colors match (especially date red, link teal background)
- [ ] Responsive behavior matches
- [ ] Overall layout identical

**Take screenshots if needed for reference**

---

## Phase 7: Edge Case Testing

### 7.1 Long Content
- [ ] Find a blog post with lots of content
- [ ] Verify scrolling works
- [ ] Verify max-width constraint works (content doesn't get too wide)

### 7.2 Images
- [ ] Test blog post with multiple images
- [ ] Verify portrait and landscape images both work
- [ ] Verify images have correct sizing

### 7.3 Embeds
- [ ] Test blog post with video/media embeds
- [ ] Verify embeds display and play correctly

### 7.4 Empty States
- [ ] What happens if no blog posts? (Homepage should show empty)
- [ ] What happens with page that has no body content?

---

## Phase 8: Database Integrity Check

### 8.1 Verify Data Migration
```bash
python manage.py shell
```

```python
from blog.models import BlogPage
from home.models import HomePage

# Check blog pages
blog_count = BlogPage.objects.count()
print(f"Blog pages: {blog_count}")

# Check a sample blog page
sample = BlogPage.objects.first()
print(f"Sample post: {sample.title}")
print(f"Date: {sample.date}")
print(f"Body blocks: {len(sample.body)}")

# Check homepage
home = HomePage.objects.first()
print(f"Homepage: {home.title}")
```

**Expected result:** All data intact, no errors accessing fields

---

## Phase 9: Known Issues & Troubleshooting

### Issue: "No module named wagtail.core"
**Solution:** Old import somewhere. Search for:
```bash
grep -r "wagtail.core" .
```
Should only find in venv, not in your code.

### Issue: "StreamField has no attribute 'stream_block'"
**Solution:** Wagtail 6 requires `use_json_field=True` - check blog/models.py line 33.

### Issue: Tailwind classes not working
**Solution:**
1. Check `tomd/static/css/tailwind.css` exists
2. Rebuild: `./tailwindcss -i ./tomd/static/css/input.css -o ./tomd/static/css/tailwind.css`
3. Check browser Network tab - CSS file loading?

### Issue: Fonts not loading
**Solution:**
1. Check files exist in `tomd/static/fonts/`
2. Run `python manage.py collectstatic` again
3. Check browser Network tab for 404s

### Issue: Dates not formatting
**Solution:**
1. Check browser console for JavaScript errors
2. Verify tomd.js is loading (Network tab)
3. Check elements have `date-format` class and `data-date` attribute

---

## Phase 10: Testing Checklist Summary

### Critical Tests (Must Pass)
- [ ] Server starts without errors
- [ ] Homepage displays blog posts
- [ ] Blog post page displays correctly
- [ ] Admin login works
- [ ] Can edit and save pages in admin
- [ ] Tailwind CSS loads
- [ ] Fonts load correctly
- [ ] JavaScript has no console errors
- [ ] Dates format correctly

### Important Tests (Should Pass)
- [ ] Responsive design works
- [ ] All links work
- [ ] Images display properly
- [ ] Embeds work
- [ ] Umami analytics loads
- [ ] Visual match with Nuxt frontend

### Nice to Have (Optional)
- [ ] Lighthouse scores good
- [ ] Performance acceptable
- [ ] No browser console warnings

---

## Ready for Deployment?

If all critical and important tests pass, you're ready to proceed with deployment!

### Next Steps:
1. Test Docker build: `docker build -t tomd-test .`
2. Test Docker run: `docker run -p 8000:8000 tomd-test`
3. Push to Git: `git push origin monolith`
4. Deploy to Fly.io: `fly deploy`
5. Monitor deployment
6. Test production site
7. Merge to main when satisfied

---

## Rollback Plan

If issues arise in testing:
1. Switch back to previous branch: `git checkout main`
2. Run old server
3. Review errors and fix
4. Return to `monolith` branch and retest

---

## Notes & Observations

Use this section to note any issues or observations during testing:

-
-
-

---

**Date Created:** 2025-12-11
**Created By:** Claude Code Migration Assistant
