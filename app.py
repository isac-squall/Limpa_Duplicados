import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Pedidos – Limpeza de Duplicados",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Limpeza de Duplicados – BASE_PEDIDOS")
st.write(
    "Sistema operacional com auditoria. "
    "A análise é feita na aba BASE_PEDIDOS."
)

# =========================
# UPLOAD DO ARQUIVO
# =========================
arquivo = st.file_uploader(
    "📂 Carregue a planilha de pedidos",
    type=["xlsx"]
)

if arquivo:
    try:
        # ✅ LÊ SOMENTE A ABA BASE_PEDIDOS
        df = pd.read_excel(
            arquivo,
            sheet_name="BASE_PEDIDOS"
        )
    except ValueError:
        st.error("❌ A aba 'BASE_PEDIDOS' não foi encontrada no arquivo.")
        st.stop()

    # =========================
    # LIMPEZA PREVENTIVA (ANTI TELA BRANCA)
    # =========================
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]
    df.columns = df.columns.astype(str)

    # DataFrame apenas para visualização segura
    df_visual = df.astype(str)

    # =========================
    # PRÉ-VISUALIZAÇÃO
    # =========================
    st.subheader("🔍 Pré-visualização da BASE_PEDIDOS")
    st.dataframe(df_visual.head(50), width="stretch")

    # =========================
    # SELEÇÃO DA COLUNA DE ANÁLISE
    # =========================
    st.subheader("⚙️ Configuração da análise")
    
    # Oferece opções de coluna
    opcoes_coluna = []
    coluna_a = df.columns[0] if len(df.columns) > 0 else None
    coluna_r = None
    
    # Procura pela coluna A (primeira coluna)
    if coluna_a:
        opcoes_coluna.append(f"Coluna A: {coluna_a}")
    
    # Procura pela coluna R (geralmente NF)
    for col in df.columns:
        if str(col).upper() in ['R', 'NF', 'NUMERO_NF', 'NUM_NF', 'NFE']:
            coluna_r = col
            opcoes_coluna.append(f"Coluna R: {coluna_r}")
            break
    
    if len(opcoes_coluna) > 1:
        coluna_selecionada = st.radio(
            "Escolha qual coluna usar para análise de duplicatas:",
            options=opcoes_coluna,
            key="coluna_escolha"
        )
        
        if "Coluna A" in coluna_selecionada:
            coluna_chave = coluna_a
        else:
            coluna_chave = coluna_r
    else:
        coluna_chave = coluna_a
        if coluna_chave:
            st.info(f"🔑 A duplicidade será analisada pela **Coluna A**: `{coluna_chave}`")
        else:
            st.error("❌ Nenhuma coluna válida encontrada.")
            st.stop()

    # =========================
    # REGRA DE TRATAMENTO
    # =========================
    regra = st.selectbox(
        "Como tratar os pedidos duplicados?",
        options=[
            "Manter o primeiro",
            "Manter o último",
            "Remover todos"
        ]
    )

    keep = {
        "Manter o primeiro": "first",
        "Manter o último": "last",
        "Remover todos": False
    }[regra]

    # =========================
    # PROCESSAMENTO
    # =========================
    if st.button("🧹 Analisar e limpar duplicados"):
        total_antes = len(df)

        # 🔴 DUPLICADOS ANTES DA REMOÇÃO
        df_duplicados = df[df.duplicated(
            subset=[coluna_chave],
            keep=False
        )]

        # 🟢 BASE LIMPA
        df_limpo = df.drop_duplicates(
            subset=[coluna_chave],
            keep=keep
        )

        total_depois = len(df_limpo)

        # =========================
        # RESULTADO GERAL - COM MELHOR FEEDBACK
        # =========================
        if df_duplicados.empty:
            st.success("✅ ANÁLISE CONCLUÍDA - NENHUMA DUPLICATA ENCONTRADA!")
            st.info(
                f"📌 A base contém **{total_antes}** registros únicos pela coluna `{coluna_chave}`. "
                "Não há dados duplicados para remover."
            )
        else:
            st.warning(f"⚠️ **{len(df_duplicados)} registros duplicados** foram encontrados e processados.")
            st.success("✅ Processamento concluído com êxito.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Registros originais", total_antes)
        col2.metric("Pedidos duplicados", len(df_duplicados))
        col3.metric("Registros finais", total_depois)

        # =========================
        # VISUALIZAÇÃO DOS DUPLICADOS
        # =========================
        st.subheader("🔴 Pedidos duplicados (antes da remoção)")
        if df_duplicados.empty:
            st.info("✅ Nenhum registro duplicado encontrado para exibição.")
        else:
            st.warning(f"⚠️ Total de {len(df_duplicados)} registros duplicados:")
            st.dataframe(
                df_duplicados.astype(str),
                width="stretch"
            )

        # =========================
        # VISUALIZAÇÃO DA BASE LIMPA
        # =========================
        st.subheader("🟢 Base final sem duplicados")
        st.dataframe(
            df_limpo.astype(str),
            width="stretch"
        )

        # =========================
        # EXPORTAÇÃO EXCEL (AUDITORIA)
        # =========================
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_limpo.to_excel(
                writer,
                sheet_name="Base_Limpa",
                index=False
            )
            df_duplicados.to_excel(
                writer,
                sheet_name="Duplicados_Encontrados",
                index=False
            )

        buffer.seek(0)

        st.download_button(
            "⬇️ Baixar Excel com auditoria completa",
            data=buffer,
            file_name="Pedidos_BASE_PEDIDOS_Auditoria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Informação adicional sobre o processamento
        st.divider()
        st.info(
            f"📊 **Resumo da operação:**\n\n"
            f"- Coluna analisada: `{coluna_chave}`\n"
            f"- Registros verificados: {total_antes}\n"
            f"- Duplicatas encontradas: {len(df_duplicados)}\n"
            f"- Registros finais (após limpeza): {total_depois}\n"
            f"- Regra aplicada: {regra}"
        )