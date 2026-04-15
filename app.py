# ── Deploy cell — add at the bottom of your notebook ──────────
!pip install -q streamlit pyngrok

# Paste your token here
NGROK_TOKEN = "paste_your_token_here"

# Write the Streamlit app file
app_code = 
import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf

st.set_page_config(page_title="E-Waste Analyzer", page_icon="♻️")
st.title("♻️ AI E-Waste Management System")
st.write("Upload a photo of e-waste to get classification + toxicity score")

# Load model (already trained in your notebook)
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('/content/ewaste_model.h5')

model = load_model()

CLASSES = ['PCB', 'Battery', 'Mobile_Phone', 'Laptop',
           'CRT_Monitor', 'LED_Monitor', 'Cables_Wires', 'Printer_Peripherals']

TOXICITY = {
    'PCB':                {'score':7.2,'level':'HIGH','rec':'Send to certified hazardous e-waste facility immediately.'},
    'Battery':            {'score':8.5,'level':'CRITICAL','rec':'Return to OEM immediately. Never burn or puncture.'},
    'Mobile_Phone':       {'score':4.5,'level':'MEDIUM','rec':'Drop at authorized e-waste center. Remove battery first.'},
    'Laptop':             {'score':4.0,'level':'MEDIUM','rec':'Take to authorized center or OEM exchange program.'},
    'CRT_Monitor':        {'score':8.0,'level':'HIGH','rec':'NEVER smash. Take to certified CRT recycler only.'},
    'LED_Monitor':        {'score':5.5,'level':'MEDIUM','rec':'Send to recycler with mercury handling certification.'},
    'Cables_Wires':       {'score':2.1,'level':'LOW','rec':'Take to scrap dealer. Never burn cables.'},
    'Printer_Peripherals':{'score':3.5,'level':'MEDIUM-LOW','rec':'Drop at authorized center. Use OEM cartridge scheme.'},
}

COLORS = {'CRITICAL':'#c0392b','HIGH':'#e67e22','MEDIUM':'#f39c12',
          'MEDIUM-LOW':'#27ae60','LOW':'#2ecc71'}

uploaded = st.file_uploader("Choose an image", type=["jpg","jpeg","png"])

if uploaded:
    img = Image.open(uploaded).convert('RGB')
    st.image(img, caption="Uploaded Image", width=300)

    arr = np.array(img.resize((224,224)), dtype=np.float32) / 255.0
    probs = model.predict(np.expand_dims(arr,0), verbose=0)[0]
    top3  = np.argsort(probs)[::-1][:3]

    best  = CLASSES[top3[0]]
    conf  = probs[top3[0]] * 100
    tox   = TOXICITY.get(best, {'score':3.0,'level':'LOW','rec':'Take to nearest e-waste center.'})

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Component",  best)
    col2.metric("Confidence", f"{conf:.1f}%")
    col3.metric("Toxicity",   f"{tox['score']}/10")

    color = COLORS.get(tox['level'], '#888')
    st.markdown(f"**Hazard Level:** :{color}[{tox['level']}]")

    st.subheader("Top 3 Predictions")
    for i in top3:
        st.progress(int(probs[i]*100), text=f"{CLASSES[i]}: {probs[i]*100:.1f}%")

    st.subheader("Recommendation")
    st.info(tox['rec'])

with open('/content/app.py', 'w') as f:
    f.write(app_code)

# Launch
from pyngrok import ngrok, conf
conf.get_default().auth_token = NGROK_TOKEN
public_url = ngrok.connect(8501)
print(f"\n🌐 YOUR LIVE URL: {public_url}\n")
print("Share this link with anyone — open in any browser!")

import subprocess
subprocess.Popen(["streamlit", "run", "/content/app.py",
                  "--server.port=8501", "--server.headless=true"])
