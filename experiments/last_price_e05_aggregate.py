from pathlib import Path

SOURCE = Path("experiments/last_price_e03_aggregate.py")
text = SOURCE.read_text()
text = text.replace(
    "last-price-e03-trade-welfare-20260810",
    "last-price-e05-trade-welfare-replication-20260811",
)
text = text.replace("e03_summary.json", "e05_summary.json")
text = text.replace("Last Price E03", "Last Price E05")
text = text.replace("E03_REPORT.md", "E05_REPORT.md")

namespace = {
    "__name__": "e05_frozen_analysis_runtime",
    "__file__": str(SOURCE),
}
exec(compile(text, str(SOURCE), "exec"), namespace)
namespace["main"]()
