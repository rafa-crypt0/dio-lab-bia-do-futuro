"""
financas.py

Funções auxiliares para calcular o saldo disponível do usuário a partir
da renda e dos gastos fixos informados, e montar o bloco de "Dados do
Cliente" usado no contexto enviado ao LLM.
"""

CATEGORIAS_PADRAO = [
    "Aluguel",
    "Alimentação",
    "Remédios",
    "Seguro-saúde",
    "Lazer",
    "Contas",
]


def calcular_saldo(renda: float, gastos: dict) -> float:
    """gastos: dict no formato {"Aluguel": 800, "Alimentação": 500, ...}"""
    total_gastos = sum(gastos.values())
    return round(renda - total_gastos, 2)


def montar_resumo_cliente(renda: float, gastos: dict, perfil: str) -> str:
    """Monta o bloco 'Dados do Cliente' para incluir no prompt do LLM."""
    saldo = calcular_saldo(renda, gastos)

    linhas_gastos = "\n".join(
        f"- {categoria}: R$ {valor:,.2f}" for categoria, valor in gastos.items()
    )

    resumo = f"""Dados do Cliente:
- Perfil de risco: {perfil}
- Renda mensal: R$ {renda:,.2f}

Gastos informados:
{linhas_gastos}

Saldo disponível no mês: R$ {saldo:,.2f}"""

    return resumo
