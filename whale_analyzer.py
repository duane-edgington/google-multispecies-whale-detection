#!/usr/bin/env python3
"""
Whale Detection Score Analyzer
Processes CSV files containing epoch time and whale detection scores,
and generates summary plots including histograms.
"""

import argparse
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import re
import fnmatch

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Analyze whale detection scores from CSV files')
    parser.add_argument('directory', type=str, help='Path to directory containing CSV files')
    parser.add_argument('--bins', type=int, default=10, help='Number of bins for histogram (default: 10)')
    parser.add_argument('--output', type=str, default='whale_analysis_plots.png', 
                       help='Output filename for plots (default: whale_analysis_plots.png)')
    parser.add_argument('--pattern', type=str, default='*.csv', 
                       help='File pattern to match (default: *.csv)')
    parser.add_argument('--name-pattern', type=str, required=True,
                       help='Filename pattern that must be contained in the filename (e.g., "epoch_oo_scores")')
    parser.add_argument('--time-period', type=str, default='D', 
                       help='Time period for mean calculation. Options: H=hour, D=day, W=week, M=month, 10T=10min, 30T=30min, etc. (default: D)')
    parser.add_argument('--plot3-samples', type=int, default=10000,
                       help='Number of samples for plot 3 (basic time series) (default: 10000)')
    parser.add_argument('--plot5-samples', type=int, default=100000,
                       help='Number of samples for plot 5 (enhanced time series with grey dots) (default: 100000)')
    return parser.parse_args()

def extract_date_info_from_path(file_path, directory_path):
    """
    Extract date information from file path and directory structure
    Returns: (year, month) tuple
    """
    # Try to extract date from filename first (common pattern: YYYYMMDD)
    filename = os.path.basename(file_path)
    date_patterns = [
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{4})_(\d{2})_(\d{2})',  # YYYY_MM_DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            year, month, _ = match.groups()
            return int(year), int(month)
    
    # If not found in filename, try directory structure
    relative_path = os.path.relpath(file_path, directory_path)
    path_parts = relative_path.split(os.sep)
    
    for part in path_parts:
        for pattern in date_patterns:
            match = re.search(pattern, part)
            if match:
                year, month, _ = match.groups()
                return int(year), int(month)
    
    # Fallback: use file modification time
    mod_time = os.path.getmtime(file_path)
    dt = datetime.fromtimestamp(mod_time)
    return dt.year, dt.month

def get_column_names(file_path):
    """Read column names from the first row of CSV file"""
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
        return first_line.split(',')
    except Exception as e:
        print(f"Error reading column names from {file_path}: {e}")
        return None

def filter_files_by_pattern(files, name_pattern):
    """Filter files to only include those that contain the name pattern"""
    filtered_files = []
    for file_path in files:
        filename = os.path.basename(file_path)
        if name_pattern in filename:
            filtered_files.append(file_path)
        else:
            print(f"Skipping {filename} - does not contain pattern '{name_pattern}'")
    return filtered_files

def process_csv_files(directory, file_pattern, name_pattern, num_bins):
    """Process all CSV files in the directory and return analyzed data"""
    all_data = []
    column_names = None
    file_pattern = os.path.join(directory, file_pattern)
    csv_files = glob.glob(file_pattern)
    
    if not csv_files:
        print(f"No CSV files found in {directory} with pattern {file_pattern}")
        return None
    
    print(f"Found {len(csv_files)} CSV files initially...")
    
    # Filter files by name pattern
    csv_files = filter_files_by_pattern(csv_files, name_pattern)
    
    if not csv_files:
        print(f"No files found containing pattern '{name_pattern}'")
        return None
    
    print(f"Processing {len(csv_files)} files containing pattern '{name_pattern}'...")
    
    for file_path in csv_files:
        try:
            # Get column names from first row
            current_column_names = get_column_names(file_path)
            if current_column_names is None:
                print(f"Skipping {os.path.basename(file_path)} - could not read column names")
                continue
            
            # Use the first file's column names as reference
            if column_names is None:
                column_names = current_column_names
            elif current_column_names != column_names:
                print(f"Warning: Column names in {os.path.basename(file_path)} differ from first file")
                print(f"Expected: {column_names}")
                print(f"Found: {current_column_names}")
            
            # Read CSV file, skipping the first row (header)
            df = pd.read_csv(file_path, skiprows=1, header=None, names=column_names)
            
            # Extract date information
            year, month = extract_date_info_from_path(file_path, directory)
            
            # Add metadata
            df['year'] = year
            df['month'] = month
            df['filename'] = os.path.basename(file_path)
            
            all_data.append(df)
            print(f"Processed: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {e}")
            continue
    
    if not all_data:
        print("No data was successfully processed")
        return None
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Convert epoch time to datetime
    # Use the actual column name from the header for epoch time
    epoch_col = column_names[0] if len(column_names) >= 1 else 'epoch_time'
    combined_df['datetime'] = pd.to_datetime(combined_df[epoch_col], unit='s')
    
    # Calculate statistics
    score_col = column_names[1] if len(column_names) >= 2 else 'score'
    stats = {
        'total_files': len(csv_files),
        'files_processed': len(all_data),
        'total_samples': len(combined_df),
        'score_mean': combined_df[score_col].mean(),
        'score_std': combined_df[score_col].std(),
        'score_min': combined_df[score_col].min(),
        'score_max': combined_df[score_col].max(),
        'date_range': (combined_df['datetime'].min(), combined_df['datetime'].max()),
        'column_names': column_names,
        'name_pattern': name_pattern
    }
    
    # Create histogram data for both linear and log scales
    hist_counts, hist_bins = np.histogram(combined_df[score_col], bins=num_bins)
    
    # Calculate log counts (handle zero counts by adding small epsilon)
    log_counts = np.log10(hist_counts + 1e-10)  # Add small epsilon to avoid log(0)
    
    return {
        'dataframe': combined_df,
        'stats': stats,
        'hist_counts': hist_counts,
        'log_hist_counts': log_counts,
        'hist_bins': hist_bins,
        'years_months': combined_df[['year', 'month']].drop_duplicates(),
        'column_names': column_names
    }

