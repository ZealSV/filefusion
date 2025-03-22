import os

def main():
    # Get directory path from user
    dir_path = input("Enter the directory path: ")
    
    # Validate directory path
    if not os.path.isdir(dir_path):
        print(f"Error: {dir_path} is not a valid directory")
        return
    
    # Get comment style
    comment_style = input("Enter comment style (1 for // or 2 for #): ")
    if comment_style == "1":
        comment = "//"
    else:
        comment = "#"
    
    # Create output file name
    output_file = "combined_files.txt"
    
    # Counters for summary
    files_processed = 0
    files_skipped = 0
    
    # Open output file for writing
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip the output file itself
                if os.path.abspath(file_path) == os.path.abspath(output_file):
                    continue
                
                try:
                    # Try to read file content
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                    
                    # Write file path as comment and then content to output file
                    outfile.write(f"{comment} {file_path}\n")
                    outfile.write(content)
                    outfile.write("\n\n")
                    
                    files_processed += 1
                    print(f"Processed: {file_path}")
                except Exception as e:
                    outfile.write(f"{comment} ERROR: Could not read {file_path}\n\n")
                    files_skipped += 1
                    print(f"Skipped: {file_path} - {e}")
    
    print(f"\nAll files combined into {output_file}")
    print(f"Files processed: {files_processed}")
    print(f"Files skipped: {files_skipped}")

if __name__ == "__main__":
    main()