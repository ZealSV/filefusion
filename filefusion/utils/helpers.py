"""Helper functions for FileFusion."""

import os
import datetime

def is_binary(file_path, sample_size=8192):
    """
    Determine if a file is binary by checking for null bytes and text encoding errors.
    
    Args:
        file_path: Path to the file to check
        sample_size: Number of bytes to sample
        
    Returns:
        bool: True if the file is binary, False otherwise
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

def get_human_readable_size(size_bytes):
    """
    Convert a size in bytes to a human readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Human readable size string
    """
    size_str = f"{size_bytes} bytes"
    if size_bytes > 1024 * 1024:
        size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes > 1024:
        size_str = f"{size_bytes / 1024:.2f} KB"
    return size_str

def get_file_metadata(file_path):
    """
    Get metadata for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict: Dictionary containing file metadata
    """
    try:
        stats = os.stat(file_path)
        size = stats.st_size
        created = datetime.datetime.fromtimestamp(stats.st_ctime)
        modified = datetime.datetime.fromtimestamp(stats.st_mtime)
        
        size_str = get_human_readable_size(size)
            
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