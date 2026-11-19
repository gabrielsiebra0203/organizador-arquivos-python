import argparse
import errno
import os
import shutil
import stat
from pathlib import Path


CATEGORIAS = {
    ".pdf": "PDFs",
    ".jpg": "Imagens",
    ".jpeg": "Imagens",
    ".png": "Imagens",
    ".xls": "Planilhas",
    ".xlsx": "Planilhas",
    ".csv": "Planilhas",
    ".txt": "Textos",
    ".doc": "Textos",
    ".docx": "Textos",
}


def listar_arquivos(pasta: Path) -> list[Path]:
    return [item for item in Path(pasta).iterdir() if item.is_file()]


def classificar_arquivo(caminho: Path) -> str:
    return CATEGORIAS.get(Path(caminho).suffix.lower(), "Outros")


def mover_arquivo(arquivo: Path, pasta_destino: Path) -> Path:
    origem = Path(arquivo)
    pasta = Path(pasta_destino)
    if not origem.is_file():
        raise FileNotFoundError(origem)

    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / origem.name

    criado = False
    try:
        try:
            descritor = os.open(origem, os.O_RDONLY | os.O_NOFOLLOW)
        except OSError as erro:
            if erro.errno == errno.ELOOP:
                raise ValueError(f"origem é um link simbólico: {origem}") from erro
            raise
        identidade = os.fstat(descritor)
        try:
            fonte = os.fdopen(descritor, "rb")
        except BaseException:
            os.close(descritor)
            raise
        with fonte:
            with destino.open("xb") as alvo:
                criado = True
                shutil.copyfileobj(fonte, alvo)
        try:
            atual = os.stat(origem, follow_symlinks=False)
        except OSError as erro:
            raise RuntimeError(f"origem desapareceu durante a cópia: {origem}") from erro
        if stat.S_ISLNK(atual.st_mode) or (atual.st_dev, atual.st_ino) != (
            identidade.st_dev,
            identidade.st_ino,
        ):
            raise RuntimeError(f"origem foi substituída durante a cópia: {origem}")
        origem.unlink()
    except BaseException as erro:
        if criado:
            try:
                destino.unlink(missing_ok=True)
            except OSError as erro_limpeza:
                erro.add_note(f"falha ao remover destino criado: {erro_limpeza}")
        raise

    return destino


def organizar_pasta(entrada: Path, saida: Path, simular: bool = False) -> None:
    for arquivo in listar_arquivos(entrada):
        categoria = classificar_arquivo(arquivo)
        if not simular:
            mover_arquivo(arquivo, Path(saida) / categoria)


def gerar_relatorio_simulacao(entrada: Path, saida: Path) -> str:
    arquivos = listar_arquivos(entrada)
    linhas = ["SIMULAÇÃO"]
    for arquivo in arquivos:
        linhas.append(f"{arquivo.name} -> {classificar_arquivo(arquivo)}")
    linhas.append(f"Total: {len(arquivos)} arquivos")
    return "\n".join(linhas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entrada", required=True)
    parser.add_argument("--saida", required=True)
    parser.add_argument("--simular", action="store_true")
    argumentos = parser.parse_args()

    if argumentos.simular:
        print(gerar_relatorio_simulacao(Path(argumentos.entrada), Path(argumentos.saida)))
    else:
        organizar_pasta(Path(argumentos.entrada), Path(argumentos.saida))
