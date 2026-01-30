import streamlit as st
from google import genai
import PyPDF2
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI PDF Chat Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
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
    """Get response from Gemini AI"""
    try:
        # Get API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            st.error("⚠️ API Key not found! Please set GEMINI_API_KEY in your environment.")
            return None
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Create prompt with context
        prompt = f"""You are a helpful AI assistant. A user has uploaded a PDF document and is asking questions about it.

PDF Content:
{pdf_content[:15000]}  

User Question: {user_question}

Please provide a helpful, accurate answer based on the PDF content. If the question asks for:
- A chart or visual: Describe what chart would be helpful and the data it should contain
- Flashcards: Create clear, concise flashcard-style Q&A pairs
- Related information: Suggest relevant points from the document
- General question: Answer comprehensively using the PDF context

Answer:"""
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        
        return response.text
    
    except Exception as e:
        st.error(f"Error getting AI response: {str(e)}")
        return None

# Main UI
st.title("📚 AI PDF Chat Assistant")
st.markdown("Upload a PDF and ask questions - get answers, suggestions, charts, and flashcards!")

# Sidebar for PDF upload
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
                
                # Show preview
                with st.expander("Preview first 500 characters"):
                    st.text(pdf_text[:500] + "...")
    
    if st.session_state.pdf_uploaded:
        if st.button("Clear PDF"):
            st.session_state.pdf_text = ""
            st.session_state.pdf_uploaded = False
            st.session_state.messages = []
            st.rerun()

# Main chat interface
if st.session_state.pdf_uploaded:
    st.markdown("### 💬 Ask me anything about your PDF!")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your PDF..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt, st.session_state.pdf_text)
                
                if response:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Sorry, I couldn't generate a response.")
else:
    st.info("👈 Please upload a PDF file from the sidebar to get started!")
    
    # Example questions
    st.markdown("### 📝 Example Questions You Can Ask:")
    st.markdown("""
    - Summarize the main points of this document
    - Create flashcards for the key concepts
    - What chart would best represent the data in section 2?
    - Suggest related topics I should explore
    - Explain [specific concept] in simple terms
    """)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and Google Gemini AI")

