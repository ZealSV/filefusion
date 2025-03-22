# FileFusion

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-brightgreen)

FileFusion is a powerful file aggregation tool that combines multiple files from a directory into a single organized document. Perfect for code reviews, documentation, backups, or creating shareable code snapshots.

## Features

- **Multi-format Output**: Generate combined files in plain text, Markdown, or HTML formats
- **Parallel Processing**: Efficiently process large directories using multi-threading
- **Smart Filtering**: Include/exclude files by extension, size, or type
- **Rich Metadata**: Capture and display file creation dates, sizes, and modification times
- **Customizable Comments**: Choose between different comment styles
- **Deep Directory Traversal**: Recursively scan nested directory structures
- **Binary File Handling**: Detect and optionally skip binary files
- **Colorized Output**: Visual feedback with progress bars and color-coded terminal output
- **Memory Efficient**: Process large files in chunks to minimize memory usage

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/filefusion.git
cd filefusion

# Install required dependencies
pip install colorama tqdm
```

## Quick Start

```bash
# Basic usage
python3 filefusion.py --path /path/to/your/directory

# Generate HTML report with all files including metadata
python3 filefusion.py --path /path/to/your/directory --format html --output code_report.html

# Extract only Python and JavaScript files, excluding tests
python3 filefusion.py --path /path/to/your/directory --include py,js --exclude test_
```

## Command-line Options

### Required Arguments

--path PATH - Directory path to process

### File Filtering

--include EXT1,EXT2,... - Only include files with specified extensions
--exclude EXT1,EXT2,... - Exclude files with specified extensions
--max-size SIZE - Maximum file size in KB to process
--include-binary - Include binary files (excluded by default)

### Output Options

--output FILENAME - Output filename (default: combined_files.txt)
--format {text,md,html} - Output format (default: text)
--comment-style {1,2} - Comment style (1 for //, 2 for #)

### Processing Options

--recursive - Scan subdirectories recursively (default: True)
--no-recursive - Do not scan subdirectories
--workers N - Number of worker threads (default: CPU count \* 4, max 32)

## Use Cases

- **Code Reviews**: Package relevant code files for easier review
- **Documentation**: Generate reference documentation of project structure
- **Code Sharing**: Share code snippets with colleagues while preserving context
- **Backup**: Create readable backups of important project files
- **Learning**: Combine tutorial code into a single readable document
- **Onboarding**: Help new team members understand project structure

## Performance

FileFusion is designed to handle large projects efficiently:

- Multi-threading enables processing hundreds of files in seconds
- Memory-efficient processing handles large codebases without issues
- Progress indicators keep you informed during long operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This tool was inspired by the need to simplify code reviews and documentation
- Thanks to all contributors who help improve this tool
