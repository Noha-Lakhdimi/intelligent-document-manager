import React, { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { FiChevronLeft, FiChevronRight } from "react-icons/fi";
import Chat from "./Chat";
import ConversationHistory from "../sidebar/ConversationHistory";

const API_BASE = "http://localhost:8000/chat";

const ChatPage = () => {
  const [historyVisible, setHistoryVisible] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConvIdx, setCurrentConvIdx] = useState(null);

  useEffect(() => {
    const storedIdx = localStorage.getItem("currentConvIdx");
    fetch(`${API_BASE}/conversations`)
      .then((res) => res.json())
      .then((data) => {
        setConversations(data);
        if (data.length > 0) {
          const idx = storedIdx ? parseInt(storedIdx, 10) : 0;
          setCurrentConvIdx(idx < data.length ? idx : 0);
        } else {
          setCurrentConvIdx(null);
        }
      });
  }, []);

  useEffect(() => {
    if (currentConvIdx !== null) {
      localStorage.setItem("currentConvIdx", currentConvIdx);
    }
  }, [currentConvIdx]);

  const handleSelectConversation = async (conv) => {
    const idx = conversations.findIndex((c) => c.id === conv.id);
    if (idx !== -1) {
      const currentConv = currentConvIdx !== null ? conversations[currentConvIdx] : null;
      if (currentConv && currentConv.mode === "file" && currentConv.id !== conv.id) {
        try {
          await fetch("http://localhost:8000/chat/reset-temp", { method: "POST" });
        } catch (err) {
          console.error("Erreur lors du nettoyage des données temporaires", err);
        }
        const updatedConv = { ...currentConv, mode: "file-readonly" };
        const newConvs = [...conversations];
        newConvs[currentConvIdx] = updatedConv;
        setConversations(newConvs);
  
        updateConversation(updatedConv).catch(console.error);
      }
  
      setCurrentConvIdx(idx);
    }
  };
  

  const saveNewConversation = async (conv) => {
    const res = await fetch(`${API_BASE}/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(conv),
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Erreur lors de la sauvegarde: ${res.status} ${errorText}`);
    }
    return res.json();
  };

  const updateConversation = async (conv) => {
    await fetch(`${API_BASE}/conversations/${conv.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(conv),
    });
  };

  const handleStartConversation = async (firstMessage) => {
    const newId = uuidv4();
    const ts = new Date();
    const mode = firstMessage.type ? "file" : "classic";
    const newConv = {
      id: newId,
      name: `Discussion du ${ts.toLocaleDateString("fr-FR")} ${ts.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })}`,
      mode,
      messages: [firstMessage],
    };

    try {
      const saved = await saveNewConversation(newConv);
      setConversations((prev) => [saved, ...prev]);
      setCurrentConvIdx(0);
      return saved;
    } catch (error) {
      console.error(error);
      alert("Erreur lors de la création de la nouvelle conversation.");
      return null;
    }
  };

  const updateConversationMode = async (convId, mode) => {
    setConversations((prevConvs) => {
      const idx = prevConvs.findIndex((c) => c.id === convId);
      if (idx === -1) return prevConvs;

      const conv = prevConvs[idx];
      if (conv.mode === mode) return prevConvs;

      const updatedConv = { ...conv, mode };
      updateConversation(updatedConv).catch(console.error);

      const newConvs = [...prevConvs];
      newConvs[idx] = updatedConv;

      return newConvs;
    });
  };

  const handleNewEmptyChat = async () => {
    const newId = uuidv4();
    const ts = new Date();
    const newConv = {
      id: newId,
      name: `Discussion du ${ts.toLocaleDateString("fr-FR")} ${ts.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })}`,
      mode: "classic",
      messages: [],
    };
    try {
      const saved = await saveNewConversation(newConv);
      setConversations((prev) => [saved, ...prev]);
      setCurrentConvIdx(0);
      return saved;
    } catch (error) {
      console.error(error);
      alert("Erreur lors de la création de la nouvelle conversation.");
      return null;
    }
  };

  const handleNewMessage = async (msg, conversationId) => {
    if (!conversationId) {
      const newConv = await handleStartConversation(msg);
      if (!newConv) return;
  
      try {
        await fetch(`${API_BASE}/conversations/${newConv.id}/messages`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(msg),
        });
      } catch (err) {
        console.error("Erreur ajout message", err);
      }
      return;
    }
  
    try {
      await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(msg),
      });
    } catch (err) {
      console.error("Erreur ajout message", err);
      return;
    }
  
    setConversations((prevConvs) => {
      const idx = prevConvs.findIndex((c) => c.id === conversationId);
      if (idx === -1) return prevConvs;
  
      const conv = prevConvs[idx];
      const existingMsgIdx = conv.messages.findIndex((m) => m.id === msg.id);
  
      let updatedMessages;
  
      if (existingMsgIdx !== -1) {
        updatedMessages = [...conv.messages];
        updatedMessages[existingMsgIdx] = {
          ...updatedMessages[existingMsgIdx],
          ...msg,
          sources: msg.sources || updatedMessages[existingMsgIdx].sources
        };
      } else {
        updatedMessages = [...conv.messages, msg];
      }
  
      const updatedConv = { ...conv, messages: updatedMessages };
      const newConvs = [...prevConvs];
      newConvs[idx] = updatedConv;
  
      setCurrentConvIdx(idx);
      return newConvs;
    });
  };
  

  const handleDeleteConversation = async (idxDel) => {
    const conv = conversations[idxDel];
    if (conv.id) {
      await fetch(`${API_BASE}/conversations/${conv.id}`, { method: "DELETE" });
    }
    const updated = conversations.filter((_, i) => i !== idxDel);
    setConversations(updated);

    if (updated.length === 0) {
      setCurrentConvIdx(null);
      localStorage.removeItem("currentConvIdx");
    } else {
      setCurrentConvIdx(0);
      localStorage.setItem("currentConvIdx", 0);
    }
  };

  const currentConversation =
    currentConvIdx !== null && conversations[currentConvIdx]
      ? conversations[currentConvIdx]
      : null;

  return (
    <div className="flex h-screen relative">
      <div className="flex-grow flex flex-col bg-gray-50 relative">
        <Chat
          messages={currentConversation?.messages || []}
          isReadOnly={false}
          onMessage={handleNewMessage}
          onNewConversation={handleNewEmptyChat}
          currentConversation={currentConversation}
          onUpdateConversationMode={updateConversationMode}
        />
      </div>

      <div
        style={{
          width: historyVisible ? 320 : 0,
          transition: "width 0.3s ease",
          overflow: "hidden",
          borderLeft: "1px solid #ccc",
        }}
      >
        {historyVisible && (
          <ConversationHistory
          conversations={conversations}
          onSelect={handleSelectConversation}
          onToggle={() => setHistoryVisible(false)}
          isVisible={historyVisible}
          onDelete={handleDeleteConversation}
          onNewEmptyChat={handleNewEmptyChat}
          currentConversationId={currentConversation?.id} 
        />
        
        )}
      </div>

      <div className="fixed top-4 right-4 z-50 group">
        <button
          onClick={() => setHistoryVisible((v) => !v)}
          className="p-2 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded shadow-md focus:outline-none"
          aria-label="Historique"
          style={{ width: 40, height: 40 }}
        >
          {historyVisible ? <FiChevronRight size={24} /> : <FiChevronLeft size={24} />}
        </button>
        {!historyVisible && (
          <div className="absolute top-full right-0 mt-1 text-sm text-gray-800 bg-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            Historique
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;