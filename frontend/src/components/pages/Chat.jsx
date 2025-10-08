import React, { useRef, useEffect, useState } from "react";
import { useVoice, speakText } from "../../hooks/useVoice";
import {
  FiSend,
  FiFolder,
  FiX,
  FiFile,
  FiFileText,
  FiLock,
  FiMic,
  FiVolume2,
  FiExternalLink
} from "react-icons/fi";
import Logo from "../../assets/logo.jpg";
import MesDocuments from "../pages/MesDocsModale";

const SUGGESTIONS = [
  "Prompt 1", 
  "Prompt 2",
  "Prompt 3", 
  "Prompt 4"
];

const getFileTypeFromName = (fileName) => {
  const ext = fileName.split(".").pop().toLowerCase();
  if (["pdf", "docx", "xls", "xlsx", "pptx"].includes(ext)) {
    return ext;
  }
  return null;
};

const renderFileIcon = (type) => {
  const baseProps = { size: 24, className: "flex-shrink-0" };
  switch (type) {
    case "pdf":
      return <FiFileText {...baseProps} className="text-red-600" />;
    case "docx":
      return <FiFileText {...baseProps} className="text-blue-600" />;
    case "xls":
    case "xlsx":
      return <FiFile {...baseProps} className="text-green-600" />;
    case "pptx":
      return <FiFile {...baseProps} className="text-orange-600" />;
    default:
      return <FiFile {...baseProps} className="text-gray-600" />;
  }
};

