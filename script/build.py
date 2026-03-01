import compileall
import os
import sys

def compile_src_to_pyc():
    src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
    
    if not os.path.exists(src_dir):
        print(f"错误: src目录不存在: {src_dir}")
        sys.exit(1)
    
    print(f"正在编译: {src_dir}")
    
    result = compileall.compile_dir(src_dir, force=True, quiet=0)
    
    if result:
        print("\n编译成功!")
        print(f"已将 {src_dir} 下所有 .py 文件编译为 .pyc 文件")
    else:
        print("\n编译失败!")
        sys.exit(1)

if __name__ == '__main__':
    compile_src_to_pyc()
