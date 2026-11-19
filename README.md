# Organizador de Arquivos

Projeto de estudo da Aula 06: um organizador que lê uma pasta de entrada, classifica cada arquivo pela extensão e o move para uma subpasta da pasta de saída correspondente à sua categoria. Também oferece um modo de simulação que apenas mostra o que seria feito.

## Tecnologias

- Python 3, exclusivamente com a biblioteca padrão
- `pathlib.Path` para caminhos
- `argparse` para a interface de linha de comando
- `os`, `shutil`, `stat` e `errno` na movimentação segura de arquivos
- `unittest`, `tempfile` e `unittest.mock` nos testes

Não há dependências de terceiros e nada precisa ser instalado.

## Estrutura de arquivos

- `organizador.py` — funções `listar_arquivos`, `classificar_arquivo`, `mover_arquivo`, `organizar_pasta` e `gerar_relatorio_simulacao`, além da CLI protegida por `if __name__ == "__main__":`.
- `test_organizador.py` — 27 testes `unittest` cobrindo listagem, classificação, movimentação, rollback, simulação, relatório e CLI.
- `config.py` — arquivo vazio; o programa não lê configurações.
- `README.md` — este documento.

O diretório `__pycache__/` é gerado automaticamente pelo Python e não faz parte do código-fonte.

## Categorias suportadas

| Categoria | Extensões |
| --- | --- |
| `PDFs` | `.pdf` |
| `Imagens` | `.jpg`, `.jpeg`, `.png` |
| `Planilhas` | `.xls`, `.xlsx`, `.csv` |
| `Textos` | `.txt`, `.doc`, `.docx` |
| `Outros` | qualquer outra extensão ou arquivo sem extensão |

A classificação ignora diferenças entre maiúsculas e minúsculas. São considerados apenas os arquivos presentes diretamente na pasta de entrada; subdiretórios são ignorados.

## Requisitos

- Python 3.11 ou superior (o código usa `BaseException.add_note()`).
- Ambiente com `os.O_NOFOLLOW` disponível; o desenvolvimento e os testes foram feitos em Linux.
- Nenhum pacote adicional.

## Execução dos testes

No diretório que contém `organizador.py`:

```bash
python3 -m unittest -v
```

A suíte deve terminar com `Ran 27 tests` e `OK`.

## Uso da CLI

### Simulação

```bash
python3 organizador.py --entrada <pasta_de_entrada> --saida <pasta_de_saida> --simular
```

A saída padrão recebe um relatório iniciado com `SIMULAÇÃO`, com uma linha `nome -> categoria` por arquivo e o total de arquivos identificados. Nenhum arquivo ou diretório é criado, alterado ou removido. O relatório é uma previsão baseada no estado atual da entrada.

### Execução real

```bash
python3 organizador.py --entrada <pasta_de_entrada> --saida <pasta_de_saida>
```

Sem `--simular`, os arquivos são movidos para `<pasta_de_saida>/<categoria>/`, preservando nome e conteúdo. A execução real não imprime mensagem de sucesso.

A execução real **movimenta arquivos**. Teste primeiro com diretórios descartáveis, por exemplo:

```bash
tmp=$(mktemp -d)
mkdir "$tmp/entrada"
printf 'conteudo' > "$tmp/entrada/notas.txt"
python3 organizador.py --entrada "$tmp/entrada" --saida "$tmp/saida" --simular
python3 organizador.py --entrada "$tmp/entrada" --saida "$tmp/saida"
```

## Limitações

- A movimentação não é totalmente atômica: existe uma janela entre a verificação de identidade do arquivo e a remoção da origem.
- O lote não é transacional: uma falha pode interromper a organização depois que alguns arquivos já foram movidos.
- A proteção contra condições de corrida é parcial: `O_NOFOLLOW` cobre apenas o componente final do caminho, não diretórios ancestrais.
- O relatório de simulação não garante que a movimentação futura terá sucesso.
- Permissões e timestamps não são preservados pela rotina de movimentação.
- Não há logs, gravação de relatório em disco, tratamento especial de conflitos em lote nem opções de CLI além de `--entrada`, `--saida` e `--simular`.
