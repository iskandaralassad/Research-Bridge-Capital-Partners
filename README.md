# Agente de Research — Bridge Capital Partners

Este projeto contém 3 newsletters automatizadas:

| Newsletter            | Frequência        | Conteúdo                                                                 |
|------------------------|--------------------|---------------------------------------------------------------------------|
| Daily News             | Todo dia           | Resumo do dia focado exclusivamente em AI (mercado, corporate, investimentos, política/regulação), com links |
| Investment Trends      | Toda sexta-feira   | Rodadas de investimento em empresas de AI na semana, teses e tendências   |
| Fundraising Trends     | Toda sexta-feira   | Atividade de alocadores (family offices, FoF, DFIs, SWFs) na semana — não restrita a AI, a menos que solicitado |

Cada uma é gerada por um script Python que chama a API da Anthropic (Claude)
com a ferramenta de busca na web habilitada, e envia o resultado por e-mail
via a caixa corporativa Outlook/Office 365.

---

## 1. Passo a passo de configuração

### 1.1. Conta e chave da API Anthropic
1. Crie/acesse uma conta em https://console.anthropic.com
2. Gere uma API key em **Settings > API Keys**.
3. Guarde essa chave — ela vai virar o secret `ANTHROPIC_API_KEY`.

Consulte https://docs.claude.com para detalhes de billing e limites de uso.

### 1.2. Caixa de e-mail dedicada (recomendado)
Crie uma caixa de e-mail dedicada no Outlook/Office 365 da Bridge Capital,
ex: `research@bridgecapital.com`, em vez de usar o e-mail pessoal de alguém.

Você (ou o time de TI) precisa:
1. Confirmar que **SMTP AUTH** está habilitado para essa caixa (em tenants
   Microsoft 365 mais recentes, isso vem desabilitado por padrão e precisa ser
   ativado pelo admin no Exchange Admin Center).
2. Gerar uma **senha de aplicativo** (app password) para essa caixa, caso MFA
   esteja ativado — isso é feito no portal de segurança da conta Microsoft.

**Alternativa (se SMTP AUTH básico estiver bloqueado pela política do tenant):**
usar a Microsoft Graph API com um App Registration no Azure AD e OAuth2
client-credentials para enviar o e-mail via `/users/{id}/sendMail`. Isso exige
suporte do time de TI para criar o App Registration com a permissão
`Mail.Send`. Se precisar, posso montar essa variante do `email_sender.py`.

### 1.3. Repositório GitHub (para agendamento via GitHub Actions)
1. Crie um repositório **privado** no GitHub da organização.
2. Suba todos os arquivos desta pasta para o repositório.
3. Vá em **Settings > Secrets and variables > Actions** e cadastre:
   - `ANTHROPIC_API_KEY`
   - `EMAIL_ADDRESS` (ex: research@bridgecapital.com)
   - `EMAIL_PASSWORD` (a senha de aplicativo gerada acima)
   - `EMAIL_RECIPIENTS` (lista separada por vírgula, ex:
     `socio1@bridgecapital.com,socio2@bridgecapital.com`)
4. Os workflows em `.github/workflows/` já estão configurados para rodar:
   - `daily-news.yml` → todo dia às 22:00 UTC
   - `friday-newsletters.yml` → toda sexta às 20:00 UTC
   Ajuste o horário (`cron:`) conforme o fuso horário desejado — cron do
   GitHub Actions é sempre em UTC.
5. Para testar sem esperar o agendamento, use a aba **Actions > [workflow] >
   Run workflow** (botão manual, já habilitado via `workflow_dispatch`).

---

## 2. Rodando localmente (para testes antes de subir ao GitHub)

```bash
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-ant-..."
export EMAIL_ADDRESS="research@bridgecapital.com"
export EMAIL_PASSWORD="sua-senha-de-app"
export EMAIL_RECIPIENTS="socio1@bridgecapital.com,socio2@bridgecapital.com"

python daily_news.py
python investment_trends.py
python fundraising_trends.py
```

---

## 3. Estrutura dos arquivos

```
bridge-research-agent/
├── config.py                 # recipients, fontes, modelo, credenciais (via env vars)
├── prompts.py                 # os 3 prompts detalhados (editar aqui para ajustar conteúdo)
├── claude_client.py            # wrapper de chamada à API com web_search
├── email_sender.py             # envio via SMTP Outlook + template HTML
├── daily_news.py                # script executável: Daily News
├── investment_trends.py          # script executável: Investment Trends (sexta)
├── fundraising_trends.py          # script executável: Fundraising Trends (sexta)
├── requirements.txt
└── .github/workflows/
    ├── daily-news.yml            # agenda diária
    └── friday-newsletters.yml     # agenda sexta-feira
```

---

## 4. Como ajustar o conteúdo/formato das newsletters

Todo o "cérebro" de cada newsletter está em `prompts.py`. Para mudar:
- Quais fontes priorizar → edite as listas em `config.py`
  (`PRIMARY_NEWS_SOURCES`, `INVESTMENT_TRENDS_SOURCES`, `FUNDRAISING_TRENDS_SOURCES`).
- Estrutura/seções de cada newsletter → edite a função correspondente em
  `prompts.py` (`daily_news_prompt`, `investment_trends_prompt`,
  `fundraising_trends_prompt`).
- Visual do e-mail (cores, fonte, logo) → edite `EMAIL_TEMPLATE` em
  `email_sender.py`.

---

## 5. Limitações e recomendações importantes

- **Verificação humana**: os prompts instruem o Claude a nunca inventar links,
  valores ou nomes — mas para um material que vai para sócios e possivelmente
  LPs, recomendo uma revisão rápida (2-3 min) antes de considerar 100%
  confiável para uso externo, especialmente no início.
- **Custo de API**: cada newsletter faz múltiplas buscas na web por execução;
  o custo por envio deve ficar na casa de poucos centavos a poucos dólares,
  mas monitore o uso em https://console.anthropic.com nas primeiras semanas.
- **Rate limits**: se notar erros de rate limit nos logs do GitHub Actions,
  pode ser necessário solicitar aumento de limite via console da Anthropic.
- **Fuso horário**: os crons estão em UTC — já ajustei os comentários no YAML,
  mas confirme os horários finais antes de considerar produção.
