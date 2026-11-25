import os
import shutil

base_dir = r"C:\Users\WILLI\.gemini\antigravity\scratch\PIA_Amazon_Optimizer"
sub_dir = os.path.join(base_dir, "PIA_Amazon_Optimizer")
os.makedirs(sub_dir, exist_ok=True)

items = ["app.py", "Procfile", "requirements.txt", "render.yaml", "README.md", "core", "static", "templates"]

for item in items:
    src = os.path.join(base_dir, item)
    dst = os.path.join(sub_dir, item)
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    elif os.path.isfile(src):
        shutil.copy2(src, dst)

print("Created mirrored PIA_Amazon_Optimizer subfolder for 100% failproof Render path resolution!")
