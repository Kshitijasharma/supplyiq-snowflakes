import streamlit as st
import requests
import json
import os
from snowflake.snowpark.context import get_active_session


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SupplyIQ",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

session = get_active_session()

SEMANTIC_VIEW = "SUPPLY_CHAIN_DB.SEMANTIC.SUPPLY_CHAIN"
ANALYST_ENDPOINT = "/api/v2/cortex/analyst/message"


# =========================================================
# SESSION STATE
# =========================================================

if "selected_question" not in st.session_state:
    st.session_state.selected_question = None

if "last_question" not in st.session_state:
    st.session_state.last_question = None

if "last_response" not in st.session_state:
    st.session_state.last_response = None


# =========================================================
# CORTEX FUNCTIONS
# =========================================================

def get_snowflake_token():
    """
    Read the OAuth token provided by the
    Snowflake container runtime.
    """
    with open("/snowflake/session/token", "r") as token_file:
        return token_file.read().strip()


def ask_cortex(question):
    """
    Send a natural-language question to Cortex Analyst.
    """

    snowflake_host = os.getenv("SNOWFLAKE_HOST")

    if not snowflake_host:
        raise RuntimeError(
            "SNOWFLAKE_HOST environment variable is unavailable."
        )

    url = f"https://{snowflake_host}{ANALYST_ENDPOINT}"

    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ],
        "semantic_view": SEMANTIC_VIEW
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {get_snowflake_token()}",
        "X-Snowflake-Authorization-Token-Type": "OAUTH"
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(request_body),
        timeout=60
    )

    return response


# =========================================================
# KPI DATA
# =========================================================

@st.cache_data(ttl=300)
def load_kpis():

    query = """
    SELECT
        ROUND(
            100.0 * SUM(qty_received)
            / NULLIF(SUM(qty_ordered), 0),
            2
        ) AS fill_rate,

        ROUND(
            100.0 * COUNT_IF(is_on_time = TRUE)
            / NULLIF(COUNT(*), 0),
            2
        ) AS otd,

        ROUND(
            SUM(landed_cost),
            2
        ) AS landed_cost

    FROM SUPPLY_CHAIN_DB.CURATED.PROCUREMENT
    """

    return session.sql(query).collect()[0]


try:

    kpi = load_kpis()

    fill_rate = kpi["FILL_RATE"]
    otd = kpi["OTD"]
    landed_cost = kpi["LANDED_COST"]

except Exception as e:

    st.error(f"Unable to load KPI data: {e}")
    st.stop()


# =========================================================
# HEADER
# =========================================================

brand_col, status_col = st.columns([4, 1])

with brand_col:

    st.title("◈ SupplyIQ")

    st.caption(
        "Governed Supply Chain Intelligence"
    )


with status_col:

    st.success("● Snowflake connected")


st.divider()


# =========================================================
# HERO
# =========================================================

hero_left, hero_right = st.columns([3, 1])

with hero_left:

    st.header("Ask your supply chain.")

    st.write(
        "Explore procurement, supplier performance, "
        "delivery reliability and inventory using "
        "natural language."
    )

    st.caption(
        "Powered by Snowflake Cortex Analyst + "
        "governed semantic definitions"
    )


with hero_right:

    with st.container(border=True):

        st.caption("SEMANTIC MODEL")

        st.markdown("**SUPPLY_CHAIN**")

        st.caption(
            "Procurement · Sales · Inventory"
        )


st.write("")


# =========================================================
# QUESTION INPUT
# =========================================================

# question = st.text_input(
#     "Ask SupplyIQ",
#     placeholder=(
#         "Ask a question — e.g. "
#         "Which suppliers have the lowest fill rate?"
#     ),
#     height = 120,
#     label_visibility="collapsed"
# )

question = st.text_area(
    "Ask SupplyIQ",
    placeholder="Ask anything about procurement, suppliers, inventory, sales or delivery performance...",
    height=100,
    label_visibility="collapsed"
)

ask_button = st.button(
    "Ask SupplyIQ →",
    type="primary",
    use_container_width=True
)

if not ask_button:
    question = None

# =========================================================
# SUGGESTED QUESTIONS
# =========================================================

st.caption("SUGGESTED QUESTIONS")

q1, q2, q3, q4 = st.columns(4)


