# Tamil Learning App - Deployment Guide

## Quick Deployment Options

### 1. **Netlify (Easiest for Static Hosting)**
Perfect for the frontend HTML/CSS/JS version

```bash
# Option A: Using Web Interface
# 1. Go to netlify.com
# 2. Drag and drop your project folder
# 3. Done! Get a live URL instantly

# Option B: Using Netlify CLI
npm install -g netlify-cli
cd kid-tamil-learn
netlify deploy
```

**Pros:**
- Free hosting
- Custom domain support
- HTTPS by default
- CDN distribution
- Form handling

**Cons:**
- Backend (backend.py) requires separate hosting

---

### 2. **Vercel (Best for Full-Stack)**
Great if using the Flask backend

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd kid-tamil-learn
vercel

# For production
vercel --prod
```

**Pros:**
- Serverless functions for backend
- Automatic deployments from Git
- Environment variables support
- Analytics included

**Cons:**
- Requires code to be in `/api` folder for serverless

---

### 3. **GitHub Pages (Free, No Account Needed)**

```bash
# Create GitHub repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/kid-tamil-learn.git
git push -u origin main

# Enable GitHub Pages in repo settings
# Your site is now at: https://YOUR_USERNAME.github.io/kid-tamil-learn/
```

**Pros:**
- Completely free
- GitHub integration
- No upfront setup
- Version control

**Cons:**
- No backend support (static only)

---

### 4. **Heroku (For Backend + Frontend)**

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create tamil-learning-app

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

**Pros:**
- Full Flask backend support
- Easy database integration
- Environment variables
- Automatic SSL

**Cons:**
- Paid after free tier (~$7/month)
- Dyno sleep after 30 mins inactivity (free tier)

---

### 5. **AWS Amplify (Powerful Hosting)**

```bash
npm install -g @aws-amplify/cli

amplify init
amplify hosting add
amplify publish
```

**Pros:**
- Highly scalable
- Lambda for serverless backend
- DynamoDB for database
- Free tier available

**Cons:**
- Steeper learning curve
- More complex configuration

---

### 6. **Local Docker (Self-Hosted)**

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "backend.py"]
```

Build and run:
```bash
docker build -t tamil-learning .
docker run -p 5000:5000 tamil-learning
```

**Pros:**
- Full control
- Works anywhere
- Easy to containerize
- Environment consistency

**Cons:**
- Requires server/VPS ($5-20/month)
- Need to manage yourself

---

### 7. **Google Cloud (Free Trial $300)**

```bash
gcloud init
gcloud app deploy

# View your app
gcloud app browse
```

**Pros:**
- Google infrastructure
- Generous free tier
- Auto-scaling
- Global CDN

**Cons:**
- Complex setup
- Requires Google account

---

## Recommended Setup by Use Case

### For **Kid's Home Learning**
- Use **index.html** locally
- Open `file:///path/to/index.html` in browser
- Works offline, no server needed

### For **Classroom (Multiple Kids)**
1. Deploy frontend to **Netlify** (free)
2. Kids open shared link
3. Learn independently with local storage

### For **School with Progress Tracking**
1. Deploy frontend to **Netlify**
2. Deploy backend to **Heroku** or **Railway**
3. Kids login, data saved to database
4. Teachers see progress dashboard

### For **Production App**
1. Use **AWS Amplify** or **Google Cloud**
2. Add authentication (Auth0, Firebase)
3. Database (DynamoDB, Firestore)
4. CDN for images/audio
5. Analytics (Google Analytics, Mixpanel)

---

## Step-by-Step: Deploy to Netlify (Easiest)

