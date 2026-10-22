#!/usr/bin/env python3
"""给全站 HTML 注入 Mellum 主题样式表引用。
用法: python3 inject.py [--apply]
"""
import os, sys, re

ROOT = '/home/xinyan/桌面/html'
THEME = 'mellum-theme.css'
MARK = 'mellum-theme.css'

def rel_path(page_path):
    """从页面所在目录回到站点根目录的相对前缀。"""
    rel_dir = os.path.dirname(os.path.relpath(page_path, ROOT))
    if rel_dir in ('', '.'):
        return THEME                      # 根目录页面：直接同名引用
    depth = len(rel_dir.split(os.sep))
    return ('../' * depth) + THEME

def main():
    apply = '--apply' in sys.argv
    stats = {'inject': 0, 'skip_done': 0, 'skip_nohead': 0, 'already': 0}
    problems = []
    for dp, dn, fn in os.walk(ROOT):
        if 'style_study' in dp or '/.git' in dp:
            continue
        for f in sorted(fn):
            if not f.endswith('.html'):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT)
            # mellum.html 自带完整样式，跳过
            if rel == 'gitlearn/mellum.html':
                stats['skip_done'] += 1
                continue
            try:
                s = open(p, encoding='utf-8').read()
            except Exception as e:
                problems.append((rel, 'read: %s' % e))
                continue
            if MARK in s:
                stats['already'] += 1
                continue
            link = '<link rel="stylesheet" href="%s">' % rel_path(p)
            if '</head>' in s:
                s2 = s.replace('</head>', link + '\n</head>', 1)
            elif '<body' in s:
                s2 = re.sub(r'(<body[^>]*>)', r'\1\n' + link, s, count=1)
                stats['skip_nohead'] += 1
            else:
                problems.append((rel, 'no </head> and no <body>'))
                continue
            stats['inject'] += 1
            if apply:
                open(p, 'w', encoding='utf-8').write(s2)
    print('注入:', stats['inject'], '| 跳过(mellum):', stats['skip_done'],
          '| 已含:', stats['already'], '| 无 head 走 body:', stats['skip_nohead'])
    if problems:
        print('\n问题:')
        for r, m in problems:
            print(' ', r, '->', m)
    else:
        print('无问题')
    print('模式:', 'APPLY 已写入' if apply else 'DRY-RUN 未写入')

if __name__ == '__main__':
    main()
