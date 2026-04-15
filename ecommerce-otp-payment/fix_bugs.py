import pathlib

# ── Fix 1: index.html category URL encoding ──
p = pathlib.Path(r'templates/index.html')
txt = p.read_text(encoding='utf-8')
old = '/?category={{ cat }}'
new = '/?category={{ cat | urlencode }}'
if old in txt:
    txt = txt.replace(old, new)
    p.write_text(txt, encoding='utf-8')
    print('Fix 1 done: category URL encoding')
else:
    print('Fix 1 SKIPPED: pattern not found')

# ── Fix 2: checkout.html bank select text color ──
p2 = pathlib.Path(r'templates/checkout.html')
txt2 = p2.read_text(encoding='utf-8')

# Fix the select element
old_select = '<select class="form-select" id="bank-select">'
new_select = '<select class="form-select" id="bank-select" style="color:#e2e8f0;background:#1e293b;">'
if old_select in txt2:
    txt2 = txt2.replace(old_select, new_select)
    print('Fix 2a done: select element styled')
else:
    print('Fix 2a SKIPPED')

# Fix the placeholder option
old_opt0 = '<option value="">-- Choose Bank --</option>'
new_opt0 = '<option value="" style="background:#1e293b;color:#94a3b8;">-- Choose Bank --</option>'
if old_opt0 in txt2:
    txt2 = txt2.replace(old_opt0, new_opt0)
    print('Fix 2b done: placeholder option styled')
else:
    print('Fix 2b SKIPPED')

# Fix the loop options
old_opt = '<option>{{ bank }}</option>'
new_opt = '<option style="background:#1e293b;color:#e2e8f0;">{{ bank }}</option>'
if old_opt in txt2:
    txt2 = txt2.replace(old_opt, new_opt)
    print('Fix 2c done: bank options styled')
else:
    print('Fix 2c SKIPPED')

p2.write_text(txt2, encoding='utf-8')
print('All fixes applied!')
