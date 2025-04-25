OPENAI_API_KEY  = "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"

# blue_ocean/analyzer.py

import openai

# Ajuste sua chave de API da OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def extract_value_factors(company_snippets):
    if not isinstance(company_snippets, dict) or not company_snippets:
        raise ValueError("Formato inválido para company_snippets")

    snippets = []
    for name, snippet in company_snippets.items():
        if isinstance(snippet, str):
            snippet_clean = snippet.strip().replace("\n", " ").strip()
            snippets.append(f"Empresa: {name}\nResumo: {snippet_clean[:3000]}")
        else:
            raise ValueError(f"O resumo da empresa '{name}' deve ser um texto.")

    prompt = (
        "Baseado nos resumos abaixo, identifique e liste até 10 fatores-chave de valor "
        "(um por linha, curtos e objetivos):\n\n"
    )
    prompt += "\n\n".join(snippets)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    factors = [line.strip("- ").strip() for line in content.split("\n") if line.strip()]

    return factors


