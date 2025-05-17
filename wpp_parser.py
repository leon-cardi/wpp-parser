import re
from collections import defaultdict
import markdown2
from weasyprint import HTML
from google.colab import files

class WhatsAppParser:
    """
    Classe para parsear mensagens brutas do WhatsApp e gerar saídas em markdown e PDF.
    """
    TIMESTAMP_PATTERN = re.compile(
        r"\[(?P<hora>\d{2}:\d{2}), (?P<data>\d{2}/\d{2}/\d{4})\]\s*"
        r"[^:]+:\s*"
        r"(?P<mensagem>.*?)(?=(?:\[\d{2}:\d{2}, \d{2}/\d{2}/\d{4}\])|$)",
        re.DOTALL
    )

    def __init__(self, raw_text: str = None):
        """
        Inicializa o parser. Se raw_text for fornecido, já realiza o parse.
        """
        self.raw_text = raw_text
        self.messages = {}
        if raw_text is not None:
            self.parse(raw_text)

    def parse(self, raw_text: str) -> dict:
        """
        Parseia o texto bruto e agrupa mensagens por data.
        Retorna um dict onde cada chave é 'DD/MM/YYYY' e o valor
        é uma lista de tuplas (hora, mensagem).
        """
        agrupado = defaultdict(list)
        for match in self.TIMESTAMP_PATTERN.finditer(raw_text):
            hora = match.group('hora')
            data = match.group('data')
            mensagem = match.group('mensagem').strip()
            agrupado[data].append((hora, mensagem))
        self.messages = dict(agrupado)
        return self.messages

    def load_from_file(self, file_path: str, encoding: str = 'utf-8') -> dict:
        """
        Lê um arquivo .txt e parseia seu conteúdo.
        Retorna o mesmo formato de dict de parse().
        """
        with open(file_path, 'r', encoding=encoding) as f:
            text = f.read()
        return self.parse(text)

    def to_markdown(self) -> str:
        """
        Converte as mensagens parseadas em um documento Markdown estruturado.
        """
        if not self.messages:
            return ""
        md_lines = []
        for data, msgs in self.messages.items():
            md_lines.append(f"## {data}")
            for hora, mensagem in msgs:
                md_lines.append(f"- **{hora}**")
                # indent message text
                for line in mensagem.splitlines():
                    md_lines.append(f"  {line}")
            md_lines.append("")
        return "\n".join(md_lines)

    def export_markdown(self, output_path: str, encoding: str = 'utf-8'):
        """
        Salva o Markdown gerado em um arquivo .md.
        """
        md = self.to_markdown()
        with open(output_path, 'w', encoding=encoding) as f:
            f.write(md)

    def export_pdf(self, output_path: str, title: str = None):
        """
        Exporta o documento Markdown como PDF.
        Requer markdown2 e weasyprint.
        """
        md = self.to_markdown()
        # Converter markdown para HTML
        html_body = markdown2.markdown(md)
        # Construir HTML completo
        html = '<html><head>'
        if title:
            html += f"<title>{title}</title>"
        html += '</head><body>' + html_body + '</body></html>'
        # Gerar PDF
        HTML(string=html).write_pdf(output_path)

    def pretty_print(self):
        """
        Imprime as mensagens agrupadas por data no formato:
            === DD/MM/YYYY ===
            [HH:MM]
            Mensagem...
        """
        if not self.messages:
            print("Nenhuma mensagem para exibir.")
            return
        for data, msgs in self.messages.items():
            print(f"=== {data} ===")
            for hora, mensagem in msgs:
                print(f"[{hora}]")
                print(f"{mensagem}\n")
