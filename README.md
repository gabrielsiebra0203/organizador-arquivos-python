# Organizador de Arquivos

Projeto de estudo da Aula 06: um organizador que lê uma pasta de entrada, classifica cada arquivo pela extensão e o move para uma subpasta da pasta de saída correspondente à sua categoria. Também oferece um modo de simulação que apenas mostra o que seria feito.

Repositório: https://github.com/gabrielsiebra0203/organizador-arquivos-python

## Funcionalidades

- Listagem dos arquivos presentes diretamente na pasta de entrada, ignorando subdiretórios.
- Classificação por extensão, com comparação que ignora diferenças entre maiúsculas e minúsculas.
- Categorias suportadas: `PDFs`, `Imagens`, `Planilhas`, `Textos` e `Outros` (detalhes em `Categorias suportadas`).
- Organização em subpastas dentro da pasta de saída, uma por categoria.
- Proteção contra sobrescrita: a criação do arquivo de destino é exclusiva. Se já existir arquivo com o mesmo nome no destino, a operação falha com `FileExistsError` e os arquivos envolvidos são preservados.
- Modo de simulação com relatório textual: apresenta `nome -> categoria` para cada arquivo e o total identificado, sem alterar arquivos ou diretórios.
- Interface de linha de comando com `argparse`, por meio de `--entrada`, `--saida` e `--simular`, protegida por `if __name__ == "__main__":`.

## Instalação

```bash
git clone https://github.com/gabrielsiebra0203/organizador-arquivos-python.git
cd organizador-arquivos-python
python3 -m unittest -v
```

## Tecnologias

- Python 3, exclusivamente com a biblioteca padrão
- `pathlib.Path` para caminhos
- `argparse` para a interface de linha de comando
- `os`, `shutil`, `stat` e `errno` na movimentação segura de arquivos
- `unittest`, `tempfile` e `unittest.mock` nos testes

Não há dependências de terceiros.

## Estrutura de arquivos

- `.gitignore` — regras que ignoram caches, ambientes virtuais e diretórios locais de dados.
- `organizador.py` — funções `listar_arquivos`, `classificar_arquivo`, `mover_arquivo`, `organizar_pasta` e `gerar_relatorio_simulacao`, além da CLI protegida por `if __name__ == "__main__":`.
- `test_organizador.py` — 27 testes `unittest` cobrindo listagem, classificação, movimentação, rollback, simulação, relatório e CLI.
- `config.py` — arquivo vazio; o programa não lê configurações.
- `README.md` — este documento.

Os diretórios `entrada/`, `saida/`, `logs/` e `__pycache__/` são locais e ignorados pelo Git conforme a configuração de `.gitignore`. `__pycache__/` é gerado automaticamente pelo Python; os demais são usados apenas como dados ou artefatos locais e não fazem parte do código-fonte.

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
- Ambiente compatível com os recursos de sistema utilizados, em especial `os.O_NOFOLLOW`; o desenvolvimento e os testes foram feitos em Linux.
- Nenhuma biblioteca externa.

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

A saída padrão recebe um relatório iniciado com `SIMULAÇÃO`, com uma linha `nome -> categoria` por arquivo e o total de arquivos identificados. Nenhum arquivo ou diretório é criado, alterado ou removido.

O relatório apenas prevê a classificação com base nos arquivos da entrada: ele não valida conflitos no destino nem garante sucesso na escrita.

### Execução real

```bash
python3 organizador.py --entrada <pasta_de_entrada> --saida <pasta_de_saida>
```

Sem `--simular`, os arquivos são movidos para `<pasta_de_saida>/<categoria>/`, preservando nome e conteúdo. Se já existir um arquivo com o mesmo nome na pasta de destino, a operação falha com `FileExistsError`: o arquivo existente e o arquivo de origem são preservados. A execução real não imprime mensagem de sucesso.

A execução real **movimenta arquivos**. Teste primeiro com diretórios descartáveis, por exemplo:

```bash
tmp=$(mktemp -d)
mkdir "$tmp/entrada"
printf 'conteudo' > "$tmp/entrada/notas.txt"
python3 organizador.py --entrada "$tmp/entrada" --saida "$tmp/saida" --simular
python3 organizador.py --entrada "$tmp/entrada" --saida "$tmp/saida"
```

## Limitações

- O lote não é transacional: uma falha pode interromper a organização depois que alguns arquivos já foram movidos.
- A movimentação não é totalmente atômica: existe uma janela entre a verificação de identidade do arquivo e a remoção da origem.
- A proteção contra condições de corrida é parcial: `O_NOFOLLOW` cobre apenas o componente final do caminho, não diretórios ancestrais.
- Permissões e timestamps não são preservados pela rotina de movimentação.
- O relatório de simulação não garante que a movimentação futura terá sucesso.
- Não há logs, gravação de relatório em disco, tratamento especial de conflitos em lote nem opções de CLI além de `--entrada`, `--saida` e `--simular`.

## Autor

Gabriel Braga Siebra — https://github.com/gabrielsiebra0203/organizador-arquivos-python
