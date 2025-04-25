# blue_ocean/visualizer.py
import matplotlib.pyplot as plt
import pandas as pd
import textwrap

def plot_strategy_canvas(factors, companies_data, save_path=None):
    plt.figure(figsize=(16, 9), dpi=300)

    for company, scores in companies_data.items():
        plt.plot(factors, scores, label=company, marker='o')

    plt.title("Canvas Estratégico - Metodologia Blue Ocean")
    plt.xlabel("Fatores-chave de Valor")
    plt.ylabel("Nível de Oferta (0 a 5)")
    plt.ylim(0, 5.5)

    # Numerar os fatores no eixo X
    wrapped_labels = [
        f"{i+1}. " + "\n".join(textwrap.wrap(factor, width=25, max_lines=3, break_long_words=False))
        for i, factor in enumerate(factors)
    ]
    plt.xticks(range(len(factors)), labels=wrapped_labels, rotation=90, ha='center', fontsize=11)

    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def save_strategy_table(factors, companies_data, xlsx_path):
    rows = []
    for company, scores in companies_data.items():
        if isinstance(company, tuple) and len(company) == 2:
            name, url = company
            link = f'=HYPERLINK("{url}", "{name}")'
        else:
            link = company
        rows.append([link] + scores)

    df = pd.DataFrame(rows, columns=["Empresa"] + factors)
    with pd.ExcelWriter(xlsx_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Estratégia")
        worksheet = writer.sheets["Estratégia"]
        worksheet.set_column("A:A", 40)

    return df
