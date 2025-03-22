import os
import argparse
import datetime
from tqdm import tqdm
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor  # Changed from ProcessPoolExecutor
import mimetypes
import sys

# Initialize colorama
init()

def is_binary(file_path, sample_size=8192):
    """
    Determine if a file is binary by checking for null bytes and text encoding errors.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(sample_size)
            if b'\0' in chunk:  # Check for null bytes
                return True
            # Try to decode as text
            try:
                chunk.decode('utf-8')
                return False
            except UnicodeDecodeError:
                return True
    except Exception:
        return True  # Assume binary if we can't read the file

def get_file_metadata(file_path):
    """
    Return formatted metadata for a file.
    """
    try:
        stats = os.stat(file_path)
        size = stats.st_size
        created = datetime.datetime.fromtimestamp(stats.st_ctime)
        modified = datetime.datetime.fromtimestamp(stats.st_mtime)
        
        size_str = f"{size} bytes"
        if size > 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.2f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.2f} KB"
            
        return {
            "size": size,
            "size_str": size_str,
            "created": created,
            "modified": modified
        }
    except Exception as e:
        return {
            "size": 0,
            "size_str": "Unknown",
            "created": "Unknown",
            "modified": "Unknown",
            "error": str(e)
        }

def should_process_file(file_path, args):
    """
    Determine if a file should be processed based on arguments.
    """
    # Check if file exists and is readable
    if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
        return False
        
    # Skip the output file
    if os.path.abspath(file_path) == os.path.abspath(args.output):
        return False
        
    # Check max size
    if args.max_size and os.path.getsize(file_path) > args.max_size * 1024:
        return False
        
    # Check include extensions
    if args.include:
        include_exts = [f".{ext.lstrip('.')}" for ext in args.include.split(',')]
        if not any(file_path.lower().endswith(ext.lower()) for ext in include_exts):
            return False
            
    # Check exclude extensions
    if args.exclude:
        exclude_exts = [f".{ext.lstrip('.')}" for ext in args.exclude.split(',')]
        if any(file_path.lower().endswith(ext.lower()) for ext in exclude_exts):
            return False
            
    return True

def process_file(args, file_path, comment_style):
    """
    Process a single file and return its content with metadata.
    """
    if not should_process_file(file_path, args):
        return {
            'file_path': file_path,
            'status': 'skipped',
            'reason': 'filtered out by rules'
        }
        
    if is_binary(file_path) and not args.include_binary:
        return {
            'file_path': file_path,
            'status': 'skipped',
            'reason': 'binary file'
        }
        
    try:
        metadata = get_file_metadata(file_path)
        rel_path = os.path.relpath(file_path, args.path)
        
        # Build the header based on format
        if args.format == 'text':
            header = f"{comment_style} File: {rel_path}\n"
            header += f"{comment_style} Size: {metadata['size_str']}\n"
            header += f"{comment_style} Created: {metadata['created']}\n"
            header += f"{comment_style} Modified: {metadata['modified']}\n"
            header += f"{comment_style} {'=' * 80}\n"
            footer = f"\n\n"
        elif args.format == 'md':
            header = f"## {rel_path}\n\n"
            header += f"- Size: {metadata['size_str']}\n"
            header += f"- Created: {metadata['created']}\n"
            header += f"- Modified: {metadata['modified']}\n\n"
            header += f"```\n"
            footer = f"```\n\n"
        elif args.format == 'html':
            header = f"<div class='file'>\n"
            header += f"<h2>{rel_path}</h2>\n"
            header += f"<div class='metadata'>\n"
            header += f"<p>Size: {metadata['size_str']}</p>\n"
            header += f"<p>Created: {metadata['created']}</p>\n"
            header += f"<p>Modified: {metadata['modified']}</p>\n"
            header += f"</div>\n"
            header += f"<pre><code>\n"
            footer = f"</code></pre>\n</div>\n\n"
            
        # Read file content in chunks for memory efficiency
        content = ''
        try:
            with open(file_path, 'r', encoding='utf-8') as infile:
                chunk_size = 4096  # 4KB chunks
                for chunk in iter(lambda: infile.read(chunk_size), ''):
                    content += chunk
        except UnicodeDecodeError:
            return {
                'file_path': file_path,
                'status': 'skipped',
                'reason': 'encoding error'
            }
        
        return {
            'file_path': file_path,
            'status': 'success',
            'metadata': metadata,
            'header': header,
            'content': content,
            'footer': footer
        }
    except Exception as e:
        return {
            'file_path': file_path,
            'status': 'error',
            'reason': str(e)
        }

def get_all_files(directory, recursive=True):
    """
    Get all files in a directory, with option for recursive search.
    """
    file_list = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
    else:
        # Non-recursive, only get files in the top directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                file_list.append(item_path)
                
    return file_list

def write_output_header(outfile, args):
    """
    Write the header for the output file based on the format.
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if args.format == 'text':
        outfile.write(f"# Combined Files from {args.path}\n")
        outfile.write(f"# Generated on: {current_time}\n")
        outfile.write(f"# {'=' * 80}\n\n")
    elif args.format == 'md':
        outfile.write(f"# Combined Files from {args.path}\n\n")
        outfile.write(f"Generated on: {current_time}\n\n")
        outfile.write(f"---\n\n")
    elif args.format == 'html':
        outfile.write("<!DOCTYPE html>\n")
        outfile.write("<html lang='en'>\n")
        outfile.write("<head>\n")
        outfile.write("    <meta charset='UTF-8'>\n")
        outfile.write("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
        outfile.write(f"    <title>Combined Files from {args.path}</title>\n")
        outfile.write("    <style>\n")
        outfile.write("        body { font-family: Arial, sans-serif; margin: 20px; }\n")
        outfile.write("        .file { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }\n")
        outfile.write("        .metadata { color: #666; margin-bottom: 10px; }\n")
        outfile.write("        h1 { color: #333; }\n")
        outfile.write("        h2 { color: #0066cc; }\n")
        outfile.write("        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }\n")
        outfile.write("    </style>\n")
        outfile.write("</head>\n")
        outfile.write("<body>\n")
        outfile.write(f"<h1>Combined Files from {args.path}</h1>\n")
        outfile.write(f"<p>Generated on: {current_time}</p>\n\n")

def write_output_footer(outfile, args, stats):
    """
    Write the footer for the output file based on the format.
    """
    if args.format == 'text':
        outfile.write(f"# {'=' * 80}\n")
        outfile.write(f"# Summary Statistics\n")
        outfile.write(f"# Files processed: {stats['processed']}\n")
        outfile.write(f"# Files skipped: {stats['skipped']}\n")
        outfile.write(f"# Total size: {stats['total_size_str']}\n")
    elif args.format == 'md':
        outfile.write(f"## Summary Statistics\n\n")
        outfile.write(f"- Files processed: {stats['processed']}\n")
        outfile.write(f"- Files skipped: {stats['skipped']}\n")
        outfile.write(f"- Total size: {stats['total_size_str']}\n")
    elif args.format == 'html':
        outfile.write("<div class='summary'>\n")
        outfile.write("<h2>Summary Statistics</h2>\n")
        outfile.write(f"<p>Files processed: {stats['processed']}</p>\n")
        outfile.write(f"<p>Files skipped: {stats['skipped']}</p>\n")
        outfile.write(f"<p>Total size: {stats['total_size_str']}</p>\n")
        outfile.write("</div>\n")
        outfile.write("</body>\n")
        outfile.write("</html>\n")

def main():
    # Set up argument parser
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
    
    args = parser.parse_args()
    
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
    
    # Process files in parallel using threads instead of processes
    # (ThreadPoolExecutor doesn't require pickling functions)
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
    total_size_str = f"{total_size} bytes"
    if total_size > 1024 * 1024:
        total_size_str = f"{total_size / (1024 * 1024):.2f} MB"
    elif total_size > 1024:
        total_size_str = f"{total_size / 1024:.2f} KB"
    
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