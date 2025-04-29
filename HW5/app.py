import streamlit as st
from main import find_similar_documents

st.set_page_config(page_title="Поисковая система", layout="centered")

st.title("🔍 Поиск статей по запросу")

user_input = st.text_input("Введите ключевые слова или фразу:")

if user_input:
    st.subheader("Найденные документы:")
    search_results = find_similar_documents(user_input)[:10]

    if search_results:
        for result in search_results:
            st.markdown(
                f"**Документ #{result['doc_id']}** — "
                f"[Открыть]({result['link']}) | "
                f"Сходство: `{result['cosine_sim']:.2f}`"
            )
    else:
        st.warning("По вашему запросу ничего не найдено.")
