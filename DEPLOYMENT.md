# Deployment Instructions

## Local Setup

1. **Clone the repository locally:**
   ```bash
   git clone https://github.com/Power-Wong/Gene-Clustering.git
   cd Gene-Clustering
   ```

2. **Install dependencies:**
   ```bash
   # Backend
   pip install -r backend/requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Set up data files:**
   - Run the data download script: `python scripts/download_data.py`
   - Follow the instructions to manually download GTEx data if needed
   - Place processed CSV files in the `data/` directory

4. **Run locally:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## GitHub Setup

To push this code to your GitHub repository:

```bash
# Navigate to the project directory
cd /path/to/gene-expression-heatmap

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Gene expression heatmap clustering web application"

# Add your GitHub remote
git remote add origin git@github.com:Power-Wong/Gene-Clustering.git

# Push to GitHub
git push -u origin main
```

**Note:** You may need to:
- Set up SSH keys for GitHub authentication
- Use HTTPS with a personal access token if SSH doesn't work
- Create the repository on GitHub first if it doesn't exist

## Vercel Deployment (Recommended)

1. **Create a Vercel account** at [vercel.com](https://vercel.com)

2. **Import your GitHub repository:**
   - Go to Vercel Dashboard
   - Click "New Project"
   - Import your `Gene-Clustering` repository

3. **Configure environment variables** (if needed):
   - None required for basic functionality

4. **Deploy!** Vercel will automatically:
   - Build the frontend (React)
   - Deploy the backend as serverless functions
   - Provide a custom domain

5. **Custom domain** (optional):
   - Add your custom domain in Vercel settings
   - Update DNS records as instructed

## Render Deployment (Alternative)

1. **Create a Render account** at [render.com](https://render.com)

2. **Create a new Web Service:**
   - Connect your GitHub repository
   - Select the `render.yaml` configuration file
   - Set environment variables if needed

3. **Deploy!** Render will:
   - Build both frontend and backend
   - Deploy as a single web service
   - Provide automatic SSL and custom domains

## Data Considerations

### BrainSpan Data
- The application expects `data/brainspan_gene_expression.csv`
- Download from: https://www.brainspan.org/static/download.html
- File: "RNA-Seq Gencode v10 summarized to genes"

### GTEx Data
- The application expects `data/gtex_gene_expression.csv`
- Requires registration at: https://gtexportal.org/
- Download "Gene TPM" dataset
- Process into gene-symbol-indexed CSV format

### Large File Handling
- Data files are excluded from Git (`.gitignore`)
- For deployment, you'll need to:
  - Upload data files separately to your server, OR
  - Modify the backend to download data on-demand, OR
  - Use cloud storage (AWS S3, Google Cloud Storage) and update the data paths

## Environment Variables

The application supports these environment variables:

- `PORT` - Port for the backend server (default: 5000)
- `PYTHON_VERSION` - Python version for deployment (set in vercel.json or render.yaml)

## Scaling Considerations

For production use with many users:

1. **Caching**: Implement Redis or similar caching for frequently requested gene sets
2. **Database**: Consider using a proper database instead of CSV files for large datasets
3. **Asynchronous Processing**: For large gene lists, implement background job processing
4. **CDN**: Serve static assets through a CDN for better performance

## Troubleshooting

### Common Issues

**"Module not found" errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt` and `npm install`

**Data loading errors:**
- Verify CSV files are in the correct format (genes as row indices, samples as columns)
- Check file permissions

**Deployment failures:**
- Check build logs in Vercel/Render dashboard
- Ensure Python and Node.js versions match requirements

### Performance Optimization

- Pre-compute clustering for common gene sets
- Implement lazy loading for large heatmaps
- Use Web Workers for client-side clustering (alternative approach)

## License

This project is licensed under the MIT License - see the LICENSE file for details.