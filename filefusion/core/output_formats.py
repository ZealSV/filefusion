"""Output format handlers for FileFusion."""

import datetime

def write_output_header(outfile, args):
    """
    Write the header for the output file based on the format.
    
    Args:
        outfile: Output file object
        args: Command-line arguments
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
    
    Args:
        outfile: Output file object
        args: Command-line arguments
        stats: Statistics dictionary
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