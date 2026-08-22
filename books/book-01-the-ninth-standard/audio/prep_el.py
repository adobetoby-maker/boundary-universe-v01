import re, json, sys, pathlib
from ssmlize import say_two_digit

def say_thousands(m):
    """Spell out comma-grouped numbers.

    The earlier rule only handled a bare X,000 and left everything else as
    digits, so the rank that this whole chapter turns on -- 10,482 -- went to
    the synthesiser unspoken. Anything above 99,999 or with an odd remainder
    is left alone rather than guessed at.
    """
    th, rest = int(m.group(1)), int(m.group(2))
    if th > 99:
        return m.group(0)
    head = f'{say_two_digit(th)} thousand'
    if rest == 0:
        return head
    if rest < 100:
        return f'{head} {say_two_digit(rest)}'
    h, r = divmod(rest, 100)
    tail = f'{say_two_digit(h)} hundred'
    if r:
        tail += f' {say_two_digit(r)}'
    return f'{head} {tail}'

def prep(path):
    t = pathlib.Path(path).read_text()
    n = int(re.search(r'ch(\d+)', path).group(1))
    words="Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty".split()
    t = re.sub(r'^#\s*Chapter\s*\d+\s*[—–-]\s*(.+)$', lambda m: f"Chapter {words[n]}. {m.group(1).rstrip('.')}.", t, count=1, flags=re.M)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t, flags=re.S)          # bold -> plain
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', t, flags=re.S)
    t = re.sub(r'(?m)^\s*[-*_]{3,}\s*$', '', t).replace('⸻','')
    t = re.sub(r'`([^`]+)`', r'\1', t)                          # inline code -> plain
    t = re.sub(r'\b(\d+),(\d{3})\b', say_thousands, t)
    t = re.sub(r'(?m)^(\s*[A-Z][A-Z \-]+:\s*)(.+?)\s*/\s*(.+)$', r'\1\2 of \3', t)  # "RANK: a / b" reads as "slash"
    t = re.sub(r'(?<![\d,])0{3}(?![\d,])', 'zero zero zero', t)
    paras=[p.strip() for p in t.split('\n\n') if p.strip()]
    chunks,cur=[],''
    for p in paras:
        c=(cur+'\n\n'+p).strip()
        if len(c)>4000 and cur: chunks.append(cur); cur=p
        else: cur=c
    if cur: chunks.append(cur)
    return chunks
for a in sys.argv[1:]:
    c=prep(a); stem=pathlib.Path(a).stem
    json.dump(c, open(f'el_{stem}.json','w'))
    stray = sum(x.count('**') + x.count('`') + x.count('*') for x in c)
    print(f"{stem}: {len(c)} chunks, {sum(len(x) for x in c):,} chars, stray markdown {stray}")
