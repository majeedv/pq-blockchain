"""
main.py  (Azraf: frontend)

Run from the project folder with:   streamlit run app/main.py
All real work happens in backend.py. This file only draws screens.
"""

import datetime

import pandas as pd
import streamlit as st

import backend

st.set_page_config(page_title="PQ Blockchain Prototype", page_icon="🔐", layout="wide")

# Streamlit reruns this whole file on every click, so keep data in session_state.
if "state" not in st.session_state:
    st.session_state.state = backend.new_state()
if "last_result" not in st.session_state:
    st.session_state.last_result = None

state = st.session_state.state

PAGES = ["Overview", "Create wallet", "Send credits", "View blockchain", "View performance"]
st.sidebar.title("🔐 PQ Blockchain")
st.sidebar.caption("ECDSA vs ML-DSA-44 prototype")
page = st.sidebar.radio("Menu", PAGES)
st.sidebar.info("Simulated credits only. The signatures in this version are placeholders.")


def show_time(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------------------- Overview
if page == "Overview":
    st.title("Overview")
    st.write(
        "Create wallets, send credits signed with ECDSA or ML-DSA-44, "
        "and see how the blockchain and the performance results change."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wallets", len(state["wallets"]))
    c2.metric("Blocks", len(state["chain"]) - 1)
    c3.metric("Rejected transactions", state["rejected"])
    c4.metric("Credits in circulation", sum(w["balance"] for w in state["wallets"].values()))

    if not state["wallets"]:
        st.info("No wallets yet. Add three sample wallets to try the prototype quickly.")
        if st.button("Add Alice, Bob and Charlie"):
            backend.create_sample_wallets(state)
            st.rerun()

# ------------------------------------------------------------ Create wallet
elif page == "Create wallet":
    st.title("Create wallet")
    name = st.text_input("Wallet name", placeholder="e.g. Dana")
    if st.button("Create wallet"):
        result = backend.create_wallet(state, name)
        (st.success if result["ok"] else st.error)(result["message"])

    st.subheader("Wallets")
    if state["wallets"]:
        rows = [
            {
                "Name": w["name"],
                "Balance": w["balance"],
                "ECDSA public key": w["public_keys"]["ECDSA"][:12] + "…",
                "ML-DSA-44 public key": w["public_keys"]["ML-DSA-44"][:12] + "…",
            }
            for w in state["wallets"].values()
        ]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("No wallets yet.")

# ------------------------------------------------------------ Send credits
elif page == "Send credits":
    st.title("Send credits")
    names = list(state["wallets"])

    if len(names) < 2:
        st.warning("You need at least two wallets first. Go to Create wallet, or add samples on the Overview page.")
    else:
        left, right = st.columns(2)

        with left:
            with st.container(border=True):
                sender = st.selectbox("Sender", names, format_func=lambda n: f"{n} ({state['wallets'][n]['balance']} credits)")
                receiver = st.selectbox("Receiver", [n for n in names if n != sender])
                amount = st.number_input("Amount", min_value=1, value=25, step=1)
                algorithm = st.radio("Signature algorithm", backend.ALGORITHMS, horizontal=True)
                if st.button("Sign and send", type="primary"):
                    st.session_state.last_result = backend.send_transaction(
                        state, sender, receiver, amount, algorithm
                    )
                    st.rerun()

        with right:
            with st.container(border=True):
                st.subheader("Result")
                result = st.session_state.last_result
                if result is None:
                    st.caption("Send a transaction to see the result here.")
                elif not result["ok"]:
                    st.error("Rejected: " + result["message"])
                else:
                    st.success(result["message"])
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Signature size", f"{result['signature_bytes']:,} B")
                    m2.metric("Sign time", f"{result['sign_ms']:.3f} ms")
                    m3.metric("Verify time", f"{result['verify_ms']:.3f} ms")
                    tx = result["transaction"]
                    st.caption("Transaction preview")
                    st.json(
                        {
                            "sender": tx["sender"],
                            "receiver": tx["receiver"],
                            "amount": tx["amount"],
                            "nonce": tx["nonce"],
                            "timestamp": show_time(tx["timestamp"]),
                            "algorithm": tx["algorithm"],
                            "public_key": tx["public_key"][:16] + "…",
                            "signature": tx["signature"][:16] + "…",
                        }
                    )

# ---------------------------------------------------------- View blockchain
elif page == "View blockchain":
    st.title("Blockchain")

    if st.button("Check chain integrity"):
        problems = backend.verify_chain(state)
        if problems:
            st.error("Tampering detected:\n\n" + "\n\n".join(problems))
        else:
            st.success("All hashes and links are consistent.")

    for block in reversed(backend.get_chain(state)):
        title = f"Block #{block['index']}  |  {len(block['transactions'])} transaction(s)  |  hash {block['hash'][:12]}…"
        with st.expander(title):
            st.write(f"Time: {show_time(block['timestamp'])}")
            st.code(f"previous hash: {block['previous_hash']}\nhash:          {block['hash']}")
            for tx in block["transactions"]:
                st.write(
                    f"{tx['sender']} → {tx['receiver']}: {tx['amount']} credits "
                    f"({tx['algorithm']}, nonce {tx['nonce']})"
                )

# -------------------------------------------------------- View performance
else:
    st.title("Performance")
    st.warning("Placeholder data. Real results from the benchmark will replace these numbers in Capstone 2.")

    df = pd.DataFrame(backend.get_benchmark_results())

    st.subheader("Median time per operation (ms)")
    times = df.pivot(index="operation", columns="algorithm", values="median_ms")
    st.bar_chart(times, color=["#F59E0B", "#14B8A6"])

    st.subheader("Sizes per transaction (bytes)")
    sizes = (
        df.drop_duplicates("algorithm")
        .set_index("algorithm")[["public_key_bytes", "signature_bytes"]]
        .T
    )
    st.bar_chart(sizes, color=["#F59E0B", "#14B8A6"])

    with st.expander("Raw table"):
        st.dataframe(df, width="stretch", hide_index=True)
