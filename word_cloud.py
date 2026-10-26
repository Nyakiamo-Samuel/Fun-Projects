import streamlit as st
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pypdf

# App Configuration
st.set_page_config(page_title="Word Cloud Generator", page_icon="☁️", layout="centered")

st.title("☁️ Interactive Word Cloud Generator")
st.write("Upload a text source (TXT/PDF) and an optional image to use as a custom shape mask!")

# Layout columns for file uploads
col1, col2 = st.columns(2)

text_content = ""
image_mask = None

with col1:
    st.subheader("1. Source Text File")
    uploaded_text_file = st.file_uploader(
        "Upload a .txt or .pdf file", 
        type=["txt", "pdf"]
    )
    
    if uploaded_text_file is not None:
        file_extension = uploaded_text_file.name.split(".")[-1].lower()
        
        # Process TXT files
        if file_extension == "txt":
            text_content = uploaded_text_file.read().decode("utf-8")
            st.success("Successfully loaded TXT file!", width=800)
            
        # Process PDF files
        elif file_extension == "pdf":
            try:
                pdf_reader = pypdf.PdfReader(uploaded_text_file)
                parsed_text = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        parsed_text.append(page_text)
                text_content = "\n".join(parsed_text)
                st.success(f"Successfully extracted text from {len(pdf_reader.pages)} PDF pages!", width=800)
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

with col2:
    st.subheader("2. Shape Mask (Optional)")
    uploaded_image_file = st.file_uploader(
        "Upload a silhouette image (.jpg, .jpeg, .png)", 
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_image_file is not None:
        # Load image and convert to numpy array mask
        img = Image.open(uploaded_image_file)
        # Convert to grayscale / standard masking format
        image_mask = np.array(img)
        st.image(img, caption="Uploaded Mask Shape", width=150)

# Customization Sidebar Options
st.sidebar.header("🎨 Word Cloud Settings")
bg_color = st.sidebar.color_picker("Background Color", "#ffffff")
max_words = st.sidebar.slider("Maximum Words", min_value=10, max_value=500, value=200, step=10)
contour_width = st.sidebar.slider("Contour Line Width", min_value=0, max_value=5, value=0)
contour_color = st.sidebar.color_picker("Contour Line Color", "#000000")

# Generation Logic
if st.button("🚀 Generate Word Cloud", type="primary", width=800):
    if not text_content.strip():
        st.warning("Please upload a text or PDF file containing readable text first.")
    else:
        with st.spinner("Generating your word cloud..."):
            try:
                # Initialize WordCloud configuration
                wc = WordCloud(
                    background_color=bg_color,
                    max_words=max_words,
                    stopwords=STOPWORDS,
                    mask=image_mask,
                    contour_width=contour_width,
                    contour_color=contour_color,
                    width=800,
                    height=400 if image_mask is None else None
                )
                
                # Generate text frequencies
                _wordcloud = wc.generate(text_content)
                
                # Plotting configuration using Matplotlib
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(_wordcloud, interpolation="bilinear")
                ax.axis("off")
                
                # Display output inside the Streamlit Web UI
                st.pyplot(fig)
                
                # Save generated image to local memory buffer for a download button
                img_array = wc.to_array()
                result_img = Image.fromarray(img_array)
                
                import io
                buf = io.BytesIO()
                result_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 Download Word Cloud Image",
                    data=byte_im,
                    file_name="wordcloud_output.png",
                    mime="image/png",
                    width=800
                )
                
            except Exception as e:
                st.error(f"Failed to generate Word Cloud: {e}")


# streamlit run PythonProject\Word_cloud\word_cloud.py