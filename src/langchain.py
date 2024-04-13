from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


def get_sql_chain_with_openai(db):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, your job is to write queries given a user’s request.

    <SCHEMA>{schema}</SCHEMA>

    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.

    For example:
    Question: Quais são os produtos mais vendidos em termos de quantidade?
    SQL Query: SELECT product_id, SUM(quantity) as total_quantity FROM order_details GROUP BY product_id ORDER BY total_quantity DESC;

    Question: Quais são os produtos mais populares entre os clientes corporativos?
    SQL Query: SELECT p.product_name, COUNT(*) as total_orders FROM products p JOIN order_details od ON p.id = od.product_id JOIN orders o ON od.order_id = o.id JOIN customers c ON o.customer_id = c.id WHERE c.company IS NOT NULL GROUP BY p.product_name ORDER BY total_orders DESC;


    Question: Quais são os produtos mais vendidos em termos de quantidade?
    SQL Query: SELECT product_id, SUM(quantity) as total_quantity_sold FROM order_details GROUP BY product_id ORDER BY total_quantity_sold DESC;

    Question: Quais são os clientes que mais compraram?
    SQL Query: SELECT c.company, COUNT(*) as total_orders FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.company ORDER BY total_orders DESC;

    Question: Quais os melhores vendedores?
    SQL Query: SELECT e.first_name, e.last_name, COUNT(*) as total_sales FROM employees e JOIN orders o ON e.id = o.employee_id WHERE o.status_id <> 0 GROUP BY e.first_name, e.last_name ORDER BY total_sales DESC;

    Question: Qual é o valor total de todas as vendas realizadas por ano?
    SQL Query:SELECT YEAR(order_date) as year, SUM(shipping_fee + taxes) as total_sales FROM orders  WHERE status_id <> 0 GROUP BY YEAR(order_date);

    Question: Qual o ticket médio por compra?
    SQL Query: SELECT AVG(total) AS average_order_value FROM ( SELECT od.order_id, SUM(od.quantity * od.unit_price) AS total FROM order_details od GROUP BY od.order_id ) AS subquery;

    Question: Qual é o volume de vendas por cidade?
    SQL Query: SELECT c.city, SUM(od.quantity * od.unit_price) AS total_sales FROM orders o JOIN order_details od ON o.id = od.order_id JOIN customers c ON o.customer_id = c.id WHERE o.status_id GROUP BY c.city ORDER BY total_sales DESC;
    Your turn:

    Question: {question}
    SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)

    # llm = ChatOpenAI(model="gpt-4-0125-preview")
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

    def get_schema(_):
        return db.get_table_info()

    return (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm
            | StrOutputParser()
    )