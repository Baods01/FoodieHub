"""
迁移运行脚本 — 从 backend 目录运行 aerich 命令
用法：python run_migration.py [aerich参数]
"""
import sys, os, subprocess
d = os.path.dirname(os.path.abspath(__file__))
os.chdir(d); sys.path.insert(0, d)
args = sys.argv[1:] or ["--help"]
subprocess.run([sys.executable, "-m", "aerich"] + args, cwd=d)
