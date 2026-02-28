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
import zipfile
import io

# Updated Data URLs
BRAINSPAN_URL = "https://www.brainspan.org/api/v2/well_known_file_download/267666525"  # RNA-Seq Gencode v10 summarized to genes
GTEx_URL = "https://storage.googleapis.com/gtex_analysis_v8/rna_seq_data/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_tpm.gct.gz"

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def download_file(url, filename):
    """Download a file from URL with progress tracking."""
    print(f"Downloading {filename}...")
    
    try:
        response = requests.get(url, stream=True, timeout=600)
        response.raise_for_status()
        
        filepath = DATA_DIR / filename
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Downloaded to {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return None

def download_brainspan_data():
    """Download BrainSpan developmental transcriptome data."""
    return download_file(BRAINSPAN_URL, "brainspan_raw.zip")

def download_gtex_data():
    """Download GTEx bulk tissue expression data."""
    return download_file(GTEx_URL, "gtex_gene_tpm.gct.gz")

def process_brainspan_data(raw_file_path):
    """Process BrainSpan data into a clean CSV format."""
    if not os.path.exists(raw_file_path):
        print(f"Raw file not found: {raw_file_path}")
        return False
    
    try:
        # Extract and read the data
        # Note: The actual format may need adjustment based on the downloaded file structure
        with zipfile.ZipFile(raw_file_path, 'r') as zip_ref:
            # Find the main data file
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if not csv_files:
                print("No CSV files found in BrainSpan archive")
                return False
            
            # Read the first CSV file
            with zip_ref.open(csv_files[0]) as csv_file:
                df = pd.read_csv(csv_file, index_col=0)
        
        # Clean and preprocess
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        df.index = df.index.str.upper()
        
        # Save processed data
        output_path = DATA_DIR / "brainspan_gene_expression.csv"
        df.to_csv(output_path)
        print(f"Processed BrainSpan data saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing BrainSpan data: {e}")
        return False

def process_gtex_data(raw_file_path):
    """Process GTEx GCT file into CSV format."""
    if not os.path.exists(raw_file_path):
        print(f"Raw file not found: {raw_file_path}")
        return False
    
    try:
        # Read GCT file (GCT format has header lines)
        df = pd.read_csv(raw_file_path, sep='\t', skiprows=2, index_col=0)
        
        # Remove description column if present
        if 'Description' in df.columns:
            df = df.drop('Description', axis=1)
        
        # Clean gene names (remove version numbers like ENSG00000000003.14 -> ENSG00000000003)
        df.index = df.index.str.split('.').str[0]
        
        # Convert to gene symbols if needed (this requires additional mapping)
        # For now, we'll keep Ensembl IDs
        
        # Clean and preprocess
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        
        # Save processed data
        output_path = DATA_DIR / "gtex_gene_expression.csv"
        df.to_csv(output_path)
        print(f"Processed GTEx data saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing GTEx data: {e}")
        return False

def setup_manual_download_instructions():
    """Provide instructions for manual download if automatic fails."""
    print("\n" + "="*70)
    print("Manual Download Instructions")
    print("="*70)
    print("If automatic download fails, please download manually:")
    print("")
    print("1. BrainSpan Data:")
    print("   - Go to: https://www.brainspan.org/static/download.html")
    print("   - Download: 'RNA-Seq Gencode v10 summarized to genes'")
    print(f"   - Save as: {DATA_DIR / 'brainspan_raw.zip'}")
    print("")
    print("2. GTEx Data:")
    print("   - Go to: https://www.gtexportal.org/home/downloads/adult-gtex/bulk_tissue_expression")
    print("   - Download: 'Gene TPM' file")
    print(f"   - Save as: {DATA_DIR / 'gtex_gene_tpm.gct.gz'}")
    print("")
    print("3. Run processing:")
    print("   python scripts/download_data.py --process-only")
    print("="*70)

def main():
    """Main function to download and process data."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and process gene expression data')
    parser.add_argument('--process-only', action='store_true', help='Only process existing raw files')
    args = parser.parse_args()
    
    print("Setting up gene expression data...")
    
    if args.process_only:
        # Only process existing files
        brainspan_processed = process_brainspan_data(DATA_DIR / "brainspan_raw.zip")
        gtex_processed = process_gtex_data(DATA_DIR / "gtex_gene_tpm.gct.gz")
    else:
        # Download and process
        brainspan_raw = download_brainspan_data()
        if brainspan_raw:
            process_brainspan_data(brainspan_raw)
        else:
            print("Skipping BrainSpan processing due to download failure")
        
        gtex_raw = download_gtex_data()
        if gtex_raw:
            process_gtex_data(gtex_raw)
        else:
            print("Skipping GTEx processing due to download failure")
    
    # Always show manual instructions
    setup_manual_download_instructions()
    
    print("\nData setup complete! You can now run the application.")

if __name__ == "__main__":
    main()