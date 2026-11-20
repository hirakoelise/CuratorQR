# CuratorQR

**Curadoria Digital e Validação de Referências em QR Code**

O CuratorQR é um software livre desenvolvido em Python para automatizar a auditoria e validação de documentos PDF. Ele extrai QR codes de catálogos, teses e documentos, e testa automaticamente a conectividade de cada link de destino, gerando um relatório detalhado e um gráfico estatístico visual.

Este software integra o pacote **CMT (Cartografia do Movimento por meio de Tecnologias Digitais)** e foi desenvolvido como parte de pesquisa em Artes Cênicas na Universidade de Brasília (UnB).

 Funcionalidades
- Arraste e solte arquivos PDF na interface.
- Extração automática de QR Codes em alta resolução.
- Teste de integridade dos links (Status HTTP).
- Classificação inteligente de resultados: 
  - **Funcionando** (Status 200/202)
  - **Bloqueio de Robô** (Status 403/429 - segurança do site)
  - **Quebrados/Erros** (Status 404, Timeout, Falha de Conexão)
- Geração de relatório em texto (`.txt`) e gráfico visual (`.png`).
- Execução 100% local e segura (o software não faz upload dos seus arquivos para nenhum servidor).

Como usar (Usuário Final)
1. Baixe o arquivo `CuratorQR.exe` na aba **[Releases]** deste repositório.
2. Dê dois cliques para abrir o programa.
3. Arraste o seu arquivo PDF para a área tracejada.
4. Clique em "Iniciar Auditoria".
5. O relatório e o gráfico serão salvos automaticamente na sua Área de Trabalho (Desktop).

Como rodar o código-fonte (Desenvolvedores)
1. Instale o Python 3.10 ou superior.
2. Instale as dependências executando o comando:
   `pip install customtkinter pymupdf pyzbar pillow requests matplotlib tkinterdnd2 pywin32`
3. Execute o arquivo principal:
   `python CuratorQR_beta.py`

Ciência Aberta e Software Livre
Acreditamos que o conhecimento e as ferramentas de preservação da memória devem circular livremente. O CuratorQR integra a cadeia de softwares livres (como o próprio Python) e é disponibilizado publicamente para que museus, artistas e pesquisadores possam auditar seus acervos sem custos. 

## 👩‍💻 Autoria e Licença
Desenvolvido por **Elise Hirako** (Doutora e Mestra em Artes Cênicas - UnB).
Este projeto está sob a licença **MIT**. Uso livre, cópia e modificação permitidos, desde que citada a fonte original (veja o arquivo `LICENSE`).
