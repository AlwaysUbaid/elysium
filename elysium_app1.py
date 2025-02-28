import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# Set page configuration
st.set_page_config(
    page_title="Elysium Trading Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #10b4cf;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0f9cb2;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #9fa3b0;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #ffffff;
    }
    .green-text {
        color: #25c286;
    }
    .red-text {
        color: #f44336;
    }
    .blue-text {
        color: #10b4cf;
    }
    .highlight {
        background-color: #263140;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'market_making_running' not in st.session_state:
    st.session_state.market_making_running = False
if 'strategy_logs' not in st.session_state:
    st.session_state.strategy_logs = []
if 'strategy_params' not in st.session_state:
    st.session_state.strategy_params = {
        "symbol": "HWTR/USDC",
        "max_order_size": 6000,
        "min_order_size": 1000,
        "position_use_pct": 0.90,
        "tick_size": 0.0001,
        "initial_offset": 0.0001,
        "min_offset": 0.00009,
        "offset_reduction": 0.00001,
        "order_refresh_time": 10
    }


# Generate mock data for demonstration
def generate_mock_data():
    # Generate mock balances
    spot_balances = [
        {"Asset": "HWTR", "Available": 12500.45, "Total": 15000.00},
        {"Asset": "USDC", "Available": 8750.32, "Total": 10000.00},
        {"Asset": "ETH", "Available": 1.52, "Total": 1.52},
        {"Asset": "BTC", "Available": 0.08, "Total": 0.08},
    ]

    # Generate mock positions
    positions = [
        {"symbol": "ETH", "size": 1.5, "entry_price": 3550.25, "mark_price": 3620.50,
         "liquidation_price": 2100.00, "unrealized_pnl": 105.37, "margin_used": 1500.00},
        {"symbol": "BTC", "size": 0.08, "entry_price": 68250.75, "mark_price": 68400.25,
         "liquidation_price": 55000.00, "unrealized_pnl": 12.36, "margin_used": 2500.00},
    ]

    # Generate mock orders
    open_orders = [
        {"symbol": "HWTR/USDC", "side": "Buy", "size": 500.0, "price": 0.8125,
         "order_id": 123456, "timestamp": datetime.now() - timedelta(minutes=5)},
        {"symbol": "HWTR/USDC", "side": "Sell", "size": 750.0, "price": 0.8300,
         "order_id": 123457, "timestamp": datetime.now() - timedelta(minutes=3)},
        {"symbol": "ETH", "side": "Buy", "size": 0.5, "price": 3520.00,
         "order_id": 123458, "timestamp": datetime.now() - timedelta(minutes=15)},
    ]

    # Generate mock trade history
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    trades = []
    cumulative_pnl = 0

    for date in dates:
        # Add 1-3 trades per day
        for _ in range(random.randint(1, 3)):
            side = random.choice(["Buy", "Sell"])
            coin = random.choice(["HWTR/USDC", "ETH", "BTC"])
            size = random.uniform(0.01, 2.0) if coin != "HWTR/USDC" else random.uniform(100, 1000)
            price = random.uniform(3500, 3700) if coin == "ETH" else (
                random.uniform(68000, 69000) if coin == "BTC" else random.uniform(0.80, 0.85))
            total_value = size * price
            pnl = random.uniform(-50, 100) if random.random() > 0.6 else 0
            cumulative_pnl += pnl

            trades.append({
                "time": date + timedelta(hours=random.randint(0, 23)),
                "coin": coin,
                "side": side,
                "size": size,
                "price": price,
                "total_value": total_value,
                "pnl": pnl,
                "cumulative_pnl": cumulative_pnl
            })

    trades_df = pd.DataFrame(trades)

    # Generate mock order book
    bid_levels = [
        {"price": 0.8150, "size": 12500, "side": "Bid"},
        {"price": 0.8145, "size": 15000, "side": "Bid"},
        {"price": 0.8140, "size": 18500, "side": "Bid"},
        {"price": 0.8135, "size": 22000, "side": "Bid"},
        {"price": 0.8130, "size": 25000, "side": "Bid"},
    ]

    ask_levels = [
        {"price": 0.8160, "size": 10000, "side": "Ask"},
        {"price": 0.8165, "size": 12500, "side": "Ask"},
        {"price": 0.8170, "size": 15000, "side": "Ask"},
        {"price": 0.8175, "size": 17500, "side": "Ask"},
        {"price": 0.8180, "size": 20000, "side": "Ask"},
    ]

    order_book = pd.concat([pd.DataFrame(bid_levels), pd.DataFrame(ask_levels)])

    return spot_balances, positions, open_orders, trades_df, order_book, bid_levels[0]["price"], ask_levels[0]["price"]


# UI Components
def render_sidebar():
    """Render the sidebar navigation"""
    st.sidebar.markdown('<div class="main-header">🚀 Elysium</div>', unsafe_allow_html=True)

    # Display wallet status
    st.sidebar.success(f"Connected: Demo Wallet")

    st.sidebar.markdown("---")

    # Navigation
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio("",
                            ["Dashboard", "Market Making (HFT)", "Strategy One", "Strategy Two", "Strategy Three",
                             "Settings"],
                            label_visibility="collapsed")

    st.sidebar.markdown("---")

    # Display market data
    st.sidebar.markdown("### Market Data")

    # Display a few key markets
    col1, col2 = st.sidebar.columns(2)
    col1.metric("BTC", "$68,420.50", delta="+1.2%")
    col2.metric("ETH", "$3,620.75", delta="+0.8%")

    st.sidebar.markdown("---")

    # Footer
    st.sidebar.caption("Elysium Trading Platform v1.0.0")

    return page


def render_dashboard():
    """Render the main dashboard page"""
    st.markdown('<div class="main-header">Elysium Dashboard</div>', unsafe_allow_html=True)

    # Generate mock data
    spot_balances, positions, open_orders, trades_df, _, _, _ = generate_mock_data()

    # Display account overview
    st.markdown('<div class="sub-header">Account Overview</div>', unsafe_allow_html=True)

    # Account metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Account Value", "$25,280.50")
    col2.metric("Margin Used", "$4,000.00")
    col3.metric("Position Value", "$7,200.75")

    # Asset balances
    st.markdown('<div class="sub-header">Balances</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">Spot Balances</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(spot_balances), hide_index=True)

    with col2:
        st.markdown('<div class="card">Open Positions</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(positions), hide_index=True)

    # Trading activity
    st.markdown('<div class="sub-header">Trading Activity</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">Active Orders</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(open_orders), hide_index=True)

    with col2:
        st.markdown('<div class="card">Recent Trades</div>', unsafe_allow_html=True)
        st.dataframe(trades_df.head(5), hide_index=True)

    # PnL chart
    st.markdown('<div class="sub-header">Performance Analytics</div>', unsafe_allow_html=True)

    # Create a cumulative PnL chart
    fig = px.line(
        trades_df,
        x='time',
        y='cumulative_pnl',
        title='Cumulative PnL',
        labels={'time': 'Date', 'cumulative_pnl': 'Cumulative PnL ($)'}
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Trading stats
    col1, col2, col3, col4 = st.columns(4)

    total_trades = len(trades_df)
    total_volume = trades_df['total_value'].sum()
    total_pnl = trades_df['pnl'].sum()
    win_rate = len(trades_df[trades_df['pnl'] > 0]) / total_trades * 100 if total_trades > 0 else 0

    col1.metric("Total Trades", f"{total_trades}")
    col2.metric("Trading Volume", f"${total_volume:.2f}")
    col3.metric("Total PnL", f"${total_pnl:.2f}")
    col4.metric("Win Rate", f"{win_rate:.1f}%")


def render_market_making():
    """Render the market making page"""
    st.markdown('<div class="main-header">Pure Market Making (High Frequency)</div>', unsafe_allow_html=True)

    # Strategy control section
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="sub-header">Strategy Control</div>', unsafe_allow_html=True)
        st.write("Configure and control the pure market making strategy for the HWTR/USDC pair.")

    with col2:
        if st.session_state.market_making_running:
            if st.button("⏹️ Stop Strategy", type="primary"):
                st.session_state.market_making_running = False
                st.session_state.strategy_logs.append(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Strategy stopped")
                st.rerun()
        else:
            if st.button("▶️ Start Strategy", type="primary"):
                st.session_state.market_making_running = True
                st.session_state.strategy_logs.append(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Strategy started")
                st.rerun()

    # Strategy parameters
    with st.expander("Strategy Parameters", expanded=not st.session_state.market_making_running):
        st.markdown('<div class="highlight">These parameters control how the market making strategy behaves.</div>',
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Order Parameters**")
            st.session_state.strategy_params["symbol"] = st.text_input(
                "Trading Pair Symbol",
                value=st.session_state.strategy_params["symbol"],
                disabled=st.session_state.market_making_running
            )
            st.session_state.strategy_params["max_order_size"] = st.number_input(
                "Maximum Order Size",
                value=st.session_state.strategy_params["max_order_size"],
                min_value=100,
                disabled=st.session_state.market_making_running
            )
            st.session_state.strategy_params["min_order_size"] = st.number_input(
                "Minimum Order Size",
                value=st.session_state.strategy_params["min_order_size"],
                min_value=10,
                disabled=st.session_state.market_making_running
            )

        with col2:
            st.markdown("**Pricing Parameters**")
            st.session_state.strategy_params["initial_offset"] = st.number_input(
                "Initial Price Offset (0.0001 = 0.01%)",
                value=st.session_state.strategy_params["initial_offset"],
                format="%.5f",
                step=0.00001,
                disabled=st.session_state.market_making_running
            )
            st.session_state.strategy_params["min_offset"] = st.number_input(
                "Minimum Offset",
                value=st.session_state.strategy_params["min_offset"],
                format="%.5f",
                step=0.00001,
                disabled=st.session_state.market_making_running
            )
            st.session_state.strategy_params["order_refresh_time"] = st.number_input(
                "Order Refresh Time (seconds)",
                value=st.session_state.strategy_params["order_refresh_time"],
                min_value=1,
                max_value=60,
                disabled=st.session_state.market_making_running
            )

    # Market data display
    st.markdown('<div class="sub-header">Market Data</div>', unsafe_allow_html=True)

    # Generate mock data
    _, _, _, _, order_book, best_bid, best_ask = generate_mock_data()

    spread = best_ask - best_bid
    spread_pct = (spread / best_bid) * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Best Bid",
        f"${best_bid:.4f}",
        delta=None
    )

    col2.metric(
        "Best Ask",
        f"${best_ask:.4f}",
        delta=None
    )

    col3.metric(
        "Spread",
        f"${spread:.4f}",
        delta=None
    )

    col4.metric(
        "Spread %",
        f"{spread_pct:.3f}%",
        delta=None
    )

    # Create order book visualization
    fig = px.bar(
        order_book,
        x="price",
        y="size",
        color="side",
        title=f"Order Book: {st.session_state.strategy_params['symbol']}",
        color_discrete_map={"Bid": "#25c286", "Ask": "#f44336"}
    )

    fig.update_layout(
        xaxis_title="Price ($)",
        yaxis_title="Size",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display computed strategy prices
    if st.session_state.market_making_running:
        current_buy_offset = max(
            st.session_state.strategy_params["initial_offset"] - st.session_state.strategy_params["offset_reduction"],
            st.session_state.strategy_params["min_offset"])
        current_sell_offset = max(
            st.session_state.strategy_params["initial_offset"] - st.session_state.strategy_params["offset_reduction"],
            st.session_state.strategy_params["min_offset"])

        buy_price = round(best_ask * (1 - current_buy_offset), 6)
        sell_price = round(best_bid * (1 + current_sell_offset), 6)

        st.markdown('<div class="highlight">Current Strategy Prices</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Buy Price",
            f"${buy_price:.6f}",
            delta=f"{-current_buy_offset * 100:.3f}%",
            delta_color="normal"
        )

        col2.metric(
            "Sell Price",
            f"${sell_price:.6f}",
            delta=f"{current_sell_offset * 100:.3f}%",
            delta_color="normal"
        )

        col3.metric(
            "Buy-to-Bid Distance",
            f"${buy_price - best_bid:.6f}"
        )

        col4.metric(
            "Sell-to-Ask Distance",
            f"${best_ask - sell_price:.6f}"
        )

        # Add simulated log entries if running
        if len(st.session_state.strategy_logs) < 20 or random.random() < 0.3:
            possible_logs = [
                f"Calculated prices - Buy: {buy_price:.6f}, Sell: {sell_price:.6f}",
                f"Current market - Bid: {best_bid:.6f}, Ask: {best_ask:.6f}",
                f"Refreshing orders - Position: {random.randint(5000, 15000)} HWTR, USDC: {random.randint(5000, 10000)}",
                f"Placed buy order: {random.randint(500, 1500)} @ {buy_price:.6f}",
                f"Placed sell order: {random.randint(500, 1500)} @ {sell_price:.6f}",
                f"Cancelled order {random.randint(10000, 99999)}",
                f"Order filled: {random.randint(100, 500)} @ {best_bid + random.uniform(0.0001, 0.0010):.6f}"
            ]
            log_entry = random.choice(possible_logs)
            st.session_state.strategy_logs.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {log_entry}")

    # Strategy logs
    st.markdown('<div class="sub-header">Strategy Logs</div>', unsafe_allow_html=True)

    if st.session_state.strategy_logs:
        log_container = st.container(height=300, border=True)
        with log_container:
            for log in reversed(st.session_state.strategy_logs[-50:]):
                st.text(log)
    else:
        st.info("Start the strategy to see logs.")

    # Open orders section
    if st.session_state.market_making_running:
        st.markdown('<div class="sub-header">Strategy Orders</div>', unsafe_allow_html=True)

        # Generate mock strategy orders
        strategy_orders = [
            {"symbol": "HWTR/USDC", "side": "Buy", "size": 750.0, "price": buy_price,
             "order_id": 123460, "timestamp": datetime.now() - timedelta(seconds=30)},
            {"symbol": "HWTR/USDC", "side": "Sell", "size": 850.0, "price": sell_price,
             "order_id": 123461, "timestamp": datetime.now() - timedelta(seconds=30)},
        ]

        st.dataframe(pd.DataFrame(strategy_orders), hide_index=True)

        if st.button("Cancel All Strategy Orders"):
            st.session_state.strategy_logs.append(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cancelled all strategy orders")
            st.success("All strategy orders cancelled")
    else:
        st.info("Start the strategy to place orders")


def render_strategy_page(strategy_name):
    """Render a generic strategy page that is coming soon"""
    st.markdown(f'<div class="main-header">{strategy_name}</div>', unsafe_allow_html=True)

    st.markdown('<div class="card" style="padding: 3rem; text-align: center;">', unsafe_allow_html=True)
    st.markdown('<h2>Coming Soon</h2>', unsafe_allow_html=True)
    st.markdown('<p>This strategy is currently under development and will be available in a future update.</p>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Display some placeholder content
    st.markdown('<div class="sub-header">Strategy Overview</div>', unsafe_allow_html=True)
    st.write(
        f"The {strategy_name} will provide advanced trading capabilities designed to optimize your trading performance.")

    # Show a placeholder image or chart
    st.markdown('<div style="text-align: center; padding: 2rem;">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/800x400?text=Strategy+Visualization+Coming+Soon",
             caption=f"{strategy_name} Visualization")
    st.markdown('</div>', unsafe_allow_html=True)

    # Show expected features
    st.markdown('<div class="sub-header">Expected Features</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('#### Advanced Risk Management')
        st.write("• Customizable stop-loss and take-profit levels")
        st.write("• Position sizing based on volatility")
        st.write("• Dynamic risk adjustment")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('#### Performance Optimization')
        st.write("• Real-time strategy backtesting")
        st.write("• Machine learning parameter optimization")
        st.write("• Automated strategy adjustment")
        st.markdown('</div>', unsafe_allow_html=True)

    # Add a notify me button
    st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
    if st.button("Notify Me When Available", type="primary"):
        st.success("Thanks! We'll notify you when this strategy becomes available.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_settings():
    """Render the settings page"""
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)

    # Platform settings
    st.markdown('<div class="sub-header">Platform Settings</div>', unsafe_allow_html=True)

    # General settings
    with st.expander("General Settings", expanded=True):
        st.markdown('<div class="highlight">Configure general platform settings</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.checkbox("Dark Mode", value=True, disabled=True, help="Enable dark mode theme (always enabled)")
            st.checkbox("Auto-refresh Dashboard", value=True, help="Automatically refresh dashboard data")
            refresh_rate = st.slider("Refresh Rate (seconds)", min_value=5, max_value=60, value=30)

        with col2:
            st.selectbox("Base Currency", options=["USD", "BTC", "ETH"], index=0)
            st.checkbox("Display 24h Change", value=True)
            st.checkbox("Show Notifications", value=True)

    # Strategy defaults
    st.markdown('<div class="sub-header">Strategy Defaults</div>', unsafe_allow_html=True)

    with st.expander("Market Making Defaults", expanded=True):
        st.markdown('<div class="highlight">Configure default parameters for the market making strategy</div>',
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.number_input("Default Max Order Size", value=6000, min_value=100)
            st.number_input("Default Min Order Size", value=1000, min_value=10)
            st.slider("Default Position Use %", min_value=10, max_value=100, value=90)

        with col2:
            st.number_input("Default Initial Offset", value=0.0001, format="%.5f", step=0.00001)
            st.number_input("Default Min Offset", value=0.00009, format="%.5f", step=0.00001)
            st.number_input("Default Order Refresh Time (seconds)", value=10, min_value=1, max_value=60)

    # Save settings
    st.button("Save Settings", type="primary")


# Main app
def main():
    """Main application entry point"""
    # Render sidebar and get selected page
    page = render_sidebar()

    # Render the selected page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Market Making (HFT)":
        render_market_making()
    elif page == "Settings":
        render_settings()
    else:
        render_strategy_page(page)


if __name__ == "__main__":
    main()