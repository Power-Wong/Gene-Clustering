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

# Data URLs
BRAINSPAN_URL = "https://www.brainspan.org/api/v2/well_known_file_download/267666525"  # RNA-Seq Gencode v10 summarized to genes
GTEx_URL = "https://storage.googleapis.com/gtex_analysis_v8/rna_seq_data/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_tpm.gct.gz"

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def download_brainspan_data():
    """Download BrainSpan developmental transcriptome data."""
    print("Downloading BrainSpan data...")
    
    try:
        response = requests.get(BRAINSPAN_URL, stream=True, timeout=300)
        response.raise_for_status()
        
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

def download_gtex_data():
    """Download GTEx bulk tissue expression data."""
    print("Downloading GTEx data...")
    
    try:
        response = requests.get(GTEx_URL, stream=True, timeout=600)  # GTEx file is large
        response.raise_for_status()
        
        raw_path = DATA_DIR / "gtex_raw.gct.gz"
        with open(raw_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded GTEx data to {raw_path}")
        return raw_path
        
    except Exception as e:
        print(f"Error downloading GTEx data: {e}")
        print("Please manually download from: https://www.gtexportal.org/home/downloads/adult-gtex/bulk_tissue_expression")
        print("Download the gene TPM file and save as gtex_raw.gct.gz")
        return None

def process_brainspan_data(raw_file_path):
    """Process BrainSpan data into a clean CSV format."""
    if not os.path.exists(raw_file_path):
        print(f"Raw file not found: {raw_file_path}")
        return False
    
    try:
        # Assuming the file is a zip containing CSV or similar
        # You may need to adjust this based on actual file format
        import zipfile
        with zipfile.ZipFile(raw_file_path, 'r') as zip_ref:
            # Extract and find the main data file
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if csv_files:
                zip_ref.extract(csv_files[0], DATA_DIR)
                df = pd.read_csv(DATA_DIR / csv_files[0], index_col=0)
            else:
                print("No CSV files found in BrainSpan archive")
                return False
        
        # Clean and preprocess
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        df.index = df.index.str.upper()
        
        output_path = DATA_DIR / "brainspan_gene_expression.csv"
        df.to_csv(output_path)
        print(f"Processed BrainSpan data saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing BrainSpan data: {e}")
        return False

def process_gtex_data(raw_file_path):
    """Process GTEx data into a clean CSV format."""
    if not os.path.exists(raw_file_path):
        print(f"Raw file not found: {raw_file_path}")
        return False
    
    try:
        # GTEx GCT format: first 2 lines are headers, then gene data
        df = pd.read_csv(raw_file_path, sep='\t', skiprows=2, compression='gzip')
        
        # First column is gene ID + description, split it
        df[['gene_id', 'gene_name']] = df['Name'].str.split('\\|', expand=True)
        df = df.set_index('gene_name')
        
        # Remove metadata columns and keep only sample columns
        sample_cols = [col for col in df.columns if not col in ['gene_id', 'Name']]
        df = df[sample_cols]
        
        # Clean gene names (remove version numbers, etc.)
        df.index = df.index.str.split('.').str[0].str.upper()
        
        # Remove rows with all zeros or NaN
        df = df.loc[(df != 0).any(axis=1)]
        df = df.dropna(how='all')
        
        output_path = DATA_DIR / "gtex_gene_expression.csv"
        df.to_csv(output_path)
        print(f"Processed GTEx data saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing GTEx data: {e}")
        return False

def main():
    """Main function to download and process data."""
    print("Setting up gene expression data...")
    
    # Download and process BrainSpan data
    brainspan_raw = download_brainspan_data()
    if brainspan_raw:
        process_brainspan_data(brainspan_raw)
    else:
        print("Skipping BrainSpan processing due to download failure")
    
    # Download and process GTEx data
    gtex_raw = download_gtex_data()
    if gtex_raw:
        process_gtex_data(gtex_raw)
    else:
        print("Skipping GTEx processing due to download failure")
    
    print("\nData setup complete! You can now run the application.")

if __name__ == "__main__":
    main()