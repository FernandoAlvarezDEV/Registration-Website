import os
import shutil
import glob
import re

base_dir = r"c:\Users\ferjo\OneDrive\Desktop\code\Web Develepment with AntiGravity"
frontend_dir = os.path.join(base_dir, "frontend")
js_dir = os.path.join(frontend_dir, "js")

# Create js dir if it doesn't exist
os.makedirs(js_dir, exist_ok=True)

# 1. Move index.js to frontend/js/ if it exists in base_dir
index_js_path = os.path.join(base_dir, "index.js")
if os.path.exists(index_js_path):
    shutil.move(index_js_path, os.path.join(js_dir, "index.js"))
    print("Moved index.js to frontend/js/")

# 2. Extract inline scripts from HTMLs in frontend/
html_files = glob.glob(os.path.join(frontend_dir, "*.html"))

# Regex to match script tags with content, avoiding src="..."
# We capture the optional id/class attributes and the content inside
script_pattern = re.compile(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)

for html_file in html_files:
    filename = os.path.basename(html_file)
    name_no_ext = os.path.splitext(filename)[0].lower() # e.g. "admin", "dashboard", "index"
    
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We might have multiple scripts. We want to skip tailwind.config
    def replacer(match):
        script_content = match.group(1).strip()
        # Skip if it is a tailwind config or very short (less than 20 chars)
        if "tailwind.config" in script_content or len(script_content) < 20:
            return match.group(0) # don't replace
        
        # It's an actual script! Let's save it to js/<name>.js
        js_path = os.path.join(js_dir, f"{name_no_ext}.js")
        with open(js_path, "w", encoding="utf-8") as jf:
            jf.write(script_content)
        
        print(f"Extracted JS from {filename} to js/{name_no_ext}.js")
        # Return the new script tag referencing the external file
        return f'<script src="js/{name_no_ext}.js"></script>'
    
    new_content = script_pattern.sub(replacer, content)
    
    if new_content != content:
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(new_content)
            print(f"Updated {filename} with external script tag")

print("JS Extraction Complete!")
