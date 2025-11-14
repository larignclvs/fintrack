# Relatório de Testes de Mutação (mutmut)

Data: 14 de novembro de 2025

Módulos alvo executados (tentativa):
- `src/services/user_service.py`
- `src/services/transaction_service.py`
- `src/controllers/api.py`

Comandos executados

1. Verifiquei que o pacote `mutmut` está instalado (via `requirements.txt`).
2. Rodei a suíte de testes para garantir linha de base:

```bash
PYTHONPATH="$(pwd)" python3 -m pytest -q
```

Resultado: 92 testes passando (suíte completa) — ambiente apto para mutação.

3. Executei o mutmut no workspace (execução padrão, 4 workers):

```bash
mutmut run --max-children 4
```

Resumo dos resultados

- Mutantes gerados (lista total encontrada): 184 (extraída do relatório `mutmut results`).
- Mutantes verificados (checados): 0
- Mutantes mortos (killed): 0
- Mutantes sobreviventes (survived): 0
- Mutantes não verificados / not checked: 184

Interpretação

- O `mutmut` gerou mutantes para os módulos alvo, porém **nenhum mutante foi efetivamente testado** (todos aparecem como `not checked`).
- Durante a fase de execução, o `mutmut` reportou "FAILED: Unable to force test failures" em uma das tentativas de forçar testes falharem para um subconjunto de mutantes. Isso normalmente indica que o runner (pytest) ou a configuração do ambiente dentro do sandbox que o mutmut cria impediu a execução isolada/forçada dos testes sobre os módulos mutados.

Possíveis causas

- Uso de recursos que dependem de estado global ou inicialização atípica (por exemplo, inicialização do banco de dados via `init_db()` no startup do FastAPI) — mutmut copia o projeto para um diretório temporário e tenta executar testes lá; se o código assume paths/arquivos/variáveis de ambiente de forma rígida pode falhar silenciosamente.
- O runner usado por mutmut aqui invoca `pytest` no diretório temporário; se há hooks, fixtures que usam `tmp_path` ou `TestClient` com banco `:memory:` ou file-backed DB diferente, mutmut pode não conseguir reproduzir as mesmas condições.
- Mutantes em partes pequenas do código podem ter sido gerados mas marcados `not checked` porque o test runner terminou anormalmente ou mutmut não conseguiu mapear quais testes exercitariam aquele trecho (por exemplo, mutants em funções que não são importadas no fluxo normal dos testes).

Recomendações e próximos passos

1. Reexecutar com maior verbosidade para diagnosticar por que os mutantes não foram checados:

```bash
mutmut run --max-children 2
mutmut results > mutmut_raw.txt
mutmut show --path <mutant-name>
```

2. Tentar limitar mutações a um único módulo para isolar problemas;

3. Ajustar o ambiente para mutmut:
- Garantir que qualquer inicialização global (ex.: `init_db()`) possa executar no diretório temporário do mutmut. Use variáveis de ambiente (por exemplo `DATABASE_URL`) em fixtures para apontar para um arquivo temporário (`tmp_path`).
- Evitar dependências externas que não sejam re-criáveis no ambiente mutado (por exemplo, remover uso de arquivos com caminhos absolutos durante os testes).

4. Executar mutmut com a flag `--tests-dir` apontando para `tests` (se necessário) ou usar `mutmut run <mutant-names>` para re-testar mutantes selecionados manualmente.

5. Priorizar escrita de testes que cubram melhor os caminhos de negócio nas funções com mutantes `not checked` — em particular `transaction_service.create_transaction` e `user_service` (validações) para aumentar chance de matar mutantes.

Conclusão provisória

O processo de mutação foi iniciado e mutantes foram gerados, mas a execução não checou nenhum mutante (todos estão como `not checked`). Para produzir métricas úteis (taxa de mutantes mortos), preciso iterar na configuração do ambiente de testes para que o runner usado pelo mutmut consiga rodar e executar os testes sobre os módulos instrumentados. Posso fazer isso para você: sugerimos começar isolando um módulo (por exemplo `src/services/user_service.py`) e reexecutar mutmut com ajustes nas fixtures e variáveis de ambiente — quer que eu proceda com essa abordagem e tente matar mutantes do `user_service` primeiro?

FIM