### Method 1: Web Drag & Drop
1. Go to [netlify.com](https://netlify.com)
2. Drag your `kid-tamil-learn` folder into the browser
3. Wait for deployment
4. Get a URL like: `https://xxxxx-tamil-learning.netlify.app`

### Method 2: GitHub + Netlify (Better)
1. Push code to GitHub
   ```bash
   git push origin main
   ```
2. Go to [netlify.com](https://netlify.com)
3. Click "New site from Git"
4. Connect GitHub account
5. Select `kid-tamil-learn` repo
6. Netlify automatically deploys on every push

---

## Step-by-Step: Run Backend Locally

### Prerequisites
```bash
# Install Python 3.8+
python --version

# Install Ollama for LLM
# Download from: https://ollama.ai
# Start it: ollama serve
```

### Setup
```bash
cd kid-tamil-learn

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run
```bash
# Make sure Ollama is running
ollama serve  # in another terminal

# Run Flask app
python backend.py

# Visit: http://localhost:5000
```

---

## Environment Variables

Create `.env` file for sensitive data:

```env
FLASK_ENV=production
OLLAMA_MODEL=llama2
OLLAMA_API=http://localhost:11434/api/generate
DATABASE_URL=postgresql://user:pass@localhost/tamil_db
SECRET_KEY=your_secret_key_here
CORS_ALLOWED_ORIGINS=https://tamil-learning.netlify.app
```

---

## Domain & Custom URL

### Connect Custom Domain
1. **On Netlify:**
   - Settings → Domain management
   - Add custom domain
   - Update DNS at registrar (GoDaddy, Namecheap, etc.)

2. **Example (registrar):**
   - Create CNAME record
   - Name: `www`
   - Value: `your-site-name.netlify.app`

---

## Monitoring & Logs

### Netlify
- View logs: Dashboard → Site settings → Build & deploy

### Heroku
```bash
heroku logs --tail
heroku apps:info
```

### Local
- Check console for errors
- Monitor API requests in browser DevTools

---

## Performance Optimization

### Frontend
```bash
# Minify HTML/CSS/JS
npm install -g minify
minify index.html > index.min.html

# Compress images (if you add any)
imagemin *.png --out-dir=. --plugin=pngquant
```

### Backend
```python
# Add caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Use compression
from flask_compress import Compress
Compress(app)
```

### CDN (Optional)
Use Cloudflare for free CDN:
1. Change DNS to Cloudflare
2. Automatic CDN caching
3. Free SSL included

---

## Troubleshooting

### **Issue: Netlify shows "Page Not Found"**
- Ensure `index.html` is in root directory
- Check publish directory setting (should be `.`)

### **Issue: Flask API returns 500 Error**
- Check Ollama is running: `ollama serve`
- View logs: `heroku logs --tail` (if on Heroku)
- Test locally first: `python backend.py`

### **Issue: Slow load times**
- Enable gzip compression
- Use CDN (Netlify CDN auto-enabled)
- Optimize images if added
- Cache API responses

### **Issue: CORS errors**
- Check backend has `flask_cors` installed
- Verify frontend URL is in allowed origins
- Test with curl: `curl -H "Origin: ..." http://localhost:5000`

---

## Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| **Netlify** | Free | Static hosting, 100GB/month |
| **Heroku** | $7/month | Dyno hours, Postgres DB |
| **Railway** | $5/month | Simple backend hosting |
| **Vercel** | Free | Next.js optimized |
| **GitHub Pages** | Free | Static only |
| **AWS Free Tier** | Free 1 year | Then ~$10-20/month |
| **Firebase** | Free+ | Generous free tier |

---

## Security Checklist

- [ ] No API keys in frontend code
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS (auto on Netlify/Heroku)
- [ ] Restrict CORS to your domain
- [ ] Validate all user inputs
- [ ] Rate limit API endpoints
- [ ] Use HTTPS for all external APIs
- [ ] Regular backups of data

---

## Next Steps

1. **Choose hosting** based on your needs
2. **Follow deployment steps** above
3. **Test thoroughly** before sharing
4. **Monitor** for errors and performance
5. **Iterate** based on user feedback

---

## Support URLs

- **Netlify Docs**: https://docs.netlify.com/
- **Heroku Docs**: https://devcenter.heroku.com/
- **Vercel Docs**: https://vercel.com/docs
- **GitHub Pages**: https://pages.github.com/
- **AWS Amplify**: https://docs.amplify.aws/

---

Happy deploying! 🚀

