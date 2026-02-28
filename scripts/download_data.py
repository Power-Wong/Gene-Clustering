#!/usr/bin/env python3
"""
Download and preprocess BrainSpan and GTEx gene expression data.

This script downloads the required datasets and processes them into CSV files
that can be easily loaded by the backend application.
"""

import os
import sys
import requests
import pandas as pd
import numpy as np
from pathlib import Path

# Data URLs (these are the actual download URLs from the sources)
BRAINSPAN_URL = "https://www.brainspan.org/api/v2/well_known_file_download/267666525"  # RNA-Seq Gencode v10 summarized to genes
# Note: GTEx data requires registration and cannot be directly downloaded
# We'll provide instructions for manual download instead

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def download_brainspan_data():
    """Download BrainSpan developmental transcriptome data."""
    print("Downloading BrainSpan data...")
    
    try:
        # Note: The actual BrainSpan download may require handling redirects
        # and might not work directly with requests due to authentication
        response = requests.get(BRAINSPAN_URL, stream=True, timeout=300)
        response.raise_for_status()
        
        # Save the raw file
        raw_path = DATA_DIR / "brainspan_raw.zip"
        with open(raw_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded BrainSpan data to {raw_path}")
        return raw_path
        
    except Exception as e:
        print(f"Error downloading BrainSpan data: {e}")
        print("Please manually download from: https://www.brainspan.org/static/download.html")
        print("Download 'RNA-Seq Gencode v10 summarized to genes' and save as brainspan_raw.zip")
        return None

def process_brainspan_data(raw_file_path):
    """Process BrainSpan data into a clean CSV format."""
    if not os.path.exists(raw_file_path):
        print(f"Raw file not found: {raw_file_path}")
        return False
    
    try:
        # Read the raw data (assuming it's a CSV or similar format)
        # The actual format may vary - this is a template
        df = pd.read_csv(raw_file_path, sep='\t', index_col=0)
        
        # Clean and preprocess the data
        # Remove any rows/columns with all NaN values
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        
        # Ensure gene symbols are in uppercase
        df.index = df.index.str.upper()
        
        # Save processed data
        output_path = DATA_DIR / "brainspan_gene_expression.csv"
        df.to_csv(output_path)
        print(f"Processed BrainSpan data saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing BrainSpan data: {e}")
        return False

def setup_gtex_instructions():
    """Provide instructions for GTEx data setup."""
    print("\n" + "="*60)
    print("GTEx Data Setup Instructions")
    print("="*60)
    print("1. Go to https://gtexportal.org/home/datasets")
    print("2. Register for GTEx Portal access (free registration required)")
    print("3. Download the 'Gene TPM' dataset")
    print("4. Extract the data and save it as:")
    print(f"   {DATA_DIR / 'gtex_gene_expression.csv'}")
    print("5. Ensure the CSV has gene symbols as row indices and tissue samples as columns")
    print("="*60)

def main():
    """Main function to download and process data."""
    print("Setting up gene expression data...")
    
    # Download and process BrainSpan data
    brainspan_raw = download_brainspan_data()
    if brainspan_raw:
        process_brainspan_data(brainspan_raw)
    else:
        print("Skipping BrainSpan processing due to download failure")
    
    # Provide GTEx setup instructions
    setup_gtex_instructions()
    
    print("\nData setup complete! You can now run the application.")

if __name__ == "__main__":
    main()