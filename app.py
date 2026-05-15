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
        # ✅ LEITURA OTIMIZADA E COMPATÍVEL
        df = pd.read_excel(
            arquivo,
            sheet_name="BASE_PEDIDOS",
            engine="openpyxl"
        )

    except ValueError:
        st.error("❌ A aba 'BASE_PEDIDOS' não foi encontrada no arquivo.")
        st.stop()

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
        st.stop()

    # =========================
    # LIMPEZA PREVENTIVA
    # =========================
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]
    df.columns = df.columns.astype(str)

    if df.empty:
        st.error("❌ A planilha está vazia.")
        st.stop()

    # =========================
    # PRÉ-VISUALIZAÇÃO
    # =========================
    st.subheader("🔍 Pré-visualização da BASE_PEDIDOS")
    st.dataframe(df.head(50).astype(str), use_container_width=True)

    # =========================
    # SELEÇÃO DA COLUNA DE ANÁLISE
    # =========================
    st.subheader("⚙️ Configuração da análise")

    opcoes_coluna = []

    # Coluna A (primeira)
    coluna_a = df.columns[0] if len(df.columns) > 0 else None

    # Coluna R (NF ou equivalentes)
    coluna_r = next(
        (col for col in df.columns
         if str(col).upper() in ['R', 'NF', 'NUMERO_NF', 'NUM_NF', 'NFE']),
        None
    )

    if coluna_a:
        opcoes_coluna.append(f"Coluna A: {coluna_a}")

    if coluna_r:
        opcoes_coluna.append(f"Coluna R: {coluna_r}")

    if len(opcoes_coluna) > 1:
        coluna_selecionada = st.radio(
            "Escolha qual coluna usar para análise de duplicatas:",
            options=opcoes_coluna
        )

        coluna_chave = coluna_a if "Coluna A" in coluna_selecionada else coluna_r

    else:
        coluna_chave = coluna_a

        if coluna_chave:
            st.info(f"🔑 A duplicidade será analisada pela **Coluna A**: `{coluna_chave}`")
        else:
            st.error("❌ Nenhuma coluna válida encontrada.")
            st.stop()

    # =========================
    # VALIDAÇÃO DE DADOS
    # =========================
    df = df.dropna(subset=[coluna_chave])

    if df.empty:
        st.error("❌ Não há dados válidos após remover valores vazios.")
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
        with st.spinner("Processando dados..."):

            total_antes = len(df)

            # DUPLICADOS
            df_duplicados = df[
                df.duplicated(subset=[coluna_chave], keep=False)
            ].sort_values(by=coluna_chave)

            # BASE LIMPA
            df_limpo = df.drop_duplicates(
                subset=[coluna_chave],
                keep=keep
            )

            total_depois = len(df_limpo)

            # =========================
            # MÉTRICAS
            # =========================
            percentual = (
                (len(df_duplicados) / total_antes) * 100
                if total_antes > 0 else 0
            )

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Registros originais", total_antes)
            col2.metric("Duplicados", len(df_duplicados))
            col3.metric("Registros finais", total_depois)
            col4.metric("Taxa de duplicação", f"{percentual:.2f}%")

            # =========================
            # FEEDBACK
            # =========================
            if df_duplicados.empty:
                st.success("✅ Nenhuma duplicata encontrada!")
            else:
                st.warning(f"⚠️ {len(df_duplicados)} registros duplicados encontrados.")
                st.success("✅ Processamento concluído com sucesso.")

            # =========================
            # VISUALIZAÇÃO
            # =========================
            st.subheader("🔴 Duplicados encontrados")

            if df_duplicados.empty:
                st.info("Nenhum duplicado para exibir.")
            else:
                st.dataframe(
                    df_duplicados.head(200).astype(str),
                    use_container_width=True
                )

            st.subheader("🟢 Base final tratada")

            st.dataframe(
                df_limpo.head(200).astype(str),
                use_container_width=True
            )

            # =========================
            # EXPORTAÇÃO
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

            # =========================
            # RESUMO FINAL
            # =========================
            st.divider()
            st.info(
                f"""
📊 **Resumo da operação**

- Coluna analisada: `{coluna_chave}`
- Registros analisados: {total_antes}
- Duplicatas encontradas: {len(df_duplicados)}
- Registros finais: {total_depois}
- Regra aplicada: {regra}
"""
            )