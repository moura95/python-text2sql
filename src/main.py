from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
import sqlalchemy
import langchain as langchain

# Fix langchain core Error
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = False


class ChatInterface:
    def __init__(self):
        load_dotenv()
        self.chat_history = [
            AIMessage(content="Não esqueça de configurar o Banco de Dados na lateral esquerda"),
            AIMessage(content="Pergunte-me qualquer coisa sobre seu banco de dados")
        ]
        st.set_page_config(page_title="Converse com seu Banco de Dados ")
        st.title('Converse com seu Banco de Dados')

    @staticmethod
    def init_database(host: str, port: str, user: str, password: str, database: str):
        db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        engine = sqlalchemy.create_engine(db_uri)
        return SQLDatabase.from_uri(db_uri), engine

    def run(self):
        with st.sidebar:
            st.subheader("Settings")
            host = st.text_input("Host", value="127.0.0.1", key="Host")
            port = st.text_input("Port", value="3306", key="Port")
            user = st.text_input("User", value="user", key="User")
            password = st.text_input("Password", type="password", value='password', key="Password")
            database = st.text_input("Database", value="database", key="Database")

            if st.button("Conectar"):
                with st.spinner('Conectando ao banco de dados...'):
                    st.session_state.db, st.session_state.engine = self.init_database(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                    )
                    st.success("Conectado ao banco de dados")

        for message in self.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.markdown(message.content)
            else:
                with st.chat_message("Human"):
                    st.markdown(message.content)

        user_message = st.chat_input("Digite uma mensagem")
        if user_message:
            self.chat_history.append(HumanMessage(content=user_message))
            with st.chat_message("Human"):
                st.markdown(user_message)

            with st.chat_message("AI"):
                if st.session_state.db:
                    chain = langchain.get_sql_chain_with_openai(st.session_state.db)
                    query = chain.invoke({"question": user_message})

                    st.code(query)
                    df = pd.read_sql_query(query, st.session_state.engine)
                    st.dataframe(df)

                    self.chat_history.append(AIMessage(content=query))
                else:
                    st.warning("Por favor, conecte-se ao banco de dados antes de fazer uma consulta.")


if __name__ == "__main__":
    interface = ChatInterface()
    interface.run()
