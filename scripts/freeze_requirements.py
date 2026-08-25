"""使用当前虚拟环境生成完整依赖快照。

脚本刻意写入 ``requirements-freeze.txt``，而不是直接覆盖手工维护的
``requirements.txt``。这样可以先检查快照，再决定如何拆分生产和开发依赖。
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """调用当前解释器的 pip freeze，并以 UTF-8 写入项目根目录。"""

    # result：pip freeze 子进程的执行结果，stdout 中保存完整依赖清单。
    # sys.executable 保证使用当前已激活虚拟环境中的 pip，而不是系统 Python。
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        check=True,
        capture_output=True,
        text=True,
    )

    # project_root：从脚本位置向上一级解析得到的项目根目录绝对路径。
    project_root = Path(__file__).resolve().parents[1]
    # output_path：依赖快照的目标文件，刻意与手工维护的 requirements.txt 分开。
    output_path = project_root / "requirements-freeze.txt"

    # 统一使用 UTF-8 和 LF 换行，确保快照在 GitHub 与其他平台可读。
    # normalized_output：统一为 LF 换行且只保留一个末尾换行的依赖文本。
    normalized_output = result.stdout.replace("\r\n", "\n").rstrip() + "\n"
    output_path.write_text(normalized_output, encoding="utf-8", newline="\n")

    # package_count：快照中的非空依赖行数量，用于向操作者反馈生成结果。
    package_count = len([line for line in normalized_output.splitlines() if line.strip()])
    print(f"Generated {output_path} with {package_count} packages.")


if __name__ == "__main__":
    main()
