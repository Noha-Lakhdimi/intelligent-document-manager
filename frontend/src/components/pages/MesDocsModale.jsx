import React, { useState, useEffect } from 'react';
import { FiFolder, FiFileText, FiInfo, FiSearch } from 'react-icons/fi';

const validExtensions = {
  pdf: "PDF",
  docx: "Word (DOCX)",
  xlsx: "Excel (XLSX)",
  xls: "Excel (XLS)",
  pptx: "PowerPoint (PPTX)",
  jpg: "JPG",
  jpeg: "JPEG",
  png: "PNG"
};

const getFileIconAndColor = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  const fileTypes = {
    pdf: { icon: <FiFileText size={48} />, color: "text-red-500" },
    docx: { icon: <FiFileText size={48} />, color: "text-blue-500" },
    xlsx: { icon: <FiFileText size={48} />, color: "text-green-600" },
    xls: { icon: <FiFileText size={48} />, color: "text-green-600" },
    pptx: { icon: <FiFileText size={48} />, color: "text-orange-500" },
    jpg: { icon: <FiFileText size={48} />, color: "text-purple-500" },
    jpeg: { icon: <FiFileText size={48} />, color: "text-purple-500" },
    png: { icon: <FiFileText size={48} />, color: "text-purple-500" },
    default: { icon: <FiFileText size={48} />, color: "text-gray-500" }
  };
  return fileTypes[extension] || fileTypes.default;
};

const DocumentItem = ({ item, onClick, onProperties, isSelected }) => {
  return (
    <div
      className={`relative bg-white rounded-lg shadow p-4 flex flex-col items-center hover:shadow-md transition cursor-pointer ${
        isSelected ? "ring-2 ring-blue-500" : ""
      }`}
      title={item.name}
      onClick={() => onClick(item)}
    >
      <div className="mb-3">
        {item.is_dir ? (
          <FiFolder size={48} className="text-yellow-500" />
        ) : (
          <div className={getFileIconAndColor(item.name).color}>
            {getFileIconAndColor(item.name).icon}
          </div>
        )}
      </div>
      <div className="w-full min-w-0">
        <p className="truncate text-center text-sm font-medium text-gray-700 px-2">
          {item.name}
        </p>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onProperties(item);
        }}
        className="absolute top-2 text-gray-700 right-2 p-1 hover:bg-blue-100 rounded"
        title="Voir les propriétés"
      >
        <FiInfo size={18} />
      </button>
    </div>
  );
};

const DocumentPropertiesModal = ({ item, onClose }) => {
  if (!item) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-96">
        <h3 className="text-lg font-semibold mb-4">Propriétés</h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li><strong>Nom :</strong> {item.name}</li>
          <li><strong>Type :</strong> {item.is_dir ? 'Dossier' : 'Fichier'}</li>
          <li><strong>Taille :</strong> {item.size || 'Non disponible'}</li>
          <li><strong>Date de création :</strong> {item.creation_date || 'Non disponible'}</li>
          <li><strong>Chemin :</strong> {item.path}</li>
        </ul>
        <button 
          onClick={onClose} 
          className="mt-4 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Fermer
        </button>
      </div>
    </div>
  );
};

const DocumentExplorer = ({
  items,
  currentPath,
  onGoBack,
  onItemClick,
  onProperties,
  searchTerm,
  onSearchChange,
  selectedItem
}) => {
  return (
    <div className="bg-white rounded shadow h-[70vh] flex flex-col">
      <div className="sticky top-0 left-0 z-10 bg-white flex items-center justify-end p-4 border-b border-gray-200">
        {currentPath && (
          <button onClick={onGoBack} className="text-blue-600 hover:underline flex items-center mr-auto">
            ← Retour
          </button>
        )}
        <div className="relative max-w-md w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <FiSearch className="text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Rechercher des documents..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {items.length === 0 ? (
          <p className="text-gray-500 text-center py-10">Aucun fichier ou dossier trouvé.</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {items.map((item, index) => (
              <DocumentItem
                key={index}
                item={item}
                isSelected={selectedItem?.name === item.name}
                onClick={onItemClick}
                onProperties={onProperties}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const MesDocsModale = ({ onSelectFile }) => {
  const [items, setItems] = useState([]);
  const [currentPath, setCurrentPath] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedForAction, setSelectedForAction] = useState(null);

  useEffect(() => {
    fetchItems('');
  }, []);

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setSearchResults([]);
      fetchItems(currentPath);
      return;
    }
    const fetchSearchResults = async () => {
      try {
        const res = await fetch(`http://localhost:8000/explorer/search?query=${encodeURIComponent(searchTerm)}`);
        if (!res.ok) throw new Error('Erreur recherche');
        const data = await res.json();
        setSearchResults(data);
      } catch (e) {
        console.error('Erreur recherche:', e);
        setSearchResults([]);
      }
    };
    fetchSearchResults();
  }, [searchTerm]);

  const fetchItems = async (path) => {
    try {
      const res = await fetch(`http://localhost:8000/explorer/?path=${encodeURIComponent(path)}`);
      if (!res.ok) throw new Error('Erreur chargement des fichiers');
      const data = await res.json();
      setItems(data.items);
      setCurrentPath(data.current_path);
    } catch (error) {
      console.error('Erreur chargement :', error);
      setItems([]);
    }
  };

  const handleItemClick = (item) => {
    if (item.is_dir) {
      fetchItems(item.path);
      setSearchTerm('');
      setSelectedForAction(null);
    } else {
      setSelectedForAction((prev) =>
        prev?.name === item.name ? null : item
      );
    }
  };

  const goBack = () => {
    const parts = currentPath.split('/').filter(Boolean);
    parts.pop();
    fetchItems(parts.join('/'));
    setSearchTerm('');
    setSelectedForAction(null);
  };

  const displayItems = searchTerm.trim() ? searchResults : items;

  return (
    <div className="w-full">
      <DocumentExplorer
        items={displayItems}
        currentPath={currentPath}
        onGoBack={goBack}
        onItemClick={handleItemClick}
        onProperties={setSelectedItem}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        selectedItem={selectedForAction}
      />

      {/* Bouton toujours visible */}
      <div className="flex justify-end mt-4 px-4">
        <button
          onClick={() => {
            if (selectedForAction) {
              onSelectFile(selectedForAction.name);
              setSelectedForAction(null);
            }
          }}
          disabled={!selectedForAction}
          className={`px-4 py-2 rounded transition duration-200 ${
            selectedForAction
              ? "bg-gray-700 text-white hover:bg-gray-800"
              : "bg-gray-300 text-gray-500 cursor-not-allowed"
          }`}
        >
          Charger dans la discussion
        </button>
      </div>

      {/* Propriétés */}
      <DocumentPropertiesModal 
        item={selectedItem} 
        onClose={() => setSelectedItem(null)} 
      />
    </div>
  );
};

export default MesDocsModale;
