import tempfile
import unittest
from pathlib import Path

import organizador


class OrganizadorTestes(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pasta = Path(self.temp_dir.name)
        self.addCleanup(self.temp_dir.cleanup)

    def listar(self, pasta):
        try:
            return organizador.listar_arquivos(pasta)
        except AttributeError:
            self.fail("organizador.listar_arquivos() ainda não existe")

    def classificar(self, caminho):
        try:
            return organizador.classificar_arquivo(caminho)
        except AttributeError:
            self.fail("organizador.classificar_arquivo() ainda não existe")

    def mover(self, arquivo, pasta_destino):
        try:
            return organizador.mover_arquivo(arquivo, pasta_destino)
        except AttributeError:
            self.fail("organizador.mover_arquivo() ainda não existe")

    def test_listar_arquivos_com_extensoes_diferentes(self):
        (self.pasta / "notas.txt").touch()
        (self.pasta / "script.py").touch()
        (self.pasta / "imagem.png").touch()

        arquivos = self.listar(self.pasta)

        self.assertTrue(all(isinstance(arquivo, Path) for arquivo in arquivos))
        self.assertEqual(
            sorted(arquivo.name for arquivo in arquivos),
            ["imagem.png", "notas.txt", "script.py"],
        )

    def test_listar_arquivos_em_pasta_vazia(self):
        self.assertEqual(self.listar(self.pasta), [])

    def test_listar_arquivos_ignora_subdiretorios(self):
        (self.pasta / "arquivo.py").touch()
        (self.pasta / "subpasta").mkdir()
        (self.pasta / "subpasta" / "dentro.txt").touch()

        arquivos = self.listar(self.pasta)

        self.assertEqual([arquivo.name for arquivo in arquivos], ["arquivo.py"])

    def test_classificar_arquivo_pdf(self):
        self.assertEqual(self.classificar(Path("relatorio.pdf")), "PDFs")

    def test_classificar_arquivo_imagens(self):
        for extensao in (".jpg", ".jpeg", ".png"):
            with self.subTest(extensao=extensao):
                self.assertEqual(
                    self.classificar(Path(f"foto{extensao}")), "Imagens"
                )

    def test_classificar_arquivo_planilhas(self):
        for extensao in (".xls", ".xlsx", ".csv"):
            with self.subTest(extensao=extensao):
                self.assertEqual(
                    self.classificar(Path(f"dados{extensao}")), "Planilhas"
                )

    def test_classificar_arquivo_textos(self):
        for extensao in (".txt", ".doc", ".docx"):
            with self.subTest(extensao=extensao):
                self.assertEqual(
                    self.classificar(Path(f"notas{extensao}")), "Textos"
                )

    def test_classificar_arquivo_extensao_desconhecida(self):
        self.assertEqual(self.classificar(Path("programa.exe")), "Outros")

    def test_classificar_arquivo_sem_extensao(self):
        self.assertEqual(self.classificar(Path("README")), "Outros")

    def test_classificar_arquivo_ignora_caixa_da_extensao(self):
        casos = (
            ("relatorio.PDF", "PDFs"),
            ("foto.JPG", "Imagens"),
            ("foto.JpEg", "Imagens"),
            ("dados.CSV", "Planilhas"),
            ("dados.XlSx", "Planilhas"),
            ("notas.TXT", "Textos"),
            ("notas.DoCx", "Textos"),
        )
        for nome, categoria in casos:
            with self.subTest(nome=nome):
                self.assertEqual(self.classificar(Path(nome)), categoria)

    def test_mover_arquivo_cria_pasta_de_destino_inexistente(self):
        arquivo = self.pasta / "notas.txt"
        arquivo.write_text("conteudo das notas", encoding="utf-8")
        destino = self.pasta / "categorias" / "textos"
        self.assertFalse(destino.exists())

        self.mover(arquivo, destino)

        self.assertTrue(destino.is_dir())

    def test_mover_arquivo_preserva_nome_e_conteudo(self):
        arquivo = self.pasta / "relatorio-final.pdf"
        conteudo = b"conteudo binario do relatorio"
        arquivo.write_bytes(conteudo)
        destino = self.pasta / "destino"
        destino.mkdir()

        self.mover(arquivo, destino)

        movido = destino / "relatorio-final.pdf"
        self.assertFalse(arquivo.exists())
        self.assertTrue(movido.is_file())
        self.assertEqual(movido.read_bytes(), conteudo)

    def test_mover_arquivo_retorna_caminho_final(self):
        arquivo = self.pasta / "notas.txt"
        arquivo.write_text("conteudo", encoding="utf-8")
        destino = self.pasta / "destino"
        destino.mkdir()

        resultado = self.mover(arquivo, destino)

        self.assertIsInstance(resultado, Path)
        self.assertEqual(resultado, destino / "notas.txt")
        self.assertTrue(resultado.is_file())

    def test_mover_arquivo_conflito_levanta_fileexistserror(self):
        origem = self.pasta / "notas.txt"
        origem.write_text("conteudo da origem", encoding="utf-8")
        destino = self.pasta / "destino"
        destino.mkdir()
        existente = destino / "notas.txt"
        existente.write_text("conteudo do destino", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            self.mover(origem, destino)

        self.assertEqual(origem.read_text(encoding="utf-8"), "conteudo da origem")
        self.assertEqual(existente.read_text(encoding="utf-8"), "conteudo do destino")
        self.assertEqual(
            sorted(item.name for item in destino.iterdir()), ["notas.txt"]
        )

    def test_mover_arquivo_origem_inexistente_levanta_filenotfounderror(self):
        origem = self.pasta / "arquivo-inexistente.txt"
        destino = self.pasta / "destino"
        destino.mkdir()

        with self.assertRaises(FileNotFoundError):
            self.mover(origem, destino)

        self.assertEqual(list(destino.iterdir()), [])

    def test_mover_arquivo_destino_existente_nao_e_sobrescrito(self):
        origem = self.pasta / "dados.csv"
        origem.write_text("linha nova", encoding="utf-8")
        destino = self.pasta / "destino"
        destino.mkdir()
        existente = destino / "outro.csv"
        existente.write_text("arquivo alheio", encoding="utf-8")

        self.mover(origem, destino)

        self.assertEqual(
            sorted(item.name for item in destino.iterdir()),
            ["dados.csv", "outro.csv"],
        )
        self.assertEqual(existente.read_text(encoding="utf-8"), "arquivo alheio")
        self.assertEqual(
            (destino / "dados.csv").read_text(encoding="utf-8"), "linha nova"
        )

    def test_mover_arquivo_falha_ao_abrir_origem_preserva_destino_preexistente(self):
        from unittest.mock import patch

        origem = self.pasta / "notas.txt"
        origem.write_text("conteudo da origem", encoding="utf-8")
        destino = self.pasta / "destino"
        destino.mkdir()
        existente = destino / "notas.txt"
        existente.write_text("conteudo do destino", encoding="utf-8")

        abrir_real = organizador.os.open
        tentativas = []

        def abrir_com_falha_na_origem(caminho, flags, *args, **kwargs):
            if Path(caminho) == origem and flags & organizador.os.O_NOFOLLOW:
                tentativas.append(caminho)
                raise OSError("falha simulada ao abrir a origem")
            return abrir_real(caminho, flags, *args, **kwargs)

        with patch.object(organizador.os, "open", abrir_com_falha_na_origem):
            with self.assertRaises(OSError) as contexto:
                organizador.mover_arquivo(origem, destino)

        self.assertEqual(tentativas, [origem])
        self.assertEqual(str(contexto.exception), "falha simulada ao abrir a origem")
        self.assertTrue(origem.is_file())
        self.assertEqual(origem.read_text(encoding="utf-8"), "conteudo da origem")

        try:
            conteudo_destino = existente.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.fail("o arquivo preexistente no destino foi apagado")
        self.assertEqual(conteudo_destino, "conteudo do destino")

    def test_mover_arquivo_falha_na_copia_remove_destino_parcial(self):
        from unittest.mock import patch

        origem = self.pasta / "dados.csv"
        origem.write_text("conteudo original", encoding="utf-8")
        destino = self.pasta / "destino"
        destino.mkdir()
        alheio = destino / "outro.txt"
        alheio.write_text("arquivo alheio", encoding="utf-8")

        tentativas = []

        def copiar_com_falha(fonte, alvo, *args, **kwargs):
            tentativas.append(alvo.name)
            alvo.write(b"bytes parciais")
            raise OSError("falha simulada durante a cópia")

        with patch.object(organizador.shutil, "copyfileobj", copiar_com_falha):
            with self.assertRaises(OSError) as contexto:
                organizador.mover_arquivo(origem, destino)

        self.assertEqual(len(tentativas), 1)
        self.assertEqual(Path(tentativas[0]).name, "dados.csv")
        self.assertEqual(str(contexto.exception), "falha simulada durante a cópia")
        self.assertTrue(origem.is_file())
        self.assertEqual(origem.read_text(encoding="utf-8"), "conteudo original")
        self.assertFalse((destino / "dados.csv").exists())
        self.assertEqual(alheio.read_text(encoding="utf-8"), "arquivo alheio")
        self.assertEqual(
            sorted(item.name for item in destino.iterdir()), ["outro.txt"]
        )

    def test_mover_arquivo_falha_ao_remover_origem_desfaz_copia_no_destino(self):
        from unittest.mock import patch

        origem = self.pasta / "notas.txt"
        origem.write_text("conteudo da origem", encoding="utf-8")
        destino = self.pasta / "destino"
        destino.mkdir()
        alheio = destino / "outro.txt"
        alheio.write_text("arquivo alheio", encoding="utf-8")

        unlink_real = Path.unlink
        tentativas = []

        def unlink_com_falha(caminho, *args, **kwargs):
            if caminho == origem:
                tentativas.append(caminho)
                raise OSError("falha simulada ao remover a origem")
            return unlink_real(caminho, *args, **kwargs)

        with patch.object(Path, "unlink", unlink_com_falha):
            with self.assertRaises(OSError) as contexto:
                organizador.mover_arquivo(origem, destino)

        self.assertEqual(tentativas, [origem])
        self.assertEqual(str(contexto.exception), "falha simulada ao remover a origem")
        self.assertTrue(origem.is_file())
        self.assertEqual(origem.read_text(encoding="utf-8"), "conteudo da origem")
        self.assertFalse((destino / "notas.txt").exists())
        self.assertEqual(alheio.read_text(encoding="utf-8"), "arquivo alheio")
        self.assertEqual(
            sorted(item.name for item in destino.iterdir()), ["outro.txt"]
        )

    def test_mover_arquivo_rejeita_origem_symlink(self):
        alvo = self.pasta / "arquivo-real.txt"
        alvo.write_text("conteudo do arquivo real", encoding="utf-8")
        link = self.pasta / "link.txt"
        try:
            link.symlink_to(alvo)
        except OSError as erro:
            self.skipTest(f"ambiente nao permite criar symlink: {erro}")

        destino = self.pasta / "destino"
        destino.mkdir()

        with self.assertRaises(ValueError):
            self.mover(link, destino)

        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), alvo)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "conteudo do arquivo real")
        self.assertEqual(list(destino.iterdir()), [])

    def test_mover_arquivo_nao_apaga_substituto_colocado_durante_copia(self):
        from unittest.mock import patch

        origem = self.pasta / "notas.txt"
        origem.write_text("conteudo original", encoding="utf-8")
        renomeado = self.pasta / "notas-original.txt"
        destino = self.pasta / "destino"
        destino.mkdir()
        alheio = destino / "outro.txt"
        alheio.write_text("arquivo alheio", encoding="utf-8")

        tentativas = []

        def copiar_com_troca(fonte, alvo, *args, **kwargs):
            tentativas.append(alvo.name)
            origem.rename(renomeado)
            origem.write_text("conteudo do substituto", encoding="utf-8")
            alvo.write(fonte.read())

        with patch.object(organizador.shutil, "copyfileobj", copiar_com_troca):
            with self.assertRaises(RuntimeError) as contexto:
                organizador.mover_arquivo(origem, destino)

        self.assertEqual(len(tentativas), 1)
        self.assertIn("origem", str(contexto.exception))
        self.assertEqual(origem.read_text(encoding="utf-8"), "conteudo do substituto")
        self.assertEqual(renomeado.read_text(encoding="utf-8"), "conteudo original")
        self.assertFalse((destino / "notas.txt").exists())
        self.assertEqual(alheio.read_text(encoding="utf-8"), "arquivo alheio")
        self.assertEqual(sorted(item.name for item in destino.iterdir()), ["outro.txt"])

    def test_mover_arquivo_fileexistserror_durante_copia_remove_destino_parcial(self):
        from unittest.mock import patch

        origem = self.pasta / "dados.csv"
        origem.write_text("conteudo original", encoding="utf-8")
        destino = self.pasta / "destino"
        destino.mkdir()
        alheio = destino / "outro.txt"
        alheio.write_text("arquivo alheio", encoding="utf-8")

        tentativas = []

        def copiar_com_fileexists(fonte, alvo, *args, **kwargs):
            tentativas.append(alvo.name)
            alvo.write(b"bytes parciais")
            raise FileExistsError("falha simulada durante a copia")

        with patch.object(organizador.shutil, "copyfileobj", copiar_com_fileexists):
            with self.assertRaises(FileExistsError) as contexto:
                organizador.mover_arquivo(origem, destino)

        self.assertEqual(len(tentativas), 1)
        self.assertEqual(str(contexto.exception), "falha simulada durante a copia")
        self.assertEqual(origem.read_text(encoding="utf-8"), "conteudo original")
        self.assertFalse((destino / "dados.csv").exists())
        self.assertEqual(alheio.read_text(encoding="utf-8"), "arquivo alheio")
        self.assertEqual(sorted(item.name for item in destino.iterdir()), ["outro.txt"])

    def test_organizar_pasta_distribui_arquivos_por_categoria(self):
        entrada = self.pasta / "entrada"
        entrada.mkdir()
        saida = self.pasta / "saida"
        saida.mkdir()

        conteudos = {
            "contrato.pdf": "conteudo do contrato",
            "foto.jpg": "conteudo da foto",
            "vendas.xlsx": "conteudo da planilha",
            "notas.txt": "conteudo das notas",
        }
        for nome, conteudo in conteudos.items():
            (entrada / nome).write_text(conteudo, encoding="utf-8")

        try:
            organizador.organizar_pasta(entrada, saida)
        except AttributeError:
            self.fail("organizador.organizar_pasta() ainda não existe")

        esperados = []
        for nome, conteudo in conteudos.items():
            categoria = self.classificar(Path(nome))
            destino = saida / categoria / nome
            self.assertTrue(destino.is_file())
            self.assertEqual(destino.read_text(encoding="utf-8"), conteudo)
            self.assertFalse((entrada / nome).exists())
            esperados.append(f"{categoria}/{nome}")

        self.assertEqual(list(entrada.iterdir()), [])
        self.assertEqual(
            sorted(
                item.relative_to(saida).as_posix()
                for item in saida.rglob("*")
                if item.is_file()
            ),
            sorted(esperados),
        )

    def test_organizar_pasta_simular_nao_altera_arquivos_nem_diretorios(self):
        entrada = self.pasta / "entrada"
        entrada.mkdir()
        saida = self.pasta / "saida"
        self.assertFalse(saida.exists())

        conteudos = {
            "contrato.pdf": "conteudo do contrato",
            "foto.jpg": "conteudo da foto",
            "notas.txt": "conteudo das notas",
        }
        for nome, conteudo in conteudos.items():
            (entrada / nome).write_text(conteudo, encoding="utf-8")

        alheio = self.pasta / "alheio.bin"
        alheio.write_text("arquivo alheio", encoding="utf-8")

        try:
            organizador.organizar_pasta(entrada, saida, simular=True)
        except TypeError as erro:
            self.fail(f"organizar_pasta() ainda não aceita simular=True: {erro}")

        for nome, conteudo in conteudos.items():
            arquivo = entrada / nome
            self.assertTrue(arquivo.is_file())
            self.assertEqual(arquivo.read_text(encoding="utf-8"), conteudo)

        self.assertFalse(saida.exists())
        self.assertEqual(alheio.read_text(encoding="utf-8"), "arquivo alheio")
        self.assertEqual(
            sorted(item.name for item in self.pasta.iterdir()),
            ["alheio.bin", "entrada"],
        )

    def test_gerar_relatorio_simulacao_apresenta_arquivos_e_categorias(self):
        entrada = self.pasta / "entrada"
        entrada.mkdir()
        saida = self.pasta / "saida"

        conteudos = {
            "contrato.pdf": "conteudo do contrato",
            "foto.jpg": "conteudo da foto",
            "notas.txt": "conteudo das notas",
        }
        for nome, conteudo in conteudos.items():
            (entrada / nome).write_text(conteudo, encoding="utf-8")

        try:
            relatorio = organizador.gerar_relatorio_simulacao(entrada, saida)
        except AttributeError:
            self.fail("organizador.gerar_relatorio_simulacao() ainda não existe")

        self.assertIsInstance(relatorio, str)
        self.assertIn("SIMULAÇÃO", relatorio)
        self.assertRegex(relatorio, r"\b3\b")
        for nome in conteudos:
            self.assertIn(nome, relatorio)
            self.assertIn(self.classificar(Path(nome)), relatorio)

        self.assertFalse(saida.exists())
        for nome, conteudo in conteudos.items():
            self.assertEqual((entrada / nome).read_text(encoding="utf-8"), conteudo)

    def test_cli_simular_apresenta_relatorio_sem_alterar_arquivos(self):
        import subprocess
        import sys

        entrada = self.pasta / "entrada"
        entrada.mkdir()
        saida = self.pasta / "saida"

        conteudos = {
            "contrato.pdf": "conteudo do contrato",
            "foto.jpg": "conteudo da foto",
        }
        for nome, conteudo in conteudos.items():
            (entrada / nome).write_text(conteudo, encoding="utf-8")

        script = Path(__file__).resolve().parent / "organizador.py"
        resultado = subprocess.run(
            [
                sys.executable,
                str(script),
                "--entrada",
                str(entrada),
                "--saida",
                str(saida),
                "--simular",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("SIMULAÇÃO", resultado.stdout)
        self.assertRegex(resultado.stdout, r"\b2\b")
        for nome in conteudos:
            self.assertIn(nome, resultado.stdout)
            self.assertIn(self.classificar(Path(nome)), resultado.stdout)

        self.assertFalse(saida.exists())
        for nome, conteudo in conteudos.items():
            self.assertEqual((entrada / nome).read_text(encoding="utf-8"), conteudo)

    def test_cli_execucao_real_organiza_arquivos_sem_simular(self):
        import subprocess
        import sys

        entrada = self.pasta / "entrada"
        entrada.mkdir()
        saida = self.pasta / "saida"

        conteudos = {
            "contrato.pdf": "conteudo do contrato",
            "foto.jpg": "conteudo da foto",
            "notas.txt": "conteudo das notas",
        }
        for nome, conteudo in conteudos.items():
            (entrada / nome).write_text(conteudo, encoding="utf-8")

        script = Path(__file__).resolve().parent / "organizador.py"
        resultado = subprocess.run(
            [
                sys.executable,
                str(script),
                "--entrada",
                str(entrada),
                "--saida",
                str(saida),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertEqual(resultado.returncode, 0)
        for nome, conteudo in conteudos.items():
            categoria = self.classificar(Path(nome))
            destino = saida / categoria / nome
            self.assertTrue(destino.is_file())
            self.assertEqual(destino.read_text(encoding="utf-8"), conteudo)
            self.assertFalse((entrada / nome).exists())
