import React from "react";
import { FiChevronLeft, FiChevronRight, FiPlusCircle, FiTrash2 } from "react-icons/fi";

const ConversationHistory = ({
  conversations,
  onSelect,
  isVisible,
  onToggle,
  onDelete,
  onNewEmptyChat,
  currentConversationId, 
}) => {
  return (
    <>
      {/* Toggle button */}
      <button
        onClick={onToggle}
        className="fixed top-4 right-4 z-50 p-2 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded shadow-md focus:outline-none"
        aria-label={isVisible ? "Cacher l'historique" : "Afficher l'historique"}
        style={{ width: 40, height: 40 }}
      >
        {isVisible ? (
          <FiChevronRight size={24} className="text-gray-600" />
        ) : (
          <FiChevronLeft size={24} className="text-gray-600" />
        )}
      </button>

      {/* Sidebar */}
      <div
        className={`flex flex-col bg-white border-l border-gray-200 shadow-lg transition-transform duration-300 ${
          isVisible ? "translate-x-0" : "translate-x-full"
        } fixed top-0 right-0 z-40`}
        style={{ width: 320, maxWidth: "100vw", height: "100vh" }}
      >
        {isVisible && (
          <>
            <h3 className="text-xl font-semibold text-gray-800 text-center mt-5">Historique</h3>
            <button
              onClick={onNewEmptyChat}
              className="mt-6 mx-4 mb-2 flex items-center gap-2 px-4 py-2 rounded border border-gray-300 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold"
            >
              <FiPlusCircle size={20} />
              <span>Nouveau Chat</span>
            </button>

            <ul className="overflow-y-auto flex-grow">
              {Array.isArray(conversations) && conversations.length > 0 ? (
                conversations.map((conv, idx) => (
                  <li
                    key={conv.id}
                    className={`flex justify-between items-center px-4 py-2 border-b border-gray-200 cursor-pointer
                      ${conv.id === currentConversationId ? "bg-gray-300 font-semibold text-gray-900" : "hover:bg-gray-100"}
                    `}
                  >

                    <span
                      onClick={() => onSelect(conv)}
                      className="truncate max-w-[80%]"
                      title={conv.name}
                    >
                      {conv.name || "Discussion sans titre"}
                    </span>
                    <button
                      onClick={() => onDelete(idx)}
                      className="text-red-600 hover:text-red-800"
                      aria-label="Supprimer la conversation"
                    >
                      <FiTrash2 size={18} />
                    </button>
                  </li>
                ))
              ) : (
                <li className="px-4 py-2 text-gray-600 text-center">
                  Aucune discussion enregistrée
                </li>
              )}
            </ul>
          </>
        )}
      </div>
    </>
  );
};

export default ConversationHistory;
