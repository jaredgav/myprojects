import os
import sys

def get_dir_size(path):
    """Return total size (in bytes) of all files in a directory (recursively)."""
    total = 0
    for root, dirs, files in os.walk(path, onerror=None):
        for f in files:
            try:
                fp = os.path.join(root, f)
                total += os.path.getsize(fp)
            except (OSError, FileNotFoundError):
                pass  # Skip files that can't be accessed
    return total

def list_dir_sizes(base_path):
    """List subdirectories and their sizes in descending order."""
    sizes = []
    for entry in os.scandir(base_path):
        if entry.is_dir(follow_symlinks=False):
            size = get_dir_size(entry.path)
            sizes.append((entry.name, size))

    # Sort by size (largest first)
    sizes.sort(key=lambda x: x[1], reverse=True)

    # Print results
    print(f"\nDirectory sizes under: {base_path}\n")
    for name, size in sizes:
        print(f"{name:<40} {size/1024/1024:>10.2f} MB")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dir_sizes.py <path>")
        sys.exit(1)

    base_path = sys.argv[1]

    if not os.path.isdir(base_path):
        print(f"Error: '{base_path}' is not a valid directory.")
        sys.exit(1)

    list_dir_sizes(base_path)
