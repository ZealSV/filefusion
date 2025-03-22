"""File processing functionality for FileFusion."""

import os
import datetime
from filefusion.utils.helpers import get_file_metadata, is_binary

def get_all_files(directory, recursive=True):
    """
    Get all files in a directory, with option for recursive search.
    
    Args:
        directory: Path to the directory to scan
        recursive: Whether to scan subdirectories
        
    Returns:
        list: List of file paths
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

def should_process_file(file_path, args):
    """
    Determine if a file should be processed based on arguments.
    
    Args:
        file_path: Path to the file to check
        args: Command-line arguments
        
    Returns:
        bool: Whether the file should be processed
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

def build_file_header(file_path, args, metadata, comment_style):
    """
    Build the header for a file based on the output format.
    
    Args:
        file_path: Path to the file
        args: Command-line arguments
        metadata: File metadata
        comment_style: Comment style to use
        
    Returns:
        str: Header text
    """
    rel_path = os.path.relpath(file_path, args.path)
    
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
    else:
        header = f"# {rel_path}\n\n"
        footer = f"\n\n"
        
    return header, footer

def process_file(args, file_path, comment_style):
    """
    Process a single file and return its content with metadata.
    
    Args:
        args: Command-line arguments
        file_path: Path to the file to process
        comment_style: Comment style to use
        
    Returns:
        dict: File processing result and metadata
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
        
        # Build header and footer
        header, footer = build_file_header(file_path, args, metadata, comment_style)
            
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