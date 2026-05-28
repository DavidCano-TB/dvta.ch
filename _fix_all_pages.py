"""Fix /api/ paths in ALL game/page HTML files"""
import re, os

files_to_fix = [
    'static/pages/cuentos.html',
    'static/cuentos.html',
]

# Also find any other HTML files with bare /api/
for root, dirs, files in os.walk('static'):
    if '.git' in root or 'node_modules' in root:
        continue
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            if path.replace('\\','/') not in [x.replace('\\','/') for x in files_to_fix]:
                try:
                    content = open(path, 'r', encoding='utf-8').read()
                    bare = len(re.findall(r"(?<!/bank)/api/", content))
                    if bare > 0:
                        files_to_fix.append(path)
                except:
                    pass

for root, dirs, files in os.walk('game_pages'):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            try:
                content = open(path, 'r', encoding='utf-8').read()
                bare = len(re.findall(r"(?<!/bank)/api/", content))
                if bare > 0:
                    files_to_fix.append(path)
            except:
                pass

# Deduplicate
files_to_fix = list(set(files_to_fix))

total_fixed = 0
for path in sorted(files_to_fix):
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    
    # Replace /api/ with /bank/api/ where not already prefixed
    # Simple approach: replace all '/api/' and `/api/` patterns
    new_src = src
    # Handle single-quoted strings
    new_src = new_src.replace("'/api/", "'/bank/api/")
    # Handle double-quoted strings  
    new_src = new_src.replace('"/api/', '"/bank/api/')
    # Handle backtick template literals
    new_src = new_src.replace('`/api/', '`/bank/api/')
    # Handle after + or space
    new_src = new_src.replace(' /api/', ' /bank/api/')
    new_src = new_src.replace('+/api/', '+/bank/api/')
    
    # But DON'T double-prefix (fix /bank/bank/api/ back)
    new_src = new_src.replace('/bank/bank/api/', '/bank/api/')
    
    if new_src != src:
        count = src.count('/api/') - new_src.count('/api/')
        # Verify we didn't break anything
        remaining = len(re.findall(r"(?<!/bank)/api/", new_src))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_src)
        print(f"  ✅ {path}: fixed (remaining bare: {remaining})")
        total_fixed += 1
    else:
        # Check if there are still bare ones
        remaining = len(re.findall(r"(?<!/bank)/api/", src))
        if remaining > 0:
            print(f"  ⚠️  {path}: {remaining} bare /api/ NOT fixed (complex pattern)")
        
print(f"\nTotal files fixed: {total_fixed}")
