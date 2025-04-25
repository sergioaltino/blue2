import streamlit as st
import pandas as pd
from collections import Counter
from blue_ocean.search import crawl_website, infer_company_name_and_sector
from blue_ocean.analyzer import extract_value_factors
from blue_ocean.visualizer import plot_strategy_canvas, save_strategy_table

def score_companies(factors, important_factors):
    import random
    scores = []
    for factor in factors:
        if any(word.lower() in factor.lower() for word in important_factors):
            scores.append(random.randint(3, 5))
        else:
            scores.append(random.randint(0, 2))
    return scores

def main_interface():
    st.set_page_config(page_title="Análise Estratégica Blue Ocean", layout="wide")
    st.title("Agente de Análise Estratégica - Metodologia Blue Ocean")

    principal_url = st.text_input("Digite o link do site da empresa principal (ex: https://exemplo.com)")
    concorrentes_urls = st.text_area("Digite os links dos concorrentes, um por linha:")

    if st.button("Analisar"):
        urls_concorrentes = [url.strip() for url in concorrentes_urls.splitlines() if url.strip()]
        urls = [("Principal", principal_url)] + [(f"Concorrente {i+1}", url) for i, url in enumerate(urls_concorrentes)]

        company_profiles = {}
        site_texts = {}
        factors_counter = Counter()

        progress = st.progress(0)

        for i, (label, url) in enumerate(urls):
            if url:
                site_text = crawl_website(url)
                site_texts[url] = site_text
                name, sector = infer_company_name_and_sector(site_text)
                
                short_text = site_text[:3000]
                extracted_factors = extract_value_factors({"Empresa": short_text})
                
                factors_counter.update(extracted_factors)
                progress.progress((i + 1) / len(urls))

        # Ordenar fatores por frequência e limitar a 20
        factors_final = [factor for factor, count in factors_counter.most_common(7)]

        for label, url in urls:
            if url:
                site_text = site_texts[url]
                name, sector = infer_company_name_and_sector(site_text)
                scores = score_companies(factors_final, factors_final)
                company_profiles[(name, url)] = scores

        st.success("Análise concluída!")

        st.subheader("Canvas Estratégico")
        plot_path = "canvas.png"
        plot_strategy_canvas(factors_final, company_profiles, save_path=plot_path)
        st.image(plot_path, caption="Gráfico Estratégico", use_container_width=True)

        xlsx_path = "estrategia_blue_ocean.xlsx"
        # Inverter dados antes de salvar no Excel
        df_for_xlsx = pd.DataFrame(
            {name: scores for (name, url), scores in company_profiles.items()},
            index=factors_final
        ).reset_index()
        df_for_xlsx.rename(columns={"index": "Fatores"}, inplace=True)

        with pd.ExcelWriter(xlsx_path, engine="xlsxwriter") as writer:
            df_for_xlsx.to_excel(writer, index=False, sheet_name="Estratégia")
            worksheet = writer.sheets["Estratégia"]
            worksheet.set_column("A:A", 40)

        df_xlsx = df_for_xlsx

        # Criar DataFrame simples para visualização
        simple_rows = []
        for (name, url), scores in company_profiles.items():
            simple_rows.append([name] + scores)

        df_simple = pd.DataFrame(simple_rows, columns=["Empresa"] + factors_final)

        # Inverter linhas e colunas para melhor impressão
        df_simple = df_simple.set_index("Empresa").transpose().reset_index()
        df_simple.rename(columns={"index": "Fatores"}, inplace=True)

        st.subheader("Tabela Estratégica")
        st.dataframe(df_simple)

        with open(xlsx_path, "rb") as file:
            st.download_button(
                label="📥 Baixar Estratégia em XLSX",
                data=file,
                file_name="estrategia_blue_ocean.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main_interface()
