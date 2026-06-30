## Base de Conhecimento
 
> Este projeto **não utiliza a pasta `data` do repositório original** (fork). Em vez disso, a base de conhecimento é construída a partir de **datasets públicos do [Hugging Face](https://huggingface.co/datasets)**, mais adequados ao escopo de educação financeira e personalização por perfil de investidor do Nomad.
 
### Datasets Utilizados
 
| Dataset | Formato | Utilização no Agente |
|---|---|---|
| [`bilalRahib/fiqa-personal-finance-dataset`](https://huggingface.co/datasets/bilalRahib/fiqa-personal-finance-dataset) | Parquet/JSON (pares pergunta-resposta) | Base de conhecimento educativa: fornece respostas de referência sobre orçamento, investimentos e crédito, usadas para fundamentar as explicações do agente e reduzir alucinação |
| [`mitulshah/transaction-categorization`](https://huggingface.co/datasets/mitulshah/transaction-categorization) | Parquet (4,5M+ registros) | Referência para categorizar os gastos informados pelo usuário (ex.: aluguel, alimentação, lazer) em categorias padronizadas, usadas no cálculo do saldo disponível |
 
> [!NOTE]
> O `fiqa-personal-finance-dataset` é derivado do [`FinGPT/fingpt-fiqa_qa`](https://huggingface.co/datasets/FinGPT/fingpt-fiqa_qa), reprocessado para maior coerência em perguntas e respostas de finanças pessoais.
 
### Adaptações nos Dados
 
- **`fiqa-personal-finance-dataset`**: filtrado para manter apenas perguntas/respostas relacionadas a orçamento pessoal, reserva de emergência e conceitos básicos de investimento, removendo conteúdo técnico de mercado financeiro avançado fora do escopo de um público iniciante.
- **`transaction-categorization`**: utilizado apenas o esquema de categorias (ex.: Alimentação, Transporte, Saúde, Lazer, Moradia), não os registros de transações em si, já que os dados financeiros usados pelo agente são exclusivamente os informados pelo próprio usuário em tempo real — nenhum dado de terceiros é misturado ao histórico pessoal do cliente.
### Estratégia de Integração
 
**Como os dados são carregados?**
Os datasets do Hugging Face (perguntas/respostas e categorias de gastos) são carregados uma única vez, na inicialização da aplicação, e ficam disponíveis em memória durante toda a sessão. Os dados financeiros do usuário (renda, gastos, perfil de risco), por sua vez, são coletados dinamicamente a cada interação, dentro da própria conversa — nunca persistidos em base externa.
 
**Como os dados são usados no prompt?**
- A base de conhecimento (FiQA) é consultada dinamicamente: a cada pergunta do usuário, um trecho relevante é recuperado (busca por similaridade) e incluído no contexto enviado ao LLM, no estilo RAG (Retrieval-Augmented Generation).
- Os dados financeiros do próprio usuário (renda, gastos informados na conversa, perfil de risco) são incluídos diretamente no prompt da sessão atual, permitindo respostas personalizadas sem a necessidade de fine-tuning do modelo.
### Exemplo de Contexto Montado
 
```
Dados do Cliente:
- Perfil de risco: Moderado
- Renda mensal: R$ 5.000
 
Gastos informados:
- Aluguel: R$ 1.200
- Alimentação: R$ 800
- Remédios: R$ 150
- Seguro-saúde: R$ 300
- Lazer: R$ 200
 
Saldo disponível no mês: R$ 2.350
 
Trecho recuperado da base de conhecimento (FiQA):
"Uma reserva de emergência idealmente cobre de 3 a 6 meses de despesas
essenciais antes de se considerar investimentos de maior risco."
```
 
---
