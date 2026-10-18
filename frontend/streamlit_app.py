import os
import requests
import streamlit as st

API = os.getenv('API_URL', 'http://127.0.0.1:8080')
st.set_page_config(page_title='RetailMind AI', page_icon='🛍️', layout='wide')
st.title('RetailMind AI')
st.caption('AI shopping assistant and retail operations intelligence')
tab1, tab2 = st.tabs(['Shop with AI', 'Retail dashboard'])
with tab1:
    query = st.text_input('What are you shopping for?', 'Find running shoes under ₹4000')
    if st.button('Find products'):
        try:
            response = requests.post(f'{API}/api/chat',json={'message':query},timeout=90)
            response.raise_for_status()
            data = response.json()
            st.write(data['answer'])
            for p in data['products']:
                st.write(f"**{p['name']}** — ₹{p['price']} — {p['stock']} in stock")
        except requests.RequestException:
            st.error('Unable to reach backend. Check Cloud Run logs and API_URL.')
with tab2:
    if st.button('Refresh metrics'):
        try:
            response = requests.get(f'{API}/api/dashboard',timeout=30)
            response.raise_for_status()
            data = response.json()
            a,b = st.columns(2)
            a.metric('Transaction rows',data['orders'])
            b.metric('Sales revenue (₹)',f"{data['revenue']:,.0f}")
            st.subheader('Low stock alerts')
            st.dataframe(data['low_stock'],use_container_width=True)
        except requests.RequestException:
            st.error('Unable to load dashboard.')