def create_plots(analysis_data, num_bins, output_file, time_period, plot3_samples, plot5_samples):
    """Create and save summary plots"""
    df = analysis_data['dataframe']
    stats = analysis_data['stats']
    hist_counts = analysis_data['hist_counts']
    log_hist_counts = analysis_data['log_hist_counts']
    hist_bins = analysis_data['hist_bins']
    column_names = analysis_data['column_names']
    name_pattern = stats['name_pattern']
    
    # Get actual column names from the CSV headers
    epoch_col = column_names[0] if len(column_names) >= 1 else 'epoch_time'
    score_col = column_names[1] if len(column_names) >= 2 else 'score'
    
    # Create figure with subplots - now 3x2 grid
    fig, axes = plt.subplots(3, 2, figsize=(18, 20))
    fig.suptitle(f'Whale Detection Score Analysis - Pattern: "{name_pattern}"', fontsize=16, fontweight='bold')
    
    # Unpack axes for easier access
    ax1, ax2 = axes[0]  # Histograms
    ax3, ax4 = axes[1]  # Time series and boxplot
    ax5, ax6 = axes[2]  # Enhanced time series and statistics
    
    # Plot 1: Histogram of scores (linear scale)
    ax1.bar(hist_bins[:-1], hist_counts, width=np.diff(hist_bins), 
            edgecolor='black', alpha=0.7, label=score_col)
    ax1.set_xlabel(score_col)
    ax1.set_ylabel('Number of Samples')
    ax1.set_title(f'{score_col} Distribution - Linear Scale ({num_bins} bins)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Histogram of scores (logarithmic scale)
    ax2.bar(hist_bins[:-1], hist_counts, width=np.diff(hist_bins), 
            edgecolor='black', alpha=0.7, label=score_col)
    ax2.set_yscale('log')
    ax2.set_xlabel(score_col)
    ax2.set_ylabel('Number of Samples (log₁₀)')
    ax2.set_title(f'{score_col} Distribution - Logarithmic Scale ({num_bins} bins)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Plot 3: Basic time series of scores (sampled)
    time_sample = df.sample(min(plot3_samples, len(df)))  # Sample for plotting efficiency
    ax3.scatter(time_sample['datetime'], time_sample[score_col], alpha=0.6, s=10, label=score_col)
    ax3.set_xlabel('Time')
    ax3.set_ylabel(score_col)
    ax3.set_title(f'{score_col} Time Series ({plot3_samples:,} samples)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 4: Boxplot by year-month
    df['year_month'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    # Sample for plotting efficiency if too many groups
    unique_groups = df['year_month'].nunique()
    if unique_groups > 12:
        # Group by year only if too many months
        df['year_month'] = df['year'].astype(str)
    
    # Manual sampling to avoid deprecation warnings
    sampled_dfs = []
    for group_name, group_data in df.groupby('year_month'):
        sampled_group = group_data.sample(min(100, len(group_data)))
        sampled_dfs.append(sampled_group)
    
    sampled_df = pd.concat(sampled_dfs, ignore_index=True)
    
    # Create boxplot data
    boxplot_data = []
    labels = []
    for group_name, group_data in sampled_df.groupby('year_month'):
        boxplot_data.append(group_data[score_col].values)
        labels.append(group_name)
    
    ax4.boxplot(boxplot_data, tick_labels=labels)
    ax4.set_title(f'{score_col} Distribution by Time Period')
    ax4.set_ylabel(score_col)
    ax4.tick_params(axis='x', rotation=45)
    
    # Plot 5: Enhanced time series with individual points and period means
    # Sample up to plot5_samples individual points
    max_samples = min(plot5_samples, len(df))
    time_sample_large = df.sample(max_samples, random_state=42)  # Fixed seed for reproducibility
    
    # Plot individual samples as light grey dots
    ax5.scatter(time_sample_large['datetime'], time_sample_large[score_col], 
               alpha=0.3, s=2, color='grey', label='Individual samples')
    
    # Calculate mean scores for the specified time period
    period_map = {
        '10T': '10 Minutes', '30T': '30 Minutes', 'H': 'Hour',
        '2H': '2 Hours', '6H': '6 Hours', '12H': '12 Hours',
        'D': 'Day', 'W': 'Week', 'M': 'Month'
    }
    period_name = period_map.get(time_period, f'{time_period} period')
    
    # Resample to get mean scores for each period
    df_resampled = df.set_index('datetime')
    period_means = df_resampled[score_col].resample(time_period).mean()
    
    # Plot period means as larger black dots
    ax5.scatter(period_means.index, period_means.values, 
               alpha=0.9, s=50, color='black', label=f'{period_name} means')
    
    ax5.set_xlabel('Time')
    ax5.set_ylabel(score_col)
    ax5.set_title(f'{score_col} Time Series: Individual Samples + {period_name} Means\n({max_samples:,} samples)')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 6: Statistics table with column information
    ax6.axis('off')
    stats_text = [
        f'Filename Pattern: "{name_pattern}"',
        f'Column Names: {", ".join(column_names)}',
        f'Files Found: {stats["total_files"]}',
        f'Files Processed: {stats["files_processed"]}',
        f'Total Samples: {stats["total_samples"]:,}',
        f'Date Range: {stats["date_range"][0].strftime("%Y-%m-%d")} to {stats["date_range"][1].strftime("%Y-%m-%d")}',
        f'Mean {score_col}: {stats["score_mean"]:.3f}',
        f'Std Dev: {stats["score_std"]:.3f}',
        f'Min {score_col}: {stats["score_min"]:.3f}',
        f'Max {score_col}: {stats["score_max"]:.3f}',
        f'Time Period for Means: {period_name}',
        f'Plot 3 Samples: {plot3_samples:,}',
        f'Plot 5 Samples: {plot5_samples:,}'
    ]
    ax6.text(0.1, 0.9, '\n'.join(stats_text), transform=ax6.transAxes, 
             fontfamily='monospace', verticalalignment='top', fontsize=9)
    ax6.set_title('Summary Statistics')
    
    # Add date information from directory/file structure
    years_months = analysis_data['years_months']
    if not years_months.empty:
        date_info = f"Data from: {years_months['year'].min()}-{years_months['month'].min():02d} to {years_months['year'].max()}-{years_months['month'].max():02d}"
        fig.text(0.5, 0.01, date_info, ha='center', fontsize=10, style='italic')
    
    # Add column information footer
    column_info = f"Columns: {epoch_col} (epoch time), {score_col} (detection score) | Pattern: {name_pattern} | Time period: {period_name} | Plot samples: {plot3_samples:,}/{plot5_samples:,}"
    fig.text(0.5, 0.02, column_info, ha='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=0.12)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Plots saved to {output_file}")

def main():
    """Main function"""
    args = parse_arguments()
    
    # Validate directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        return
    
    # Process CSV files
    analysis_data = process_csv_files(args.directory, args.pattern, args.name_pattern, args.bins)
    
    if analysis_data is None:
        return
    
    # Create and save plots
    create_plots(analysis_data, args.bins, args.output, args.time_period, args.plot3_samples, args.plot5_samples)
    
    # Print summary
    print("\nAnalysis Complete!")
    print(f"Filename pattern: '{args.name_pattern}'")
    print(f"Column names found: {analysis_data['stats']['column_names']}")
    print(f"Files found matching pattern: {analysis_data['stats']['total_files']}")
    print(f"Files successfully processed: {analysis_data['stats']['files_processed']}")
    print(f"Total samples: {analysis_data['stats']['total_samples']:,}")
    score_col = analysis_data['stats']['column_names'][1] if len(analysis_data['stats']['column_names']) >= 2 else 'score'
    print(f"{score_col} range: {analysis_data['stats']['score_min']:.3f} - {analysis_data['stats']['score_max']:.3f}")
    print(f"Mean {score_col}: {analysis_data['stats']['score_mean']:.3f}")
    print(f"Plot 3 samples: {args.plot3_samples:,}")
    print(f"Plot 5 samples: {args.plot5_samples:,}")

if __name__ == "__main__":
    main()
