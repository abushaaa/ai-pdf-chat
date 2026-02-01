import streamlit as st
import PyPDF2
import os
from dotenv import load_dotenv
import cohere

load_dotenv()

st.set_page_config(
    page_title="AI PDF Chat Assistant",
    page_icon="📚",
    layout="wide"
)

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def get_ai_response(user_question, pdf_content):
    try:
        api_key = os.getenv('COHERE_API_KEY')
        
        if not api_key:
            st.error("⚠️ API Key not found!")
            return None
        
        co = cohere.Client(api_key)
        
        prompt = f"""You are a helpful AI assistant. Answer the user's question based on this PDF content.

PDF Content:
{pdf_content[:10000]}

User Question: {user_question}

Provide a helpful, accurate answer based on the PDF content. If asked for:
- Charts: Describe what visualization would be helpful
- Flashcards: Create clear Q&A pairs
- Related info: Suggest relevant topics from the document

Answer:"""
        
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=800,
            temperature=0.7,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        
        return response.generations[0].text.strip()
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

st.title("📚 AI PDF Chat Assistant")
st.markdown("Upload a PDF and ask questions - get answers, suggestions, and more!")

with st.sidebar:
    st.header("📄 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
            
            if pdf_text:
                st.session_state.pdf_text = pdf_text
                st.session_state.pdf_uploaded = True
                st.success(f"✅ PDF loaded! ({len(pdf_text)} characters)")
                
                with st.expander("Preview first 500 characters"):
                    st.text(pdf_text[:500] + "...")
    
    if st.session_state.pdf_uploaded:
        if st.button("Clear PDF"):
            st.session_state.pdf_text = ""
            st.session_state.pdf_uploaded = False
            st.session_state.messages = []
            st.rerun()

if st.session_state.pdf_uploaded:
    st.markdown("### 💬 Ask me anything about your PDF!")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask a question about your PDF..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt, st.session_state.pdf_text)
                
                if response:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Sorry, couldn't generate a response.")
else:
    st.info("👈 Please upload a PDF file from the sidebar to get started!")
    
    st.markdown("### 📝 Example Questions You Can Ask:")
    st.markdown("""
    - Summarize the main points of this document
    - Create flashcards for the key concepts
    - What chart would best represent the data?
    - Suggest related topics I should explore
    - Explain this concept in simple terms
    """)

st.markdown("---")
st.markdown("Built with Streamlit and Cohere AI")
