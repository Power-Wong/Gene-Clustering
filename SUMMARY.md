# Gene Expression Heatmap Clustering Project Summary

## Project Overview

This project creates a web application that allows users to:
1. Input a list of gene symbols
2. Automatically retrieve and process expression data from BrainSpan (developmental time) and GTEx (tissue types)
3. Perform hierarchical clustering on genes with similar expression patterns
4. Visualize results as interactive heatmaps

## Technical Architecture

### Frontend
- **Framework**: React.js
- **Visualization**: Plotly.js for interactive heatmaps
- **Styling**: Bootstrap for responsive design
- **HTTP Client**: Axios for API communication

### Backend
- **Framework**: Flask (Python)
- **Data Processing**: Pandas, NumPy, SciPy
- **Clustering**: Hierarchical clustering with SciPy
- **Deployment**: Compatible with Vercel (serverless) and Render (traditional)

### Data Sources
- **BrainSpan**: Developmental transcriptome across prenatal/postnatal stages
- **GTEx**: Tissue-specific gene expression across 53+ human tissues

## Key Features

### User Interface
- Simple text input for gene lists (supports various delimiters)
- Real-time processing feedback
- Interactive heatmaps with zoom and hover information
- Error handling for invalid gene symbols

### Data Processing
- Gene symbol validation against available datasets
- Automatic data normalization (z-score transformation)
- Hierarchical clustering of both genes and samples
- Handling of missing data and edge cases

### Deployment Flexibility
- **Vercel**: Full-stack deployment with serverless functions
- **Render**: Traditional web service deployment
- **Local Development**: Easy setup with Docker or direct installation

## Implementation Details

### Clustering Algorithm
- Uses average linkage hierarchical clustering
- Euclidean distance metric
- Z-score normalization across samples for each gene
- Separate clustering for rows (genes) and columns (samples)

### Data Structure
- Input: List of gene symbols
- Output: JSON with clustered heatmap data including:
  - Normalized expression values
  - Gene and sample ordering after clustering
  - Dendrogram information (for future enhancement)

### Error Handling
- Validates input gene symbols
- Handles missing data gracefully
- Provides informative error messages
- Robust backend error logging

## Deployment Instructions

### GitHub Setup
1. Create repository at `https://github.com/Power-Wong/Gene-Clustering`
2. Push code using the provided instructions
3. Set up deployment platform (Vercel recommended)

### Data Preparation
1. Download BrainSpan data from official source
2. Register and download GTEx data (requires approval)
3. Process data into CSV format as specified
4. Upload data files to deployment environment

### Platform Configuration
- **Vercel**: Uses `vercel.json` for build configuration
- **Render**: Uses `render.yaml` for service definition
- Both platforms support free tiers for initial deployment

## Future Enhancements

### Immediate Improvements
- Add loading states and progress indicators
- Implement client-side clustering as fallback
- Add export functionality (PNG, CSV)
- Improve mobile responsiveness

### Advanced Features
- Support for additional data sources (TCGA, GEO)
- Gene set enrichment analysis integration
- Custom clustering parameters (distance metrics, linkage methods)
- Session persistence and sharing capabilities

### Performance Optimizations
- Implement caching layer for frequently accessed genes
- Add pagination for large gene lists
- Optimize frontend rendering for large heatmaps
- Consider WebAssembly for computationally intensive operations

## Limitations and Considerations

### Data Access
- GTEx data requires registration and approval
- BrainSpan data may have usage restrictions
- Large datasets require significant storage and memory

### Computational Requirements
- Clustering complexity: O(n²) for n genes
- Memory usage scales with dataset size
- Free deployment tiers may have resource limitations

### Browser Compatibility
- Modern browsers required for Plotly.js features
- Large heatmaps may impact performance on mobile devices
- Consider progressive loading for better UX

## Getting Started

1. **Clone the repository**
2. **Set up development environment** (follow DEPLOYMENT.md)
3. **Download and process data files**
4. **Run locally to test functionality**
5. **Deploy to preferred platform**
6. **Customize styling and features as needed**

## Support and Maintenance

- Monitor deployment logs for errors
- Keep dependencies updated for security
- Consider user feedback for feature prioritization
- Plan for data updates as new versions become available

This project provides a solid foundation for gene expression analysis and can be extended based on specific research needs and user requirements.