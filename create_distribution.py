import hashlib
import os
import zipfile
from datetime import datetime

def create_distribution():
    # Create distribution folder
    dist_folder = "distribution"
    os.makedirs(dist_folder, exist_ok=True)
    
    # Files to include
    files = [
        "dist/ChildGrowthAnalyzer.exe",
        "README.txt",
        "example.csv"
    ]
    
    # Create ZIP file
    zip_name = f"ChildGrowthAnalyzer_v1.1.0_{datetime.now().strftime('%Y%m%d')}.zip"
    zip_path = os.path.join(dist_folder, zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))
    
    # Create SHA256 checksum
    sha256_hash = hashlib.sha256()
    with open(zip_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    # Save checksum
    checksum = sha256_hash.hexdigest()
    checksum_file = os.path.join(dist_folder, "checksum.txt")
    with open(checksum_file, "w") as f:
        f.write(f"{zip_name}: {checksum}")
    
    print(f"Distribution created: {zip_path}")
    print(f"SHA256 Checksum: {checksum}")

if __name__ == "__main__":
    create_distribution() 