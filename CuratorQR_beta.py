import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import fitz
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import io
import gc
import time
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD
import ctypes

NOME_MARCA = "CuratorQR"
VERSAO = "v0.2 (Beta)"
AUTORA = "Elise Hirako"
TEXTO_RODAPE = "O software CuratorQR integra o pacote CMT - Cartografia do Movimento por meio de Tecnologias Digitais"

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("green") 

class AppCuratorQR(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # --- JANELA SEM BORDAS + APARECER NA BARRA DE TAREFAS ---
        self.overrideredirect(True) 
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x00040000) 

        self.geometry("650x660+300+100") 
        self.configure(fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC") 

        # --- BARRA DE TÍTULO PERSONALIZADA ---
        self.barra_titulo = ctk.CTkFrame(self, fg_color="#F4F7F6", height=40, corner_radius=0)
        self.barra_titulo.pack(fill="x", side="top")
        
        self.label_c = ctk.CTkLabel(self.barra_titulo, text="CQR", font=("Segoe UI", 20, "bold"), text_color="#800000")
        self.label_c.pack(side="left", padx=(15, 5), pady=5)
        
        self.label_titulo_barra = ctk.CTkLabel(self.barra_titulo, text=f"{NOME_MARCA} {VERSAO} | CMT", font=("Segoe UI", 12), text_color="#555555")
        self.label_titulo_barra.pack(side="left", pady=5)

        self.btn_fechar = ctk.CTkButton(self.barra_titulo, text="X", width=30, height=30, fg_color="transparent", hover_color="#e74c3c", text_color="#555555", font=("Segoe UI", 12, "bold"), command=self.fechar_app)
        self.btn_fechar.pack(side="right", padx=5)

        self.barra_titulo.bind("<Button-1>", self.iniciar_arrasto)
        self.barra_titulo.bind("<B1-Motion>", self.arrastar_janela)
        self.label_c.bind("<Button-1>", self.iniciar_arrasto)
        self.label_c.bind("<B1-Motion>", self.arrastar_janela)
        self.label_titulo_barra.bind("<Button-1>", self.iniciar_arrasto)
        self.label_titulo_barra.bind("<B1-Motion>", self.arrastar_janela)

        if getattr(sys, 'frozen', False):
            pasta_atual = sys._MEIPASS
        else:
            pasta_atual = os.path.dirname(os.path.abspath(__file__))

        # --- LOGO CMT ---
        caminho_imagem = os.path.join(pasta_atual, "logo_cmt.png")
        try:
            img_pil = Image.open(caminho_imagem)
            img_pil.thumbnail((250, 160), Image.Resampling.LANCZOS)
            self.foto_logo = ImageTk.PhotoImage(img_pil)
            self.label_logo = ctk.CTkLabel(self, image=self.foto_logo, text="", fg_color="#FFFFFF")
            self.label_logo.pack(pady=(20, 10))
        except Exception:
            self.label_logo = ctk.CTkLabel(self, text="Erro na logo.", font=("Segoe UI", 11), text_color="red", fg_color="#FFFFFF")
            self.label_logo.pack(pady=(20, 10))

        # --- TÍTULOS ---
        self.label_titulo = ctk.CTkLabel(self, text=NOME_MARCA, font=("Segoe UI", 36, "bold"), text_color="#777777", fg_color="#FFFFFF")
        self.label_titulo.pack(pady=(0, 5))
        self.label_subtitulo = ctk.CTkLabel(self, text="Curadoria Digital e Validação de Referências em QRCode", font=("Segoe UI", 15), text_color="#555555", fg_color="#FFFFFF")
        self.label_subtitulo.pack(pady=(0, 20))

        # --- ÁREA DE ARRASTAR E SOLTAR ---
        self.frame_arquivo = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=2, border_color="#D4A373", corner_radius=10, height=80)
        self.frame_arquivo.pack(pady=10, padx=40, fill="x")
        self.frame_arquivo.pack_propagate(False)
        self.label_arquivo = ctk.CTkLabel(self.frame_arquivo, text="📄 Arraste o PDF aqui ou clique para selecionar", font=("Segoe UI", 13), text_color="#777777", fg_color="#FFFFFF")
        self.label_arquivo.pack(expand=True)

        self.frame_arquivo.drop_target_register(DND_FILES)
        self.frame_arquivo.dnd_bind('<<Drop>>', self.ao_soltar_arquivo)
        self.label_arquivo.bind("<Button-1>", lambda e: self.selecionar_pdf())
        self.frame_arquivo.bind("<Button-1>", lambda e: self.selecionar_pdf())

        # --- BOTÕES ---
        self.btn_selecionar = ctk.CTkButton(self, text="Selecionar Arquivo PDF", command=self.selecionar_pdf, fg_color="#708238", hover_color="#5a6b2d", font=("Segoe UI", 14, "bold"), corner_radius=8)
        self.btn_selecionar.pack(pady=10)
        self.btn_iniciar = ctk.CTkButton(self, text="Iniciar Auditoria", command=self.iniciar_auditoria, state="disabled", fg_color="#2F4F4F", hover_color="#1d3333", font=("Segoe UI", 14, "bold"), corner_radius=8)
        self.btn_iniciar.pack(pady=15)

        # --- STATUS E BARRA ---
        self.label_status = ctk.CTkLabel(self, text="", font=("Segoe UI", 12), text_color="#A33B20", fg_color="#FFFFFF")
        self.label_status.pack(pady=5)
        self.barra_progresso = ctk.CTkProgressBar(self, width=300, progress_color="#D4A373", fg_color="#E0E0E0")
        self.barra_progresso.pack(pady=10)
        self.barra_progresso.pack_forget()

        # --- RODAPÉ ---
        texto_rodape_final = (
            f"© Copyleft - Desenvolvido por {AUTORA} | Uso livre desde que citada a fonte.\n"
            f"{TEXTO_RODAPE}"
        )
        self.label_rodape = ctk.CTkLabel(self, text=texto_rodape_final, font=("Segoe UI", 11), text_color="#999999", justify="center", fg_color="#FFFFFF")
        self.label_rodape.pack(side="bottom", pady=15)

        self.caminho_pdf = None

    def fechar_app(self):
        self.destroy()
        sys.exit()

    def iniciar_arrasto(self, event):
        self.x_offset = event.x
        self.y_offset = event.y

    def arrastar_janela(self, event):
        x = self.winfo_pointerx() - self.x_offset
        y = self.winfo_pointery() - self.y_offset
        self.geometry(f"+{x}+{y}")

    def ao_soltar_arquivo(self, event):
        caminho = event.data.strip('{}')
        if caminho.lower().endswith('.pdf'):
            self.caminho_pdf = caminho
            nome = os.path.basename(caminho)
            self.label_arquivo.configure(text=f"📄 {nome}", text_color="#2F4F4F")
            self.btn_iniciar.configure(state="normal")
        else:
            messagebox.showwarning("Formato Inválido", "Por favor, arraste apenas arquivos PDF.")

    def selecionar_pdf(self):
        caminho = filedialog.askopenfilename(title="Selecione o catálogo em PDF", filetypes=[("Arquivos PDF", "*.pdf")])
        if caminho:
            self.caminho_pdf = caminho
            nome = os.path.basename(caminho)
            self.label_arquivo.configure(text=f"📄 {nome}", text_color="#2F4F4F")
            self.btn_iniciar.configure(state="normal")

    def iniciar_auditoria(self):
        if not self.caminho_pdf:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo PDF primeiro.")
            return
        self.btn_selecionar.configure(state="disabled")
        self.btn_iniciar.configure(state="disabled", text="Processando...")
        self.barra_progresso.pack(pady=10)
        self.barra_progresso.start()
        self.label_status.configure(text="Iniciando curadoria...")
        threading.Thread(target=self.processar_pdf, daemon=True).start()

    def processar_pdf(self):
        try:
            self.label_status.configure(text="Etapa 1: Lendo QR Codes do PDF...")
            qrcodes = []
            doc = fitz.open(self.caminho_pdf)
            total_paginas = len(doc)
            for i, page in enumerate(doc):
                self.label_status.configure(text=f"Lendo página {i+1}/{total_paginas}...")
                try:
                    pix = page.get_pixmap(dpi=120)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    codes = decode(img)
                    if codes:
                        for c in codes:
                            dados = c.data.decode("utf-8", errors="replace")
                            qrcodes.append({"pagina": i+1, "conteudo": dados})
                    del img, pix
                    gc.collect()
                except Exception:
                    continue
            doc.close()

            if not qrcodes:
                self.after(0, lambda: messagebox.showinfo("Aviso", "Nenhum QR Code foi encontrado neste PDF."))
                self.after(0, self.resetar_botoes)
                return

            self.label_status.configure(text=f"Etapa 2: Testando {len(qrcodes)} links...")
            resultados = []
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

            for idx, item in enumerate(qrcodes, start=1):
                url = item["conteudo"]
                self.label_status.configure(text=f"Testando link {idx}/{len(qrcodes)}...")
                if url.lower().startswith("http"):
                    try:
                        r = requests.head(url, timeout=10, allow_redirects=True, headers=headers)
                        if r.status_code >= 400:
                            r = requests.get(url, timeout=10, allow_redirects=True, headers=headers, stream=True)
                        status = str(r.status_code)
                        if 200 <= r.status_code < 300:
                            desc = "Funcionando"
                        elif r.status_code in (403, 429):
                            desc = "Bloqueio de Robô"
                        else:
                            desc = "Erro / Não encontrado"
                    except requests.exceptions.Timeout:
                        status, desc = "timeout", "Tempo esgotado"
                    except requests.exceptions.ConnectionError:
                        status, desc = "erro", "Falha de conexão"
                    except Exception:
                        status, desc = "erro", "Erro desconhecido"
                else:
                    status, desc = "N/A", "Texto simples"
                resultados.append({"pagina": item["pagina"], "url": url, "status": status, "resultado": desc})
                time.sleep(0.1) 

            self.label_status.configure(text="Etapa 3: Gerando relatório e gráfico...")
            pasta_destino = os.path.join(os.path.expanduser("~"), "Desktop")
            arquivo_txt = os.path.join(pasta_destino, "CuratorQR_Relatorio.txt")
            arquivo_png = os.path.join(pasta_destino, "CuratorQR_Grafico.png")

            # --- NOVA CONTAGEM COM AS 4 CATEGORIAS ---
            ok = sum(1 for r in resultados if r["resultado"] == "Funcionando")
            bloqueados = sum(1 for r in resultados if r["resultado"] == "Bloqueio de Robô")
            quebrados = sum(1 for r in resultados if r["resultado"] in ("Erro / Não encontrado", "Tempo esgotado", "Falha de conexão", "Erro desconhecido"))
            outros = len(resultados) - ok - bloqueados - quebrados

            with open(arquivo_txt, "w", encoding="utf-8") as f:
                f.write(f"RELATÓRIO CURATORQR - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write(f"Arquivo analisado: {os.path.basename(self.caminho_pdf)}\n")
                f.write(f"Desenvolvido por {AUTORA}\n")
                f.write(f"{TEXTO_RODAPE}\n")
                f.write("=" * 80 + "\n\n")
                for r in resultados:
                    f.write(f"Página {r['pagina']:>3} | Status {r['status']:>7} | {r['resultado']}\n")
                    f.write(f"  URL: {r['url']}\n\n")

            # --- NOVO GRÁFICO COM 4 CORES (VERDE, AZUL, AMARELO, VERMELHO) ---
            cor_fundo = '#FFFFFF'
            cores_terra = ['#708238', '#3498db', '#D4A373', '#A33B20'] # Verde, Azul, Ocre, Terracota
            
            fig, ax = plt.subplots(figsize=(8, 6), facecolor=cor_fundo)
            ax.set_facecolor(cor_fundo)
            
            labels = ['Funcionando', 'Bloqueio Robô', 'Atenção', 'Quebrados']
            sizes = [ok, bloqueados, outros, quebrados]
            
            if sum(sizes) > 0:
                # Filtra as categorias que têm valor zero para não aparecerem no gráfico
                labels_ativos = [l for l, s in zip(labels, sizes) if s > 0]
                sizes_ativos = [s for s in sizes if s > 0]
                cores_ativas = [c for c, s in zip(cores_terra, sizes) if s > 0]

                wedges, texts, autotexts = ax.pie(sizes_ativos, colors=cores_ativas, autopct='%1.1f%%', startangle=140, pctdistance=0.78, wedgeprops=dict(width=0.35, edgecolor=cor_fundo, linewidth=4))
                
                for autotext in autotexts:
                    autotext.set_color('#2C2C2C')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(12)
                    autotext.set_family('Arial') 
                    
                plt.title('CuratorQR\nRelatório de Auditoria', fontsize=16, fontweight='bold', color='#2C2C2C', family='Arial', pad=20)
                ax.legend(wedges, labels_ativos, title="Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), prop={'family': 'Arial'}) 
                plt.savefig(arquivo_png, dpi=300, bbox_inches='tight', facecolor=cor_fundo)
            plt.close()

            self.after(0, lambda: messagebox.showinfo("CuratorQR", "Seu relatório está pronto!\nLocalize-o no Desktop.\nAté breve!"))
            self.after(0, self.resetar_botoes)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{str(e)}"))
            self.after(0, self.resetar_botoes)

    def resetar_botoes(self):
        self.barra_progresso.stop()
        self.barra_progresso.pack_forget()
        self.btn_selecionar.configure(state="normal")
        self.btn_iniciar.configure(state="normal", text="Iniciar Auditoria")
        self.label_arquivo.configure(text="📄 Arraste o PDF aqui ou clique para selecionar", text_color="#777777")
        self.label_status.configure(text="")
        self.caminho_pdf = None
        self.btn_iniciar.configure(state="disabled")

if __name__ == "__main__":
    app = AppCuratorQR()
    app.mainloop()