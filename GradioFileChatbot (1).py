import gradio as gr
import docx2txt
import PyPDF2
import openai  # Import OpenAI for actual API calls

# Replace with your actual OpenAI API key
API_KEY = "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"  # Replace this with your OpenAI API key
openai.api_key = API_KEY

def read_text_from_file(file_path):
    """Read text from uploaded files."""
    text = ""
    if file_path.name.endswith('.docx'):
        text = docx2txt.process(file_path.name)
    elif file_path.name.endswith('.pdf'):
        with open(file_path.name, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    elif file_path.name.endswith('.txt'):
        with open(file_path.name, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()
    return text

def chatbot_response(files, user_input, history):
    """Process user input and file data, and return a response."""
    # Read text from uploaded files
    file_texts = ""
    if files is not None:
        for file in files:
            file_texts += read_text_from_file(file) + "\n"

    # Combine history, file texts, and user input for context
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    if file_texts:
        messages.append({"role": "system", "content": f"File Content: {file_texts}"})
    for message in history:
        messages.append(message)
    messages.append({"role": "user", "content": user_input})

    # Call OpenAI API to get a response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use your preferred OpenAI model
            messages=messages
        )
        answer = response['choices'][0]['message']['content']
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": answer})
        return history, history
    except Exception as e:
        error_message = f"Error: {str(e)}"
        history.append({"role": "assistant", "content": error_message})
        return history, history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="File Chatbot", type="messages")  # Use 'messages' format
    file_input = gr.File(label="Upload Files", file_types=[".pdf", ".docx", ".txt"], file_count="multiple")
    user_input = gr.Textbox(label="Ask a Question", placeholder="Type your question here...")
    chat_history = gr.State([])  # Holds the conversation history
    submit_button = gr.Button("Submit")
    clear_button = gr.Button("Clear Chat")

    submit_button.click(
        chatbot_response,
        inputs=[file_input, user_input, chat_history],
        outputs=[chatbot, chat_history],
    )
    clear_button.click(lambda: ([], []), outputs=[chatbot, chat_history])

    # Automatically select an available port
    demo.launch(server_name="127.0.0.1")
