import streamlit as st

def calculate_asymmetric_position(
    account_balance: float,
    risk_percent: float,
    entry_price: float,
    stop_loss: float,
    target_ratio: float
) -> dict:
    """Calculates stock position sizing based on asymmetric risk parameters."""
    if stop_loss >= entry_price:
        raise ValueError("Stop-loss must be strictly below the entry price for long positions.")
    
    total_dollar_risk = account_balance * (risk_percent / 100.0)
    risk_per_share = entry_price - stop_loss
    
    shares_to_buy = int(total_dollar_risk // risk_per_share)
    total_capital_required = shares_to_buy * entry_price
    
    if total_capital_required > account_balance:
        shares_to_buy = int(account_balance // entry_price)
        total_capital_required = shares_to_buy * entry_price
        actual_dollar_risk = shares_to_buy * risk_per_share
    else:
        actual_dollar_risk = shares_to_buy * risk_per_share

    profit_target = entry_price + (risk_per_share * target_ratio)
    potential_profit = shares_to_buy * (profit_target - entry_price)

    return {
        "max_risk": total_dollar_risk,
        "actual_risk": actual_dollar_risk,
        "risk_per_share": risk_per_share,
        "shares": shares_to_buy,
        "capital_needed": total_capital_required,
        "target_price": profit_target,
        "potential_profit": potential_profit
    }

# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="Asymmetric Risk Calculator", page_icon="📈", layout="centered")

st.title("📈 Asymmetric Position Sizing Calculator")
st.markdown("Enforce mathematical risk discipline. Define your downside first to maximize upside.")

# Layout: Two input columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Account Parameters")
    balance = st.number_input("Account Balance ($)", min_value=100.0, value=50000.0, step=1000.0)
    risk_pct = st.number_input("Account Risk Limit (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    ratio = st.number_input("Target Reward-to-Risk Ratio (X:1)", min_value=1.0, max_value=20.0, value=3.0, step=0.5)

with col2:
    st.subheader("Trade Setup")
    entry = st.number_input("Stock Entry Price ($)", min_value=0.01, value=100.0, step=1.0)
    stop = st.number_input("Stop-Loss Price ($)", min_value=0.00, value=95.0, step=1.0)

st.markdown("---")

# Execution and Error Handling
try:
    plan = calculate_asymmetric_position(balance, risk_pct, entry, stop, ratio)
    
    # Visual KPI Blocks
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="🛒 Shares to Buy", value=f"{plan['shares']:,}")
    kpi2.metric(label="🎯 Profit Target", value=f"${plan['target_price']:.2f}")
    kpi3.metric(label="💰 Capital Required", value=f"${plan['capital_needed']:.2f}")
    
    st.markdown("### Detailed Trade Plan Breakdown")
    
    # Secondary metrics display
    detail1, detail2, detail3 = st.columns(3)
    detail1.write(f"**Max Allowed Risk:** ${plan['max_risk']:.2f}")
    detail2.write(f"**Actual Position Risk:** ${plan['actual_risk']:.2f}")
    detail3.write(f"**Risk Per Share:** ${plan['risk_per_share']:.2f}")
    
    # High-impact outcome warning or validation
    if plan['shares'] == 0:
        st.warning("Position size is 0. Your defined stop-loss risk per share exceeds your total allowed account risk.")
    else:
        st.success(f"🟩 **Asymmetric Profile:** Risking **${plan['actual_risk']:.2f}** to potentially make **${plan['potential_profit']:.2f}**.")

except ValueError as err:
    st.error(f"❌ Input Error: {err}")