const Chat = ({
  messages,
  isReadOnly = false,
  onMessage,
  onNewConversation,
  currentConversation,
  onUpdateConversationMode,
}) => {
  const [input, setInput] = useState("");
  const [showDocs, setShowDocs] = useState(false);
  const [loadingByConversation, setLoadingByConversation] = useState({});
  const [isFileSelectionDisabled, setIsFileSelectionDisabled] = useState(false);
  const [pendingMessage, setPendingMessage] = useState(null);
  const [isReadOnlyMode, setIsReadOnlyMode] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentlySpeakingId, setCurrentlySpeakingId] = useState(null);
  const [hasSentMessage, setHasSentMessage] = useState(false);

  const currentConversationId = currentConversation?.id;
  const mode = currentConversation?.mode || "";
  const isLoading = loadingByConversation[currentConversationId] || false;

  const started = messages.length > 0;
  const messagesEndRef = useRef(null);
  const lastConversationIdRef = useRef(null);

  const hasSelectedFile = messages.some(msg => msg.fileUrl);

  const readMessageAloud = (text, messageId) => {
    if (!text || !window.speechSynthesis) {
      console.error("Synthèse vocale non disponible ou texte vide");
      return;
    }
    
    if (isSpeaking && currentlySpeakingId === messageId) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setCurrentlySpeakingId(null);
      return;
    }
    
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    setIsSpeaking(true);
    setCurrentlySpeakingId(messageId);
    
    utterance.onend = () => {
      setIsSpeaking(false);
      setCurrentlySpeakingId(null);
    };
    
    utterance.onerror = (event) => {
      console.error('Erreur de lecture:', event);
      setIsSpeaking(false);
      setCurrentlySpeakingId(null);
    };
    
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const sendMessageToAPI = async (text) => {
    if (!currentConversationId) {
        console.warn("Aucune conversation active pour envoyer un message");
        return;
    }

    if (!text || !text.trim()) {
        console.warn("Le message est vide");
        return;
    }

    const userMessage = {
        id: Date.now(),
        sender: "user",
        text: text.trim(),
    };
    await onMessage(userMessage, currentConversationId);

    const tempMessageId = Date.now() + 1;
    const tempMessage = {
        id: tempMessageId,
        sender: "bot",
        text: "Assistant est en train de rédiger une réponse...",
        isLoading: true,
    };
    await onMessage(tempMessage, currentConversationId);

    let finalText = "";
    setLoadingForCurrentConversation(true);

    try {
        let endpoint;
        if (mode === "file" && hasSelectedFile) {
            endpoint = "http://localhost:8000/chat/query-by-filename";
        } else {
            endpoint = "http://localhost:8000/chat/stream-query";
        }

        console.log("Envoi à l'endpoint:", endpoint);
        console.log("Données envoyées:", {
            query_text: text.trim(),
            conversation_id: currentConversationId
        });

        const res = await fetch(endpoint, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ 
                query_text: text.trim(), 
                conversation_id: currentConversationId 
            }),
        });

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(
                `HTTP error ${res.status}: ${errorData.detail || res.statusText}`
            );
        }
    
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n").filter(Boolean);

        for (const line of lines) {
          try {
            const data = JSON.parse(line);

            if (data.response) {
              const token = data.response || "";
              finalText += token;

              const updatedBotMessage = {
                id: tempMessageId,
                sender: "bot",
                text: finalText,
                isLoading: true,
              };
              await onMessage(updatedBotMessage, currentConversationId);
            }

            if (data.sources) {
              const updatedBotMessageWithSources = {
                id: tempMessageId,
                sender: "bot",
                text: finalText,
                isLoading: false,
                sources: data.sources,
              };
              await onMessage(updatedBotMessageWithSources, currentConversationId);
            }
          } catch (err) {
            console.error("Error parsing JSON:", err);
          }
        }
      }

      const finalBotMessage = {
        id: tempMessageId,
        sender: "bot",
        text: finalText,
        isLoading: false,
      };
      await onMessage(finalBotMessage, currentConversationId);
    } catch (err) {
      console.error("Error in sendMessageToAPI:", err);
      const errorMsg = {
          id: Date.now() + 2,
          sender: "bot",
          text: `Désolé, une erreur est survenue: ${err.message}`,
          isLoading: false,
      };
      await onMessage(errorMsg, currentConversationId);
  } finally {
      setLoadingForCurrentConversation(false);
  }
};

  const setLoadingForCurrentConversation = (loading) => {
    setLoadingByConversation((prev) => ({
      ...prev,
      [currentConversationId]: loading,
    }));
  };

  const startChatWithMessage = async (text) => {
    if (!text.trim()) return;

    if (!started && !currentConversationId && onNewConversation) {
      setPendingMessage(text);
      await onNewConversation("classic");
    } else {
      setInput("");
      await sendMessageToAPI(text);
    }
  };

  const handleVoiceResult = async (transcript, isFinal) => {
    if (!transcript.trim()) return;
    setInput(transcript);
  };
  
  const { listening, start, stop } = useVoice(handleVoiceResult);

  useEffect(() => {
    const handleBeforeUnload = () => {
      sessionStorage.setItem("isRefreshing", "true");
      sessionStorage.setItem("activeConversation", currentConversationId || "");
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [currentConversationId]);

  useEffect(() => {
    const wasRefreshed = sessionStorage.getItem("isRefreshing") === "true";
    setIsRefreshing(wasRefreshed);
    sessionStorage.removeItem("isRefreshing");
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    setIsFileSelectionDisabled(messages.length > 0);
  }, [messages]);

  useEffect(() => {
    if (pendingMessage && currentConversationId) {
      sendMessageToAPI(pendingMessage);
      setPendingMessage(null);
      setInput("");
    }
  }, [currentConversationId, pendingMessage]);

  useEffect(() => {
    const currentMode = currentConversation?.mode;
    setIsReadOnlyMode(currentMode === "file-readonly");
    lastConversationIdRef.current = currentConversation?.id;
  }, [currentConversation]);

  return (
    <div className="flex flex-col h-screen">
      <div className="top-0 border-b z-20 bg-white h-16 flex items-center justify-between px-4">
        <div className="text-xl font-semibold text-gray-700">Assistant IA</div>
        {started && (
          <div className="text-sm font-medium text-gray-500 absolute left-1/2 transform -translate-x-1/2">
            {isReadOnlyMode ? (
              <span className="flex items-center">
                <FiLock size={14} className="mr-1" /> Lecture seule
              </span>
            ) : (
              `Mode : ${mode === "classic" ? "Classique" : "Fichier"}`
            )}
          </div>
        )}
        <div style={{ width: "80px" }} />
      </div>

      <div className="flex-1 overflow-auto p-4 bg-gray-50 space-y-4">
        {!started ? (
          <div className="flex flex-col justify-center items-center text-center h-full">
            <img src={Logo} alt="Logo AEP" className="w-20 h-20 mb-6" />
            <p className="mb-6 text-gray-600 max-w-md">
              Message to display 
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-xl w-full">
              {SUGGESTIONS.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => startChatWithMessage(suggestion)}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 rounded px-4 py-3 transition"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`max-w-xl py-2 px-8 rounded-xl whitespace-pre-wrap break-words relative group ${
                msg.sender === "user"
                  ? "bg-gray-300 text-gray-900 ml-auto rounded-br-none"
                  : "bg-white text-gray-800 rounded-bl-none shadow"
              }`}
            >
              {msg.text && !msg.isLoading && msg.sender === "bot" && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    readMessageAloud(msg.text, msg.id);
                  }}
                  className={`absolute right-2 bottom-2 p-1 rounded-full ${
                    isSpeaking && currentlySpeakingId === msg.id 
                      ? 'bg-red-100 text-red-500' 
                      : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                  }`}
                  title={
                    isSpeaking && currentlySpeakingId === msg.id 
                      ? "Arrêter la lecture" 
                      : "Lire le message à haute voix"
                  }
                >
                  <FiVolume2 size={16} />
                </button>
              )}

              {msg.type && msg.fileUrl ? (
                <a
                  href={msg.fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-3 border border-gray-400 bg-gray-100 rounded hover:bg-gray-200"
                >
                  {renderFileIcon(msg.type)}
                  <span className="text-gray-800 font-medium truncate max-w-xs">
                    {msg.fileName}
                  </span>
                </a>
              ) : (
                <>
                  {msg.text}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 text-xs text-gray-500 space-y-1 border-t pt-2">
                      <div className="font-semibold text-gray-600">Sources :</div>
                      {Array.from(
                        new Set(msg.sources.map(s => s.source)) 
                      )
                      .filter(source => source)
                      .map((source, idx) => {
                        const normalizedPath = source.replace(/\\/g, '/');
                        const fileName = normalizedPath.split('/').pop();
                        
                        const uniquePages = Array.from(
                          new Set(
                            msg.sources
                              .filter(s => s.source === source)
                              .map(s => s.page !== undefined && s.page !== null ? s.page + 1 : null)
                              .filter(Boolean)
                          )
                        ).sort((a, b) => a - b);

                        return (
                          <div key={idx} className="flex items-center gap-1">
                            <span className="text-blue-600 hover:underline font-medium">{fileName}</span>
                            {uniquePages.length > 0 && (
                              <span className="text-gray-500">
                                (pages {uniquePages.join(', ')})
                              </span>
                            )}
                            <a
                              href={`http://localhost:8000/uploads/${fileName}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline ml-1 text-xs"
                              title="Ouvrir le document"
                            >
                              <FiExternalLink size={12} />
                            </a>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="sticky bottom-0 bg-white border-t px-4 py-2 flex items-center gap-2">
        {isReadOnlyMode ? (
          <div className="w-full text-center py-3 text-gray-500">
            Ce chat est en lecture seule. Créez une nouvelle conversation pour
            poser des questions.
          </div>
        ) : (
          <>
            <button
              onClick={() => setShowDocs(true)}
              title="Sélectionner un fichier existant"
              className={`text-gray-600 hover:text-gray-800 ${
                isLoading || isReadOnly || isFileSelectionDisabled
                  ? "text-gray-400 cursor-not-allowed"
                  : ""
              }`}
              disabled={isLoading || isReadOnly || isFileSelectionDisabled}
            >
              <FiFolder size={20} />
            </button>

            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  startChatWithMessage(input);
                }
              }}
              placeholder="Poser une question..."
              className="flex-grow resize-none border rounded px-3 py-2"
              style={{ maxHeight: "100px" }}
              disabled={isLoading || isReadOnly || isReadOnlyMode}
            />

            <div className="relative group">
            <button
                onClick={() => {
                  if (listening) {
                    stop();
                  } else {
                    start();
                  }
                }}
                className={`p-2 rounded flex items-center gap-2 ${
                  listening 
                    ? "bg-red-500 text-white animate-pulse" 
                    : "bg-gray-300 text-gray-700 hover:bg-gray-400"
                }`}
                disabled={isLoading || isReadOnly || isReadOnlyMode}
              >
                <FiMic size={20} />
              </button>
            </div>

            <button
              onClick={() => startChatWithMessage(input)}
              className="bg-gray-600 hover:bg-gray-700 text-white p-2 rounded"
              disabled={!input.trim() || isLoading || isReadOnly || isReadOnlyMode}
            >
              <FiSend size={20} />
            </button>
          </>
        )}
      </div>

      {showDocs && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center px-4">
          <div className="relative bg-white rounded-lg shadow-lg w-full max-w-5xl max-h-[90vh] overflow-y-auto p-8">
            <button
              onClick={() => setShowDocs(false)}
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-800"
            >
              <FiX size={20} />
            </button>
            <MesDocuments
              onSelectFile={async (fileName) => {
                setShowDocs(false);

                if (!started && onNewConversation && currentConversationId == null) {
                  await onNewConversation("file");
                } 
                else if (onUpdateConversationMode && currentConversationId) {
                  await onUpdateConversationMode(currentConversationId, "file");
                }

                const fileType = getFileTypeFromName(fileName);
                const fileMessage = {
                  id: Date.now(),
                  sender: "user",
                  type: fileType,
                  fileName: fileName,
                  fileUrl: `http://localhost:8000/uploads/${fileName}`,
                  sources: null,
                  isLoading: false
                };

                await onMessage(fileMessage, currentConversationId);

                const botMsg = {
                  id: Date.now() + 1,
                  sender: "bot",
                  text: `Fichier "${fileName}" sélectionné. Posez votre question maintenant.`,
                  type: null,
                  fileName: null,
                  fileUrl: null,
                  sources: null,
                  isLoading: false
                };
                await onMessage(botMsg, currentConversationId);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
