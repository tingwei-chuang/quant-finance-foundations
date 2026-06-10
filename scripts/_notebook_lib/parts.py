"""Reusable section builders shared by every week module.

Each helper returns one or more ``NotebookNode`` cells in the standard layout
described in the roadmap: header, style setup, body (per-week), exercises,
mistakes, checklist, references.
"""

from __future__ import annotations

import nbformat as nbf

from .cells import code, md


def docs_prefix(solution: bool) -> str:
    """Return the relative prefix to ``docs/`` from a notebook directory.

    Main notebooks live in ``notebooks/``; solution notebooks live one level
    deeper in ``notebooks/solutions/`` and therefore need an extra ``..``.
    """
    return "../../docs/" if solution else "../docs/"


def style_setup_cell() -> nbf.NotebookNode:
    """Emit a one-time setup cell: CJK fonts, sign rendering, deterministic look.

    Without this most matplotlib installs render Chinese titles as tofu boxes
    and emit a flood of "missing glyph" warnings.
    """
    return code(
        "# 教學樣式設定（CJK 字型、負號正常顯示、固定隨機種子）\n"
        "import matplotlib as _mpl\n"
        "_mpl.rcParams['font.sans-serif'] = [\n"
        "    'PingFang TC', 'Heiti TC', 'Microsoft JhengHei',\n"
        "    'Noto Sans CJK TC', 'Noto Sans TC',\n"
        "    'WenQuanYi Zen Hei', 'Source Han Sans TC',\n"
        "    'Arial Unicode MS', 'DejaVu Sans',\n"
        "]\n"
        "_mpl.rcParams['axes.unicode_minus'] = False\n"
        "_mpl.rcParams['figure.figsize'] = (8.5, 4.5)\n"
        "_mpl.rcParams['savefig.dpi'] = 100\n"
        "import numpy as _np\n"
        "_np.random.seed(0)  # belt-and-braces; library functions take explicit seeds"
    )


def header(
    *,
    solution: bool,
    week: str,
    title: str,
    objectives: list[str],
    hours: str,
    prereqs: list[str],
    resources: list[tuple[str, str]],
) -> list[nbf.NotebookNode]:
    """Return the standard opening cells shared by every notebook."""
    obj = "\n".join(f"- {o}" for o in objectives)
    pre = "\n".join(f"- {p}" for p in prereqs)
    res = "\n".join(f"- [{name}]({url})" for name, url in resources)
    res_block = res if resources else "- （本週為環境設定，無外部資源）"
    _ = solution  # reserved for future per-version header changes
    return [
        md(
            f"# {week} — {title}\n\n"
            "> 本 notebook 屬於「量化數學路線圖」（quant-math-roadmap）開源教學專案。\n"
            "> 僅供**教育與研究方法論**用途，**不構成投資建議**，任何結果都不代表"
            "實際可獲利或可投資的策略。"
        ),
        md(
            "## 學習目標\n\n"
            f"{obj}\n\n"
            "## 預估學習時間\n\n"
            f"約 {hours}。\n\n"
            "## 先備概念\n\n"
            f"{pre}\n\n"
            "## 外部學習資源\n\n"
            f"{res_block}\n\n"
            "> 外部資源僅供參考連結；本專案不重製任何受版權保護的課程材料。"
        ),
        style_setup_cell(),
    ]


def footer_references(solution: bool) -> nbf.NotebookNode:
    """Return the standard closing 'references and disclaimer' cell."""
    p = docs_prefix(solution)
    return md(
        "## 參考與致謝\n\n"
        "- 本 notebook 的所有解說、範例與習題皆為本專案**原創**撰寫。\n"
        f"- 推薦的外部學習資源請見 [`docs/resources.md`]({p}resources.md)。\n"
        f"- 數學與財務概念筆記請見 [`docs/math/`]({p}math/) 與 "
        f"[`docs/finance/`]({p}finance/)。\n\n"
        "### 隱私與免責聲明\n\n"
        "- 本 notebook 不含任何真實個人資訊。\n"
        "- 本 notebook 僅使用可重現的合成資料，不需要網路連線。\n"
        "- 本 notebook 不對任何策略做出實際投資獲利的宣稱。"
    )


def checklist(items: list[str]) -> nbf.NotebookNode:
    """Return the 'what you should be able to do' checklist cell."""
    body = "\n".join(f"- [ ] {i}" for i in items)
    return md("## 完成本週後，你應該能做到什麼\n\n" + body)


def mistakes(items: list[str]) -> nbf.NotebookNode:
    """Return the common-mistakes cell."""
    body = "\n".join(f"- **{i}**" for i in items)
    return md("## 常見錯誤\n\n" + body)


def exercises_intro() -> nbf.NotebookNode:
    """Return the exercises section heading."""
    return md(
        "## 練習\n\n"
        "請依序完成以下練習。**基礎練習**鞏固定義，**應用練習**動手寫程式，"
        "**反思問題**把數學連結到回測與研究方法論。\n\n"
        "> 主 notebook 的程式練習提供可執行的起始碼（starter）。完整參考解答請見 "
        "`notebooks/solutions/` 對應的 `_solution` notebook。"
    )