with q1:

    if st.button(
        "Supplier fill rate",
        use_container_width=True
    ):

        st.session_state.selected_question = (
            "Which suppliers have the lowest fill rate?"
        )


with q2:

    if st.button(
        "Inventory by category",
        use_container_width=True
    ):

        st.session_state.selected_question = (
            "What is the average days of inventory by category?"
        )


with q3:

    if st.button(
        "Delivery by transport",
        use_container_width=True
    ):

        st.session_state.selected_question = (
            "Compare on-time delivery by transport mode."
        )


with q4:

    if st.button(
        "Landed cost",
        use_container_width=True
    ):

        st.session_state.selected_question = (
            "Which suppliers have the highest landed cost?"
        )


# If user clicks a suggested question,
# use it instead of the text input.

if st.session_state.selected_question:

    question = st.session_state.selected_question

    st.session_state.selected_question = None


# =========================================================
# KPI OVERVIEW
# =========================================================

st.write("")
st.write("")

st.subheader("Live overview")

st.caption(
    "Current supply-chain performance based on "
    "governed procurement metrics."
)

kpi1, kpi2, kpi3 = st.columns(3)


with kpi1:

    with st.container(border=True):

        st.caption("FULFILLMENT")

        st.metric(
            label="Fill Rate",
            value=f"{fill_rate:.2f}%"
        )

        st.caption(
            "Received quantity ÷ ordered quantity"
        )


with kpi2:

    with st.container(border=True):

        st.caption("DELIVERY PERFORMANCE")

        st.metric(
            label="On-Time Delivery",
            value=f"{otd:.2f}%"
        )

        st.caption(
            "Delivered on or before expected date"
        )


with kpi3:

    with st.container(border=True):

        st.caption("PROCUREMENT")

        st.metric(
            label="Estimated Landed Cost",
            value=f"{landed_cost / 1_000_000:.2f}M"
        )

        st.caption(
            "Goods cost + shipment cost"
        )


# =========================================================
# PROCESS QUESTION
# =========================================================

