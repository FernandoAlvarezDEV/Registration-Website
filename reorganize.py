import os
import shutil
import glob
import re

base_dir = r"c:\Users\ferjo\OneDrive\Desktop\code\Web Develepment with AntiGravity"
frontend_dir = os.path.join(base_dir, "frontend")
js_dir = os.path.join(frontend_dir, "js")

# Find all HTML files in base_dir
html_files = glob.glob(os.path.join(base_dir, "*.html"))

# Move them to frontend_dir if they are not already there
for html_file in html_files:
    filename = os.path.basename(html_file)
    dest_path = os.path.join(frontend_dir, filename)
    shutil.move(html_file, dest_path)
    print(f"Moved {filename} to {frontend_dir}")

# Find all HTMLs in frontend_dir and update the script tags and links
html_files_in_frontend = glob.glob(os.path.join(frontend_dir, "*.html"))

for html_file in html_files_in_frontend:
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update script src paths from ../js/name.js to js/name.js
    content = re.sub(r'src=["\']\.\./js/([^"\']+)["\']', r'src="js/\1"', content)
    # Also in case it was something else like js/ or ./js/ it's probably fine.
    
    # Write updated content back
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Updated script paths in {html_file}")

# Clean up any leftover htmls directory in frontend if it exists
htmls_nested_dir = os.path.join(frontend_dir, "htmls")
if os.path.exists(htmls_nested_dir):
    # move any inner htmls out to frontend just in case
    inner_htmls = glob.glob(os.path.join(htmls_nested_dir, "*.html"))
    for h in inner_htmls:
        shutil.move(h, os.path.join(frontend_dir, os.path.basename(h)))
    try:
        shutil.rmtree(htmls_nested_dir)
        print(f"Removed old directory {htmls_nested_dir}")
    except Exception as e:
        print(f"Could not remove {htmls_nested_dir}: {e}")

print("Reorganization complete.")
