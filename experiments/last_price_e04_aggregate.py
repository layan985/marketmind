from pathlib import Path

SOURCE = Path("experiments/last_price_e03_aggregate.py")
text = SOURCE.read_text()
text = text.replace(
    "last-price-e03-trade-welfare-20260810",
    "last-price-e04-trade-welfare-replication-20260810",
)
text = text.replace("e03_summary.json", "e04_summary.json")
text = text.replace("Last Price E03", "Last Price E04")
text = text.replace("E03_REPORT.md", "E04_REPORT.md")

namespace = {
    "__name__": "e04_frozen_analysis_runtime",
    "__file__": str(SOURCE),
}
exec(compile(text, str(SOURCE), "exec"), namespace)
namespace["main"]()
