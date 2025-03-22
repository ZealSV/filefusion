"""Command-line interface for FileFusion."""

import argparse
import os
import sys
from tqdm import tqdm
from colorama import Fore, Style, init

from filefusion.core.file_processor import get_all_files, process_file
from filefusion.core.output_formats import (
    write_output_header, 
    write_output_footer,
)
from filefusion.utils.helpers import get_human_readable_size

# Initialize colorama
init()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Combine files from a directory into a single output file.')
    
    # Required arguments
    parser.add_argument('--path', type=str, help='Directory path to process', required=True)
    
    # File filtering options
    parser.add_argument('--include', type=str, help='Only include files with these extensions (comma separated)')
    parser.add_argument('--exclude', type=str, help='Exclude files with these extensions (comma separated)')
    parser.add_argument('--max-size', type=int, help='Maximum file size in KB to process')
    parser.add_argument('--include-binary', action='store_true', help='Include binary files (default: exclude)')
    
    # Output options
    parser.add_argument('--output', type=str, default='combined_files.txt', help='Output filename')
    parser.add_argument('--format', choices=['text', 'md', 'html'], default='text', help='Output format')
    parser.add_argument('--comment-style', type=int, choices=[1, 2], default=2, 
                        help='Comment style (1 for //, 2 for #)')
    
    # Processing options
    parser.add_argument('--recursive', action='store_true', default=True, 
                        help='Scan subdirectories recursively (default: True)')
    parser.add_argument('--no-recursive', action='store_false', dest='recursive',
                        help='Do not scan subdirectories')
    parser.add_argument('--workers', type=int, default=min(32, os.cpu_count() * 4), 
                        help='Number of worker threads (default: CPU count * 4)')
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Validate directory path
    if not os.path.isdir(args.path):
        print(f"{Fore.RED}Error:{Style.RESET_ALL} {args.path} is not a valid directory")
        return 1
    
    # Set comment style
    comment_style = "//" if args.comment_style == 1 else "#"
    
    # Get all files
    print(f"{Fore.BLUE}Scanning directory:{Style.RESET_ALL} {args.path}")
    all_files = get_all_files(args.path, args.recursive)
    print(f"{Fore.BLUE}Found:{Style.RESET_ALL} {len(all_files)} files")
    
    # Process files using multiple threads
    from concurrent.futures import ThreadPoolExecutor
    
    results = []
    print(f"{Fore.BLUE}Processing files with {args.workers} threads{Style.RESET_ALL}")
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Create a list of tuples for each file to process
        file_tasks = [(args, file_path, comment_style) for file_path in all_files]
        
        # Process files with progress bar
        for result in tqdm(
            executor.map(lambda x: process_file(*x), file_tasks),
            total=len(all_files),
            desc="Processing files",
            unit="file"
        ):
            results.append(result)
    
    # Filter results
    successful = [r for r in results if r['status'] == 'success']
    skipped = [r for r in results if r['status'] == 'skipped']
    errors = [r for r in results if r['status'] == 'error']
    
    # Calculate statistics
    total_size = sum(r['metadata']['size'] for r in successful)
    total_size_str = get_human_readable_size(total_size)
    
    stats = {
        'processed': len(successful),
        'skipped': len(skipped) + len(errors),
        'errors': len(errors),
        'total_size': total_size,
        'total_size_str': total_size_str
    }
    
    # Write output file
    print(f"{Fore.BLUE}Writing to output file:{Style.RESET_ALL} {args.output}")
    with open(args.output, 'w', encoding='utf-8') as outfile:
        # Write header
        write_output_header(outfile, args)
        
        # Write each successful file
        for result in successful:
            outfile.write(result['header'])
            outfile.write(result['content'])
            outfile.write(result['footer'])
        
        # Write footer with statistics
        write_output_footer(outfile, args, stats)
    
    # Print summary
    print(f"\n{Fore.GREEN}Summary:{Style.RESET_ALL}")
    print(f"  Files processed: {Fore.GREEN}{stats['processed']}{Style.RESET_ALL}")
    print(f"  Files skipped: {Fore.YELLOW}{len(skipped)}{Style.RESET_ALL}")
    print(f"  Errors: {Fore.RED}{len(errors)}{Style.RESET_ALL}")
    print(f"  Total size: {Fore.CYAN}{stats['total_size_str']}{Style.RESET_ALL}")
    print(f"\nAll files combined into {Fore.GREEN}{args.output}{Style.RESET_ALL}")
    
    # Print some errors if any
    if errors:
        print(f"\n{Fore.RED}Some files had errors:{Style.RESET_ALL}")
        for i, error in enumerate(errors[:5]):  # Show first 5 errors
            print(f"  {i+1}. {error['file_path']}: {error['reason']}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())