if question:

    st.write("")
    st.divider()

    st.subheader("Conversation")

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # -----------------------------------------------------
    # CALL CORTEX
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown("**◈ SupplyIQ**")

        with st.spinner(
            "Analyzing your supply-chain data..."
        ):

            try:

                response = ask_cortex(question)

            except Exception as e:

                st.error(
                    "Unable to connect to Cortex Analyst."
                )

                with st.expander("Technical details"):
                    st.code(str(e))

                st.stop()


        # =================================================
        # SUCCESS
        # =================================================

        if response.status_code == 200:

            try:

                result = response.json()

            except Exception:

                st.error(
                    "Cortex Analyst returned an invalid response."
                )

                st.stop()


            st.session_state.last_question = question
            st.session_state.last_response = result


            st.success(
                "✓ Answered using governed semantic definitions"
            )


            content = (
                result
                .get("message", {})
                .get("content", [])
            )


            # =================================================
            # RESPONSE ITEMS
            # =================================================

            for item in content:

                item_type = item.get("type")


                # ---------------------------------------------
                # TEXT
                # ---------------------------------------------

                if item_type == "text":

                    text = item.get("text", "")

                    if text:

                        st.markdown(text)


                # ---------------------------------------------
                # SQL
                # ---------------------------------------------

                elif item_type == "sql":

                    sql = item.get("statement")

                    if not sql:
                        continue


                    try:

                        dataframe = (
                            session
                            .sql(sql)
                            .to_pandas()
                        )


                        # =====================================
                        # RESULTS
                        # =====================================

                        if not dataframe.empty:

                            st.markdown("#### Results")

                            st.dataframe(
                                dataframe,
                                use_container_width=True,
                                hide_index=True
                            )


                            # =================================
                            # AUTO VISUALIZATION
                            # =================================

                            numeric_columns = (
                                dataframe
                                .select_dtypes(
                                    include="number"
                                )
                                .columns
                                .tolist()
                            )


                            # Best case:
                            # one label column + one numeric
                            if (
                                len(dataframe.columns) == 2
                                and len(dataframe) > 1
                                and len(numeric_columns) == 1
                            ):

                                st.markdown(
                                    "#### Visualization"
                                )

                                label_column = (
                                    dataframe.columns[0]
                                )

                                chart_data = (
                                    dataframe
                                    .set_index(label_column)
                                )

                                st.bar_chart(
                                    chart_data
                                )


                            # More complex numeric results
                            elif (
                                len(numeric_columns) > 0
                                and len(dataframe) > 1
                            ):

                                with st.expander(
                                    "Show visualization"
                                ):

                                    try:

                                        non_numeric = [
                                            column
                                            for column
                                            in dataframe.columns
                                            if column
                                            not in numeric_columns
                                        ]

                                        if non_numeric:

                                            chart_data = (
                                                dataframe
                                                .set_index(
                                                    non_numeric[0]
                                                )
                                            )

                                            st.bar_chart(
                                                chart_data[
                                                    numeric_columns
                                                ]
                                            )

                                    except Exception:

                                        st.caption(
                                            "Visualization is not "
                                            "available for this result."
                                        )


                        else:

                            st.info(
                                "The query completed successfully "
                                "but returned no matching records."
                            )


                    except Exception as e:

                        st.error(
                            "Cortex generated a query, but "
                            "Snowflake could not execute it."
                        )

                        with st.expander(
                            "Technical details"
                        ):

                            st.code(str(e))


                    # =========================================
                    # SQL TRANSPARENCY
                    # =========================================

                    with st.expander(
                        "View generated SQL"
                    ):

                        st.code(
                            sql,
                            language="sql"
                        )


                # ---------------------------------------------
                # SUGGESTIONS
                # ---------------------------------------------

                elif item_type in (
                    "suggestion",
                    "suggestions"
                ):

                    suggestions = (
                        item.get("suggestions")
                        or item.get("suggestion")
                        or []
                    )


                    if suggestions:

                        st.info(
                            "SupplyIQ needs a little more "
                            "information to answer that question."
                        )

                        st.markdown(
                            "**Try one of these:**"
                        )


                        if isinstance(
                            suggestions,
                            list
                        ):

                            for suggestion in suggestions:

                                st.write(
                                    f"• {suggestion}"
                                )

                        else:

                            st.write(
                                suggestions
                            )


        # =================================================
        # CORTEX ERROR
        # =================================================

        else:

            st.error(
                "Cortex Analyst couldn't process "
                "this question."
            )

            with st.expander(
                "Technical details"
            ):

                st.code(
                    f"HTTP {response.status_code}\n\n"
                    f"{response.text}"
                )


# =========================================================
# GOVERNANCE
# =========================================================

st.write("")
st.write("")
st.divider()

st.subheader("Governed semantic layer")

st.caption(
    "Business users receive consistent answers because "
    "core supply-chain metrics have centrally defined meanings."
)


g1, g2, g3, g4 = st.columns(4)


with g1:

    with st.container(border=True):

        st.caption("FULFILLMENT")

        st.markdown("**Fill Rate**")

        st.write(
            "Received quantity ÷ ordered quantity"
        )


with g2:

    with st.container(border=True):

        st.caption("DELIVERY")

        st.markdown("**On-Time Delivery**")

        st.write(
            "Actual receipt date compared with "
            "expected receipt date"
        )


with g3:

    with st.container(border=True):

        st.caption("COST")

        st.markdown("**Landed Cost**")

        st.write(
            "Received-goods cost + shipment cost"
        )


with g4:

    with st.container(border=True):

        st.caption("INVENTORY")

        st.markdown("**Days of Inventory**")

        st.write(
            "On-hand inventory ÷ average daily demand"
        )


# =========================================================
# DATA MODEL
# =========================================================

with st.expander(
    "About the SupplyIQ data model"
):

    model1, model2, model3 = st.columns(3)


    with model1:

        st.markdown("**Procurement**")

        st.caption(
            "Purchase orders, suppliers, routes, "
            "delivery performance and costs."
        )


    with model2:

        st.markdown("**Sales**")

        st.caption(
            "Products, customers, order quantities "
            "and sales performance."
        )


    with model3:

        st.markdown("**Inventory**")

        st.caption(
            "Stock levels, demand and "
            "inventory coverage."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

footer_left, footer_right = st.columns([3, 1])


with footer_left:

    st.caption(
        "SupplyIQ · Governed Conversational "
        "Supply Chain Analytics"
    )


with footer_right:

    st.caption(
        "Powered by Snowflake Cortex"
    )