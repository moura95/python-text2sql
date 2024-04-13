from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
import sqlalchemy

import langchain as langchain


class ChatInterface:
    def __init__(self):
        load_dotenv()
        self.chat_history = [
            AIMessage(content="Nao Esqueca de Configurar o Banco de Dados na lateral esquerda"),
            AIMessage(content="Pergunte-me qualquer coisa sobre seu banco de dados")
        ]
        st.set_page_config(page_title="Converse com seu Banco de Dados ")
        st.title('Converse com seu Banco de Dados')
        self.db = None
        self.db_uri = ""
        self.engine = None

    def init_database(self, host: str, port: str, user: str, password: str, database: str) -> SQLDatabase:
        self.db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        self.engine = sqlalchemy.create_engine(self.db_uri)
        return SQLDatabase.from_uri(self.db_uri)

    def run(self):
        with st.sidebar:
            st.subheader("Settings")
            st.text_input("Host", value="127.0.0.1", key="Host")
            st.text_input("Port", value="3306", key="Port")
            st.text_input("User", value="user", key="User")
            st.text_input("Password", type="password", value='password', key="Password")
            st.text_input("Database", value="database", key="Database")

            if st.button("Conectar"):
                with st.spinner('Conectando ao banco de dados...'):
                    self.db = self.init_database(
                        host=st.session_state['Host'],
                        port=st.session_state['Port'],
                        user=st.session_state['User'],
                        password=st.session_state['Password'],
                        database=st.session_state['Database'],
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
                chain = langchain.get_sql_chain_with_openai(self.db)
                query = chain.invoke({"question": user_message})

                st.code(query)
                df = pd.read_sql_query(query, self.engine)
                st.dataframe(df)

            self.chat_history.append(AIMessage(content=query))


if __name__ == "__main__":
    interface = ChatInterface()
    interface.run()
