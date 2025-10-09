# 🤖 AI-Powered Document Management & Chat System

This project was developed as part of an engineering internship and provides a comprehensive solution for managing documents, extracting information, and engaging in AI-powered conversations. It features a user-friendly frontend built with React, a robust backend powered by FastAPI, and utilizes AI models for document understanding and question answering. The application allows users to upload, organize, and interact with documents in a **local, self-contained environment**, with no connection to external drives or databases.

---

## 🔒 Confidentiality Notice

This repository contains a neutral and sanitized version of the original internship project.  
All company-specific data, configurations, and design elements have been removed or replaced for confidentiality reasons.

💡 **Local-Only Implementation**  
Due to company preferences, all documents and data are managed **locally within the application**. For other use cases or deployments, integration with external storage or databases could be added as needed.

---

## 🚀 Key Features

* **Document Upload & Management:**  
  Upload documents of various formats (PDF, Word, Excel, etc.) and organize them securely within the application.

* **AI-Powered Chat Interface:**  
  Interact with an AI assistant capable of answering questions based on your uploaded documents. The assistant also provides **source references** for each response.

* **Context-Aware Questioning:**  
  Users can query a **specific document** or ask a **general question**. The AI automatically identifies the most relevant information using **metadata** and semantic similarity.

* **Structured Metadata Extraction & Document Navigation:**  
  Since documents share a similar structure, the system analyzes the **preamble and key sections** to extract distinguishing metadata (title, identifiers). This metadata supports:  
  1. **Filtering and organizing documents** in the manager.  
  2. **Precise AI queries**, enabling quick and accurate answers.

* **Dynamic Indexing & File Management:**  
  All documents are automatically indexed. Any **addition, modification, or deletion**, including actions in the trash/recycle bin, triggers real-time reindexing for fast, context-aware search.

* **File Explorer:**  
  Browse, preview, rename, and move files through an intuitive in-app explorer. Drag-and-drop uploads and **metadata-based filters** make navigation simple. Deleted files are safely managed in the built-in trash/recycle bin.

* **Real-time Streaming Responses & Voice Interaction:**  
  Receive instant feedback from the AI during conversations. Users can also interact via **voice**, both for asking questions and receiving spoken answers.

---

## 🛠️ Tech Stack

**Frontend**  
- React  
- Vite  
- React Router DOM  
- Tailwind CSS  

**Backend**  
- FastAPI (Python)   

**AI Models**  
- **Large Language Model (LLM):** Ollama (LLaMA 3.2:3b-instruct-q4_K_M, nomic-embed-text-13)  
- **Embedding & Ranking Models:** Sentence Transformers (Cross-Encoder architecture)  
- **Named Entity Recognition (NER):** spaCy (fr_core_news_sm)  

**Storage & Data**  
- Chroma (Vector Database)  
- JSON, OS, Pydantic  

**Document Processing**  
- LangChain  
- pdfplumber  
- pdf2image  
- pytesseract  

**Other Libraries & Tools**  
- Transformers (Hugging Face)  
- asyncio  
- httpx

---

## 📦 Getting Started

### Prerequisites
- Node.js and npm (or yarn) for the frontend.  
- Python 3.7+ for the backend.  
- Ollama installed and running for AI model inference.  
- Tesseract installed if OCR functionality is needed.  

### Installation

**Frontend:**  
```bash
cd frontend
npm install # or yarn install
npm run dev # or yarn dev
```

**Backend:**

```bash
cd backend
poetry install # Recommended
# OR
pip install -r requirements.txt
```

### Running Locally

**Frontend:**

```bash
cd frontend
npm run dev
# or
npm start
```

**Backend:**

```bash
cd backend
poetry run uvicorn main:app --reload # Recommended
# OR
python main.py # if you installed dependencies with pip
```

## 💻 Usage

1.  Start both the frontend and backend servers.
2.  Open your browser and navigate to the frontend URL (usually `http://localhost:5173`).
3.  Upload documents using the "MesDocuments" page.
4.  Browse and manage your files in the "Home" or "MesDocuments" pages.
5.  Go to the "Chat" page to ask questions about your documents.

## 📂 Project Structure

```
├── backend/
│   ├── main.py           # Main FastAPI application
│   ├── extractors.py     # Text extraction functions
│   ├── routers/          # API route handlers
│   │   ├── chat.py       # Chat API endpoints
│   │   ├── explorer.py   # File explorer API endpoints
│   │   ├── upload.py     # File upload API endpoints
│   │   └── ...           # Other route handlers
│   ├── watcher.py        # File system watcher 
│   ├── NER_Training.py   # NER Training script
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main application component
│   │   ├── main.jsx        # Entry point for React
│   │   ├── components/    # React components
│   │   │   ├── pages/      # Page components
│   │   │   │   ├── Home.jsx       # Home page
│   │   │   │   ├── MesDocuments.jsx # My Documents page
│   │   │   │   ├── Chat.jsx       # Chat page
│   │   │   │   └── ...           # Other page components
│   │   │   ├── sidebar/    # Sidebar components
│   │   │   └── ...           # Other components
│   │   ├── hooks/        # Custom React hooks
│   │   │   ├── useVoice.js # Voice input/output hook 
│   │   │   └── ...
│   │   ├── assets/       # Static assets (images, etc.)
│   │   └── ...
│   ├── public/         # Public assets (HTML, etc.)
│   └── ...
├── README.md         # This file
├── ...
```

## 🤝 Contributing

We welcome contributions to this project!

1. Fork the repository.  
2. Create a new branch for your feature or bug fix.  
3. Make your changes and commit them with descriptive messages.  
4. Submit a pull request.

💡 **Customization Notes:**  
Contributors can adapt **labels, metadata, and system prompts** to fit different needs while keeping the overall project structure intact.

## 📝 License

This project is licensed under the [MIT License](LICENSE).

## 💖 Thanks Message

Thank you for checking out this project! I hope it's helpful and that you find it valuable.

