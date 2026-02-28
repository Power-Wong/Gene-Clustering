"""
Gene Expression Heatmap Backend API

This Flask application provides endpoints for processing gene lists,
retrieving expression data from BrainSpan and GTEx datasets,
performing clustering, and returning visualization-ready data.
"""

import os
import json
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
from sklearn.preprocessing import StandardScaler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Data file paths (these will be populated with actual data files)
BRAINSPAN_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'brainspan_gene_expression.csv')
GTEx_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'gtex_gene_expression.csv')

class GeneExpressionProcessor:
    """Handles gene expression data processing and clustering."""
    
    def __init__(self):
        self.brainspan_data = None
        self.gtex_data = None
        self._load_data()
    
    def _load_data(self):
        """Load BrainSpan and GTEx data from CSV files."""
        try:
            if os.path.exists(BRAINSPAN_DATA_PATH):
                self.brainspan_data = pd.read_csv(BRAINSPAN_DATA_PATH, index_col=0)
                logger.info(f"Loaded BrainSpan data: {self.brainspan_data.shape}")
            else:
                logger.warning("BrainSpan data file not found")
                self.brainspan_data = pd.DataFrame()
                
            if os.path.exists(GTEx_DATA_PATH):
                self.gtex_data = pd.read_csv(GTEx_DATA_PATH, index_col=0)
                logger.info(f"Loaded GTEx data: {self.gtex_data.shape}")
            else:
                logger.warning("GTEx data file not found")
                self.gtex_data = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.brainspan_data = pd.DataFrame()
            self.gtex_data = pd.DataFrame()
    
    def validate_genes(self, gene_list):
        """Validate gene symbols against available data."""
        valid_genes = []
        invalid_genes = []
        
        # Get all available genes from both datasets
        available_genes = set()
        if not self.brainspan_data.empty:
            available_genes.update(self.brainspan_data.index.tolist())
        if not self.gtex_data.empty:
            available_genes.update(self.gtex_data.index.tolist())
        
        for gene in gene_list:
            gene_upper = gene.strip().upper()
            if gene_upper in available_genes:
                valid_genes.append(gene_upper)
            else:
                invalid_genes.append(gene.strip())
        
        return valid_genes, invalid_genes
    
    def get_expression_data(self, gene_list):
        """Extract expression data for given genes."""
        brainspan_subset = pd.DataFrame()
        gtex_subset = pd.DataFrame()
        
        if not self.brainspan_data.empty:
            brainspan_subset = self.brainspan_data.loc[
                self.brainspan_data.index.isin(gene_list)
            ]
        
        if not self.gtex_data.empty:
            gtex_subset = self.gtex_data.loc[
                self.gtex_data.index.isin(gene_list)
            ]
        
        return brainspan_subset, gtex_subset
    
    def cluster_data(self, data_df):
        """Perform hierarchical clustering on expression data."""
        if data_df.empty or data_df.shape[0] < 2:
            return {
                'data': data_df.values.tolist() if not data_df.empty else [],
                'genes': data_df.index.tolist() if not data_df.empty else [],
                'samples': data_df.columns.tolist() if not data_df.empty else [],
                'row_dendrogram': None,
                'col_dendrogram': None
            }
        
        # Normalize data (z-score across samples for each gene)
        scaler = StandardScaler()
        normalized_data = scaler.fit_transform(data_df.T).T
        
        # Handle NaN values
        normalized_data = np.nan_to_num(normalized_data, nan=0.0)
        
        # Row clustering (genes)
        if normalized_data.shape[0] > 1:
            row_linkage = linkage(normalized_data, method='average', metric='euclidean')
            row_dendro = dendrogram(row_linkage, no_plot=True)
            row_order = row_dendro['leaves']
        else:
            row_linkage = None
            row_order = list(range(normalized_data.shape[0]))
        
        # Column clustering (samples)
        if normalized_data.shape[1] > 1:
            col_linkage = linkage(normalized_data.T, method='average', metric='euclidean')
            col_dendro = dendrogram(col_linkage, no_plot=True)
            col_order = col_dendro['leaves']
        else:
            col_linkage = None
            col_order = list(range(normalized_data.shape[1]))
        
        # Reorder data according to clustering
        clustered_data = normalized_data[np.ix_(row_order, col_order)]
        
        # Prepare dendrogram data for frontend
        row_dendrogram_data = self._prepare_dendrogram_data(row_linkage, data_df.index.tolist(), row_order) if row_linkage is not None else None
        col_dendrogram_data = self._prepare_dendrogram_data(col_linkage, data_df.columns.tolist(), col_order) if col_linkage is not None else None
        
        return {
            'data': clustered_data.tolist(),
            'genes': [data_df.index[i] for i in row_order],
            'samples': [data_df.columns[i] for i in col_order],
            'row_dendrogram': row_dendrogram_data,
            'col_dendrogram': col_dendrogram_data
        }
    
    def _prepare_dendrogram_data(self, linkage_matrix, labels, order):
        """Prepare dendrogram data for Plotly visualization."""
        if linkage_matrix is None:
            return None
        
        # This is a simplified version - in practice, you might want to use
        # scipy's dendrogram function to get the full structure
        return {
            'linkage': linkage_matrix.tolist(),
            'labels': labels,
            'order': order
        }

# Initialize processor
processor = GeneExpressionProcessor()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'brainspan_data_loaded': not processor.brainspan_data.empty,
        'gtex_data_loaded': not processor.gtex_data.empty
    })

@app.route('/api/process-genes', methods=['POST'])
def process_genes():
    """Process gene list and return clustered expression data."""
    try:
        data = request.get_json()
        if not data or 'genes' not in data:
            return jsonify({'error': 'Missing genes in request'}), 400
        
        gene_list = data['genes']
        if not isinstance(gene_list, list):
            return jsonify({'error': 'genes must be a list'}), 400
        
        if len(gene_list) == 0:
            return jsonify({'error': 'genes list cannot be empty'}), 400
        
        # Validate genes
        valid_genes, invalid_genes = processor.validate_genes(gene_list)
        
        if len(valid_genes) == 0:
            return jsonify({
                'error': 'No valid genes found in our datasets',
                'invalid_genes': invalid_genes
            }), 400
        
        # Get expression data
        brainspan_data, gtex_data = processor.get_expression_data(valid_genes)
        
        # Cluster data
        brainspan_clustered = processor.cluster_data(brainspan_data)
        gtex_clustered = processor.cluster_data(gtex_data)
        
        return jsonify({
            'success': True,
            'valid_genes': valid_genes,
            'invalid_genes': invalid_genes,
            'brainspan': brainspan_clustered,
            'gtex': gtex_clustered
        })
        
    except Exception as e:
        logger.error(f"Error processing genes: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))