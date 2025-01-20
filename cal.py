import streamlit as st

# Streamlit App Title
st.title("Profit Calculator for SUN E-Learning and IQuest")

# Input Manufacturing Cost
st.header("Manufacturing Cost")
manufacturing_cost = st.number_input("Enter Manufacturing Cost ($)", min_value=0, step=10)

# Profit Margins for SUN E-Learning and IQuest
st.header("Profit Margins")
profit_margin_sun = st.number_input("Enter Profit Margin for SUN E-Learning (%)", min_value=0, max_value=100, step=1)
profit_margin_iquest = st.number_input("Enter Profit Margin for IQuest (%)", min_value=0, max_value=100, step=1)

# Calculate Individual Selling Prices
selling_price_sun = manufacturing_cost + (manufacturing_cost * (profit_margin_sun / 100))
selling_price_iquest = manufacturing_cost + (manufacturing_cost * (profit_margin_iquest / 100))

# Calculate Profits
profit_sun = selling_price_sun - manufacturing_cost
profit_iquest = selling_price_iquest - manufacturing_cost

# Calculate Combined Profit Margin and Total Selling Price
combined_profit_margin = profit_margin_sun + profit_margin_iquest
total_selling_price = manufacturing_cost + (manufacturing_cost * (combined_profit_margin / 100))

# Display Results
st.header("Results")
results = [
    {
        "Company": "SUN E-Learning",
        "Manufacturing Cost ($)": manufacturing_cost,
        "Selling Price ($)": selling_price_sun,
        "Profit ($)": profit_sun,
    },
    {
        "Company": "IQuest",
        "Manufacturing Cost ($)": manufacturing_cost,
        "Selling Price ($)": selling_price_iquest,
        "Profit ($)": profit_iquest,
    }
]

st.table(results)

# Display Combined Results
st.subheader("Combined Results")
st.write(f"**Combined Profit Margin:** {combined_profit_margin:.2f}%")
st.write(f"**Total Selling Price (Combined):** ${total_selling_price:.2f}")
