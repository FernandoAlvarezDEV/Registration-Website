import os

directory = r'c:\Users\ferjo\OneDrive\Desktop\Proyectos Personales\Registration-Website'

files_to_check = [
    'frontend/success.html',
    'frontend/login.html',
    'frontend/js/success.js',
    'frontend/Index.html',
    'frontend/event-details.html',
    'frontend/dashboard.html',
    'frontend/admin.html',
    'render.yaml'
]

for rel_path in files_to_check:
    path = os.path.join(directory, rel_path)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('Index.html', 'index.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
