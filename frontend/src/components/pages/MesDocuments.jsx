import React, { useState, useEffect, useRef } from 'react';
import { FiFolder, FiFileText, FiMoreVertical, FiEdit2, FiTrash2, FiDownload, FiCopy, FiMove, FiInfo, FiX, FiCheck, FiFilePlus, FiArrowLeft } from 'react-icons/fi';
import Navbar from '../navbar/Navbar';

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

const FileConflictDialog = ({ filename, onReplace, onRename, onCancel }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Fichier existant</h3>
          <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
            <FiX size={20} />
          </button>
        </div>
        
        <p className="mb-4">
          Le fichier <span className="font-semibold">"{filename}"</span> existe déjà.
          Que souhaitez-vous faire ?
        </p>
        
        <div className="flex flex-col space-y-3">
          <button
            onClick={onReplace}
            className="flex items-center justify-between px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            <span>Remplacer le fichier existant</span>
            <FiCheck />
          </button>
          
          <button
            onClick={onRename}
            className="flex items-center justify-between px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            <span>Créer une copie</span>
            <FiFilePlus />
          </button>
          
          <button
            onClick={onCancel}
            className="flex items-center justify-between px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            <span>Annuler l'opération</span>
            <FiX />
          </button>
        </div>
      </div>
    </div>
  );
};

const FolderItem = ({ 
  item, 
  onDoubleClick, 
  onMenuClick, 
  menuOpen, 
  menuRef,
  onRename,
  onDelete,
  onMove,
  onCopy,
  onProperties
}) => (
  <div className="relative bg-white rounded-lg shadow p-4 flex flex-col items-center hover:shadow-md transition">
    <div className="mb-3" onDoubleClick={onDoubleClick}>
      <FiFolder size={48} className="text-yellow-500" />
    </div>
    
    <div className="w-full min-w-0" onDoubleClick={onDoubleClick}>
      <p className="truncate text-center text-sm font-medium text-gray-700 px-2">
        {item.name}
      </p>
    </div>
    
    <button
      onClick={onMenuClick}
      className="absolute top-2 right-2 p-1 hover:bg-gray-200 rounded"
    >
      <FiMoreVertical size={18} />
    </button>

    {menuOpen && (
      <div ref={menuRef} className="absolute top-8 right-2 w-40 bg-white border rounded shadow z-50">
        <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-blue-100" onClick={onRename}>
          <FiEdit2 /> Renommer
        </button>
        <button className="w-full px-4 py-2 flex items-center gap-2 text-red-600 hover:bg-red-100" onClick={onDelete}>
          <FiTrash2 /> Supprimer
        </button>
        <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-yellow-100" onClick={onMove}>
          <FiMove /> Déplacer
        </button>
        <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-green-100" onClick={onCopy}>
          <FiCopy /> Copier
        </button>
        <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-gray-100" onClick={onProperties}>
          <FiInfo /> Propriétés
        </button>
      </div>
    )}
  </div>
);

const FileItem = ({ 
  item, 
  onDoubleClick, 
  onMenuClick, 
  menuOpen, 
  menuRef,
  onRename,
  onDelete,
  onDownload,
  onMove,
  onCopy,
  onProperties
}) => {
  const { icon, color } = getFileIconAndColor(item.name);
  
  return (
    <div className="relative bg-white rounded-lg shadow p-4 flex flex-col items-center hover:shadow-md transition">
      <div className={`mb-3 ${color}`} onDoubleClick={onDoubleClick}>
        {icon}
      </div>
      
      <div className="w-full min-w-0" onDoubleClick={onDoubleClick}>
        <p className="truncate text-center text-sm font-medium text-gray-700 px-2">
          {item.name}
        </p>
      </div>
      
      <button
        onClick={onMenuClick}
        className="absolute top-2 right-2 p-1 hover:bg-gray-200 rounded"
      >
        <FiMoreVertical size={18} />
      </button>

      {menuOpen && (
        <div ref={menuRef} className="absolute top-8 right-2 w-40 bg-white border rounded shadow z-50">
          <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-blue-100" onClick={onRename}>
            <FiEdit2 /> Renommer
          </button>
          <button className="w-full px-4 py-2 flex items-center gap-2 text-red-600 hover:bg-red-100" onClick={onDelete}>
            <FiTrash2 /> Supprimer
          </button>
          <button className="w-full px-4 py-2 flex items-center gap-2 text-green-600 hover:bg-green-100" onClick={onDownload}>
            <FiDownload /> Télécharger
          </button>
          <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-yellow-100" onClick={onMove}>
            <FiMove /> Déplacer
          </button>
          <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-green-100" onClick={onCopy}>
            <FiCopy /> Copier
          </button>
          <button className="w-full px-4 py-2 flex items-center gap-2 hover:bg-gray-100" onClick={onProperties}>
            <FiInfo /> Propriétés
          </button>
        </div>
      )}
    </div>
  );
};

const FolderConflictDialog = ({ 
  folderName, 
  onReplace, 
  onRename, 
  onMerge, 
  onCancel 
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Dossier existant</h3>
          <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
            <FiX size={20} />
          </button>
        </div>
        
        <p className="mb-4">
          Le dossier <span className="font-semibold">"{folderName}"</span> existe déjà.
          Que souhaitez-vous faire ?
        </p>
        
        <div className="flex flex-col space-y-3">
          <button
            onClick={onReplace}
            className="flex items-center justify-between px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            <span>Remplacer le dossier existant</span>
            <FiCheck />
          </button>
          
          <button
            onClick={onRename}
            className="flex items-center justify-between px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            <span>Renommer le nouveau dossier</span>
            <FiEdit2 />
          </button>
          
          <button
            onClick={onMerge}
            className="flex items-center justify-between px-4 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200"
          >
            <span>Fusionner les dossiers</span>
            <FiCopy />
          </button>
          
          <button
            onClick={onCancel}
            className="flex items-center justify-between px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            <span>Annuler l'opération</span>
            <FiX />
          </button>
        </div>
      </div>
    </div>
  );
};
const PdfPreview = ({ fileUrl }) => {
  return (
    <iframe
      src={fileUrl}
      width="100%"
      height="100%"
      title="Aperçu PDF"
      style={{ border: "none", borderRadius: 4 }}
    />
  );
};

const MetadataPanel = ({ 
  metadata, 
  isLoading, 
  error,
  filename,
  onRefresh 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async (updatedMetadata) => {
    setIsSaving(true);
    try {
      const response = await fetch(`http://localhost:8000/upload/metadata/${encodeURIComponent(filename)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedMetadata),
      });
      
      if (!response.ok) throw new Error('Erreur lors de la sauvegarde');
      
      setIsEditing(false);
      onRefresh(); 
    } catch (err) {
      console.error('Erreur:', err);
      alert('Échec de la mise à jour des métadonnées');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-600 bg-red-50 rounded">
        <FiAlertCircle className="inline mr-2" />
        {error}
      </div>
    );
  }

  if (!metadata || Object.keys(metadata).length === 0) {
    return (
      <div className="p-4 text-gray-500">
        Aucun mots-clé disponible pour ce fichier
      </div>
    );
  }

  return (
    <div className="p-4 overflow-y-auto h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Mots-clés</h3>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
          >
            <FiEdit2 className="mr-1" /> Modifier
          </button>
        )}
      </div>
      
      {isEditing ? (
        <MetadataEditor 
          metadata={metadata}
          onSave={handleSave}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <div className="space-y-4 flex-1">
          {Object.entries(metadata).map(([key, value]) => (
            <div key={key} className="bg-gray-50 p-3 rounded-lg">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                {key.replace(/_/g, ' ')}
              </div>
              <div className="mt-1 text-sm text-gray-800">
                {value && value !== "Non spécifié" ? value : null}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {isSaving && (
        <div className="mt-4 text-center text-gray-500">
          Enregistrement en cours...
        </div>
      )}
    </div>
  );
};

const FolderConflictDialogCreate = ({ 
  folderName, 
  onReplace, 
  onRename, 
  onCancel 
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Dossier existant</h3>
          <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
            <FiX size={20} />
          </button>
        </div>
        
        <p className="mb-4">
          Le dossier <span className="font-semibold">"{folderName}"</span> existe déjà.
          Que souhaitez-vous faire ?
        </p>
        
        <div className="flex flex-col space-y-3">
          <button
            onClick={onReplace}
            className="flex items-center justify-between px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            <span>Remplacer le dossier existant</span>
            <FiCheck />
          </button>
          
          <button
            onClick={onRename}
            className="flex items-center justify-between px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            <span>Renommer le nouveau dossier</span>
            <FiEdit2 />
          </button>
          
          <button
            onClick={onCancel}
            className="flex items-center justify-between px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            <span>Annuler l'opération</span>
            <FiX />
          </button>
        </div>
      </div>
    </div>
  );
};

const MetadataFilters = ({ 
  availableFilters, 
  selectedFilters, 
  onFilterChange 
}) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border mb-6">
      <h3 className="text-lg font-semibold mb-3">Filtrer par métadonnées</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {availableFilters.map(filterKey => (
          <div key={filterKey} className="flex items-center">
            <input
              type="checkbox"
              id={`filter-${filterKey}`}
              checked={selectedFilters[filterKey] || false}
              onChange={() => onFilterChange(filterKey)}
              className="mr-2"
            />
            <label htmlFor={`filter-${filterKey}`} className="capitalize">
              {filterKey.replace(/_/g, ' ')}
            </label>
          </div>
        ))}
      </div>
    </div>
  );
};

const MetadataEditor = ({ metadata, onSave, onCancel }) => {
  const [editableMetadata, setEditableMetadata] = useState({...metadata});

  const handleChange = (key, value) => {
    setEditableMetadata(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">Éditer les mots-clés</h3>
      <div className="space-y-4">
        {Object.keys(editableMetadata).map(key => (
          <div key={key} className="bg-gray-50 p-3 rounded-lg">
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              {key.replace(/_/g, ' ')}
            </label>
            <input
              type="text"
              value={editableMetadata[key] || ''}
              onChange={(e) => handleChange(key, e.target.value)}
              className="mt-1 w-full p-2 border rounded text-sm text-gray-800"
            />
          </div>
        ))}
      </div>
      <div className="flex justify-end space-x-3 mt-6">
        <button
          onClick={onCancel}
          className="px-4 py-2 border rounded hover:bg-gray-100"
        >
          Annuler
        </button>
        <button
          onClick={() => onSave(editableMetadata)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Enregistrer
        </button>
      </div>
    </div>
  );
};

const groupFilesByMetadata = async (itemsToGroup, activeFilters) => {
  if (!activeFilters || Object.keys(activeFilters).length === 0) {
    return { 'Tous les fichiers': { items: itemsToGroup, isOpen: false } };
  }

  const groups = {};
  const folders = itemsToGroup.filter(item => item.is_dir);
  const files = itemsToGroup.filter(item => !item.is_dir);

  if (folders.length > 0) {
    groups['Dossiers'] = { items: folders, isOpen: false };
  }

  try {
    const filenames = files.map(f => f.name).join(',');
    const res = await fetch(`http://localhost:8000/upload/batch_metadata?filenames=${encodeURIComponent(filenames)}`);
    
    if (!res.ok) throw new Error('Erreur de récupération des métadonnées');
    
    const allMetadata = await res.json();

    files.forEach(file => {
      const metadata = allMetadata[file.name] || {};
      const groupKeys = Object.keys(activeFilters)
        .filter(key => activeFilters[key])
        .map(key => metadata[key] || 'Non renseigné');

      const groupName = groupKeys.join(' - ') || 'Sans métadonnées';
      
      if (!groups[groupName]) {
        groups[groupName] = { items: [], isOpen: false };
      }
      groups[groupName].items.push(file);
    });

  } catch (error) {
    console.error("Erreur lors du regroupement:", error);
    groups['Fichiers'] = { items: files, isOpen: false };
  }

  return groups;
};


const MesDocuments = () => {
  const [items, setItems] = useState([]);
  const [currentPath, setCurrentPath] = useState('');
  const [menuOpenFor, setMenuOpenFor] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [itemToMove, setItemToMove] = useState(null);
  const [itemToCopy, setItemToCopy] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [metadataLoading, setMetadataLoading] = useState(false);
  const [metadataError, setMetadataError] = useState(null);
  const [availableMetadataFilters, setAvailableMetadataFilters] = useState([]);
  const [selectedFilters, setSelectedFilters] = useState({});
  const [groupedItems, setGroupedItems] = useState({ 
    'Tous les fichiers': { items: [], isOpen: false } 
  });
  const [conflictDialog, setConflictDialog] = useState({
    open: false,
    filename: '',
    onReplace: null,
    onRename: null,
    onCancel: null
  });
  const [folderConflictDialog, setFolderConflictDialog] = useState({
    open: false,
    folderName: '',
    onReplace: null,
    onRename: null,
    onMerge: null,
    onCancel: null
  });
  const [folderConflictDialogCreate, setFolderConflictDialogCreate] = useState({
    open: false,
    folderName: '',
    onReplace: null,
    onRename: null,
    onCancel: null
  });
  const handleFilterChange = (filterKey) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterKey]: !prev[filterKey]
    }));
  };
  const menuRef = useRef(null);

  const fetchMetadataFilters = async () => {
    try {
      const res = await fetch('http://localhost:8000/upload/metadata_keys');
      if (!res.ok) throw new Error('Erreur récupération des filtres');
      const data = await res.json();
      setAvailableMetadataFilters(data.keys);
    } catch (err) {
      console.error('Erreur récupération des filtres:', err);
    }
  };

  useEffect(() => {
    if (availableMetadataFilters.length > 0) {
      fetchItems(currentPath);
    }
  }, [selectedFilters]);


  useEffect(() => {
    const groupItems = async () => {
      const grouped = await groupFilesByMetadata(items, selectedFilters);
      setGroupedItems(grouped);
    };
  
    groupItems();
  }, [items, selectedFilters]);

  useEffect(() => {
    fetchItems('');
    fetchMetadataFilters();

    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpenFor(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
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
  }, [searchTerm, currentPath]);


  const fetchItems = async (path) => {
    try {
      let url = `http://localhost:8000/explorer/?path=${encodeURIComponent(path)}`;
      
      const activeFilters = Object.keys(selectedFilters).filter(key => selectedFilters[key]);
      if (activeFilters.length > 0) {
        url += `&metadata=${encodeURIComponent(activeFilters.join(','))}`;
      }
  
      const res = await fetch(url);
      if (!res.ok) throw new Error('Erreur chargement des fichiers');
      const data = await res.json();
      setItems(data.items);
      setCurrentPath(data.current_path);
      setMenuOpenFor(null);
    } catch (error) {
      console.error('Erreur chargement :', error);
      setItems([]);
    }
  };

  const fetchMetadata = async (filename) => {
    setMetadataLoading(true);
    setMetadataError(null);
    try {
      const response = await fetch(`http://localhost:8000/upload/metadata/${encodeURIComponent(filename)}`);
      if (!response.ok) throw new Error('Erreur lors de la récupération des métadonnées');
      const data = await response.json();
      return data.success ? data.metadata : null;
    } catch (error) {
      console.error("Erreur:", error);
      setMetadataError(error.message);
      return null;
    } finally {
      setMetadataLoading(false);
    }
  };

  const handleFileConflict = (filename) => {
    return new Promise((resolve) => {
      setConflictDialog({
        open: true,
        filename,
        onReplace: () => {
          setConflictDialog({ ...conflictDialog, open: false });
          resolve('replace');
        },
        onRename: () => {
          setConflictDialog({ ...conflictDialog, open: false });
          resolve('rename');
        },
        onCancel: () => {
          setConflictDialog({ ...conflictDialog, open: false });
          resolve('cancel');
        }
      });
    });
  };

  const handleFolderConflict = (folderName) => {
    return new Promise((resolve) => {
      setFolderConflictDialog({
        open: true,
        folderName,
        onReplace: () => {
          setFolderConflictDialog({ ...folderConflictDialog, open: false });
          resolve('replace');
        },
        onRename: () => {
          setFolderConflictDialog({ ...folderConflictDialog, open: false });
          resolve('rename');
        },
        onMerge: () => {
          setFolderConflictDialog({ ...folderConflictDialog, open: false });
          resolve('merge');
        },
        onCancel: () => {
          setFolderConflictDialog({ ...folderConflictDialog, open: false });
          resolve('cancel');
        }
      });
    });
  };

  const handleFolderConflictCreate = (folderName) => {
    return new Promise((resolve) => {
      setFolderConflictDialogCreate({
        open: true,
        folderName,
        onReplace: () => {
          setFolderConflictDialogCreate({ ...folderConflictDialogCreate, open: false });
          resolve('replace');
        },
        onRename: () => {
          setFolderConflictDialogCreate({ ...folderConflictDialogCreate, open: false });
          resolve('rename');
        },
        onCancel: () => {
          setFolderConflictDialogCreate({ ...folderConflictDialogCreate, open: false });
          resolve('cancel');
        }
      });
    });
  };

  const handleFolderClick = (path) => {
    fetchItems(path);
    setSearchTerm('');
  };

  const goBack = () => {
    const parts = currentPath.split('/').filter(Boolean);
    parts.pop();
    fetchItems(parts.join('/'));
    setSearchTerm('');
  };

  const openCreateModal = () => {
    setShowCreateModal(true);
  };

  const generateUniqueFolderName = async (baseName, path) => {
    let counter = 1;
    let newName = baseName;
    
    const checkExists = async (name) => {
      try {
        const res = await fetch(`http://localhost:8000/explorer/?path=${encodeURIComponent(path)}`);
        if (!res.ok) return false;
        const data = await res.json();
        return data.items.some(item => item.is_dir && item.name === name);
      } catch {
        return false;
      }
    };
    
    while (await checkExists(newName)) {
      newName = `${baseName}(${counter})`;
      counter++;
    }
    
    return newName;
  };

  const createFolder = async (folderName) => {
    if (!folderName.trim()) {
      alert('Le nom du dossier est obligatoire');
      return;
    }
  
    const forbiddenPatterns = Object.keys(validExtensions).map(ext => `.${ext}$`);
    const regex = new RegExp(forbiddenPatterns.join('|'), 'i');
    
    if (regex.test(folderName)) {
      alert('Le nom du dossier ne peut pas ressembler à une extension de fichier');
      return;
    }
  
    try {
      const folderExists = items.some(item => item.is_dir && item.name === folderName.trim());
      
      let action = 'create';
      let finalFolderName = folderName.trim();
      
      if (folderExists) {
        const userChoice = await handleFolderConflictCreate(folderName);
        
        if (userChoice === 'cancel') {
          return;
        }
        
        if (userChoice === 'rename') {
          finalFolderName = await generateUniqueFolderName(folderName.trim(), currentPath);
          action = 'create';
        } else if (userChoice === 'replace') {
          action = 'replace';
        }
      }
  
      const formData = new FormData();
      formData.append('path', currentPath);
      formData.append('folder_name', finalFolderName);
      formData.append('action', action);
  
      const res = await fetch('http://localhost:8000/explorer/create_folder', {
        method: 'POST',
        body: formData,
      });
  
      if (!res.ok) throw new Error(await res.text());
  
      alert(`Dossier '${finalFolderName}' ${action === 'replace' ? 'remplacé' : 'créé'} avec succès !`);
      setShowCreateModal(false);
      setNewFolderName('');
      fetchItems(currentPath);
    } catch (e) {
      alert('Erreur lors de la création du dossier');
      console.error(e);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
  
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!validExtensions[fileExtension]) {
      const allowedExtensions = Object.values(validExtensions).join(', ');
      alert(`Type de fichier non autorisé. Extensions autorisées : ${allowedExtensions}`);
      return;
    }
  
    const fileExists = items.some(item => !item.is_dir && item.name === file.name);
  
    let uploadFile = file;
    
    if (fileExists) {
      const action = await handleFileConflict(file.name);
      
      if (action === 'cancel') {
        e.target.value = '';
        return;
      }
      
      if (action === 'rename') {
        const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, "");
        const fileExt = file.name.split('.').pop();
        
        let counter = 1;
        let newName;
        do {
          newName = `${fileNameWithoutExt}(${counter}).${fileExt}`;
          counter++;
        } while (items.some(item => item.name === newName));
        
        uploadFile = new File([file], newName, { type: file.type });
      }
    }
  
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('path', currentPath);
  
    try {
      const res = await fetch('http://localhost:8000/explorer/file', {
        method: 'POST',
        body: formData,
      });
  
      if (res.ok) {
        alert(`Fichier ${uploadFile.name} téléversé avec succès !`);
        fetchItems(currentPath);
      } else {
        throw new Error(await res.text());
      }
    } catch (error) {
      console.error('Erreur upload:', error);
      alert(`Échec du téléversement : ${error.message}`);
    } finally {
      e.target.value = '';
    }
  };

  const handleFolderUpload = async (e) => {
    const files = Array.from(e.target.files);
    const validFiles = [];
    const invalidFiles = [];
  
    files.forEach(file => {
      const fileExtension = file.name.split('.').pop().toLowerCase();
      if (validExtensions[fileExtension]) {
        validFiles.push(file);
      } else {
        invalidFiles.push(file.name);
      }
    });
  
    if (invalidFiles.length > 0) {
      const allowedExtensions = Object.values(validExtensions).join(', ');
      const shouldContinue = confirm(
        `${invalidFiles.length} fichier(s) non autorisés seront ignorés.\n` +
        `Extensions autorisées : ${allowedExtensions}\n\n` +
        `Continuer avec ${validFiles.length} fichier(s) valide(s) ?`
      );
  
      if (!shouldContinue) {
        e.target.value = '';
        return;
      }
    }
  
    if (validFiles.length === 0) {
      alert("Aucun fichier valide à importer");
      e.target.value = '';
      return;
    }
  
    const folderNames = [...new Set(validFiles.map(f => f.webkitRelativePath.split('/')[0]))];
  
    for (const folderName of folderNames) {
      const folderExists = items.some(item => item.is_dir && item.name === folderName);
  
      if (folderExists) {
        const action = await handleFolderConflict(folderName);
  
        if (action === 'cancel') {
          e.target.value = '';
          return;
        }
  
        if (action === 'replace') {
          try {
            const res = await fetch('http://localhost:8000/explorer/delete_folder', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                path: currentPath ? `${currentPath}/${folderName}` : folderName,
              }),
            });
  
            if (!res.ok) throw new Error('Échec suppression dossier');
          } catch (error) {
            console.error('Erreur suppression:', error);
            alert(`Échec suppression du dossier ${folderName}`);
            e.target.value = '';
            return;
          }
        }
      }
    }

    const groupFilesByMetadata = (items, filters) => {
      if (!filters || Object.keys(filters).length === 0) {
        return { 'Tous les fichiers': items };
      }
    
      const groups = {};
      
      items.forEach(item => {
        if (!item.is_dir) {
          fetchMetadata(item.name).then(metadata => {
            const groupKeys = Object.keys(activeFilters)
              .filter(key => activeFilters[key])
              .map(key => metadata[key] || null)
              .filter(val => val !== null); 
    
            if (groupKeys.length > 0) {
              const groupName = groupKeys.join(' - ');
              if (!groups[groupName]) {
                groups[groupName] = [];
              }
              groups[groupName].push(item);
            } else {
              if (!groups['Autres']) {
                groups['Autres'] = [];
              }
              groups['Autres'].push(item);
            }
          });
        } else {
          if (!groups['Dossiers']) {
            groups['Dossiers'] = [];
          }
          groups['Dossiers'].push(item);
        }
      });
    
      return groups;
    };
    
  
    for (const file of validFiles) {
      const fileExists = items.some(
        item =>
          !item.is_dir &&
          item.name === file.name &&
          item.path.startsWith(currentPath + (currentPath ? '/' : ''))
      );
  
      let finalFile = file;
  
      if (fileExists) {
        const action = await handleFileConflict(file.name);
  
        if (action === 'cancel') {
          e.target.value = '';
          return;
        }
  
        if (action === 'rename') {
          const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, "");
          const fileExt = file.name.split('.').pop();
  
          let counter = 1;
          let newName;
          do {
            newName = `${fileNameWithoutExt}(${counter}).${fileExt}`;
            counter++;
          } while (items.some(item => item.name === newName));
  
          finalFile = new File([file], newName, { type: file.type });
        }
      }
  
      try {
        const formData = new FormData();
        formData.append('file', finalFile);
        formData.append('path', currentPath);
  
        let relativePath = file.webkitRelativePath || '';
        if (relativePath) {
          const parts = relativePath.split('/');
          parts[parts.length - 1] = finalFile.name;
          relativePath = parts.join('/');
        }
        formData.append('relative_path', relativePath);
  
        const res = await fetch('http://localhost:8000/explorer/folder', {
          method: 'POST',
          body: formData,
        });
  
        if (!res.ok) throw new Error('Échec upload');
      } catch (error) {
        console.error(`Erreur sur ${file.name}:`, error);
        alert(`Échec importation de ${file.name}`);
        e.target.value = '';
        return;
      }
    }
  
    alert(`${validFiles.length} fichier(s) importé(s) avec succès !`);
    e.target.value = '';
    fetchItems(currentPath);
  };

  const renameItem = async (item) => {
    const lastDotIndex = item.name.lastIndexOf('.');
    const isDir = item.is_dir;
    const nameWithoutExtension = isDir ? item.name : item.name.substring(0, lastDotIndex);
    const extension = isDir ? '' : item.name.substring(lastDotIndex);
  
    let newName;
    let attempts = 0;
    const maxAttempts = 5;
    
    do {
      attempts++;
      newName = prompt(
        `Nouveau nom${isDir ? '' : ' (ne modifiez pas l\'extension)'}:`,
        nameWithoutExtension
      );
      
      if (!newName) return;
      
      if (isDir) {
        newName = newName.trim();
      } else {
        newName = newName.trim() + extension;
      }
      
      const nameExists = items.some(i => i.name === newName && i.path !== item.path);
      
      if (!nameExists) break;
      
      if (attempts >= maxAttempts) {
        alert('Trop de tentatives. Opération annulée.');
        return;
      }
      
      alert(`Le nom "${newName}" est déjà utilisé. Veuillez choisir un autre nom.`);
    } while (true);
  
    try {
      const res = await fetch('http://localhost:8000/explorer/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          old_path: currentPath ? `${currentPath}/${item.name}` : item.name,
          new_name: newName,
        }),
      });
  
      if (!res.ok) throw new Error('Erreur renommage');
      alert('Renommé avec succès');
      fetchItems(currentPath);
    } catch (e) {
      alert('Erreur lors du renommage');
      console.error(e);
    }
    setMenuOpenFor(null);
  };

  const deleteItem = async (item) => {
    if (!window.confirm(`Déplacer '${item.name}' vers la Corbeille ?`)) return;

    try {
      const res = await fetch('http://localhost:8000/trash/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          old_path: currentPath ? `${currentPath}/${item.name}` : item.name,
        }),
      });

      if (!res.ok) throw new Error('Erreur déplacement');
      alert('Déplacé vers la Corbeille');
      fetchItems(currentPath);
    } catch (e) {
      alert('Erreur lors du déplacement');
      console.error(e);
    }
    setMenuOpenFor(null);
  };

  const downloadItem = (item) => {
    if (item.is_dir) {
      alert('Téléchargement des dossiers non supporté');
      setMenuOpenFor(null);
      return;
    }
    const url = `http://localhost:8000/uploads/${encodeURIComponent(item.path)}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = item.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setMenuOpenFor(null);
  };

  const handleMoveConflict = async (item, destinationPath) => {
    try {
      const res = await fetch(`http://localhost:8000/explorer/?path=${encodeURIComponent(destinationPath)}`);
      if (!res.ok) throw new Error('Erreur vérification conflit');
      const data = await res.json();
      
      const existingItem = data.items.find(i => i.name === item.name);
      if (!existingItem) return 'proceed';
      
      if (item.is_dir) {
        const action = await handleFolderConflict(item.name);
        return action;
      } else {
        const action = await handleFileConflict(item.name);
        return action;
      }
    } catch (error) {
      console.error('Erreur vérification conflit:', error);
      return 'cancel';
    }
  };

  const displayItems = searchTerm.trim() ? searchResults : items;

  return (
    <>
      <Navbar
        searchTerm={searchTerm}
        onSearch={setSearchTerm}
        onCreateFolder={openCreateModal}
        onCreateFolderSubmit={createFolder}
        onAddFile={handleFileUpload}
        onAddFolder={handleFolderUpload}
      />

      <div className="p-6 max-w-7xl mx-auto">
        {currentPath && (
          <button onClick={goBack} className="mb-6 text-blue-600 hover:underline">
            ← Retour
          </button>
        )}

        {availableMetadataFilters.length > 0 && (
          <MetadataFilters
            availableFilters={availableMetadataFilters}
            selectedFilters={selectedFilters}
            onFilterChange={handleFilterChange}
          />
        )}


        {itemToMove && (
          <div className="bg-gray-100 p-2 mb-4 flex justify-end gap-2 items-center border border-gray-200">
            <span className="mr-auto text-gray-700">Déplacer <strong>{itemToMove.name}</strong> ici ?</span>
            <button
              onClick={async () => {
                try {
                  const destinationPath = currentPath || '';
                  const conflictAction = await handleMoveConflict(itemToMove, destinationPath);
                  
                  if (conflictAction === 'cancel') {
                    setItemToMove(null);
                    return;
                  }
                  
                  let finalName = itemToMove.name;
                  if (conflictAction === 'rename') {
                    const baseName = itemToMove.name.replace(/\.[^/.]+$/, "");
                    const extension = itemToMove.is_dir ? '' : `.${itemToMove.name.split('.').pop()}`;
                    
                    let counter = 1;
                    let newName;
                    const res = await fetch(`http://localhost:8000/explorer/?path=${encodeURIComponent(destinationPath)}`);
                    const data = await res.json();
                    
                    do {
                      newName = `${baseName}(${counter})${extension}`;
                      counter++;
                    } while (data.items.some(item => item.name === newName));
                    
                    finalName = newName;
                  }
                  
                  const res = await fetch('http://localhost:8000/explorer/move_item', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      source: itemToMove.path,
                      destination: destinationPath,
                      new_name: conflictAction === 'rename' ? finalName : undefined,
                      overwrite: conflictAction === 'replace'
                    }),
                  });
                  
                  if (res.ok) {
                    alert(conflictAction === 'replace' ? 'Élément remplacé' : 'Élément déplacé');
                    fetchItems(currentPath);
                    setItemToMove(null);
                  } else {
                    throw new Error(await res.text());
                  }
                } catch (error) {
                  console.error('Erreur déplacement:', error);
                  alert(`Échec du déplacement: ${error.message}`);
                }
              }}
              className="bg-gray-600 text-white px-3 py-1 rounded flex items-center gap-2 hover:bg-gray-700"
            >
              <FiMove /> Confirmer
            </button>
            <button
              onClick={() => setItemToMove(null)}
              className="bg-gray-300 px-3 py-1 rounded flex items-center gap-2 text-gray-700 hover:bg-gray-400"
            >
              Annuler
            </button>
          </div>
        )}

        {itemToCopy && (
          <div className="bg-gray-100 p-2 mb-4 flex justify-end gap-2 items-center border border-gray-200">
            <span className="mr-auto text-gray-700">Coller <strong>{itemToCopy.name}</strong> ici ?</span>
            <button
              onClick={async () => {
                const res = await fetch('http://localhost:8000/explorer/copy_item', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    source: itemToCopy.path,
                    destination: currentPath || '',
                  }),
                });
                if (res.ok) {
                  alert('Copié');
                  fetchItems(currentPath);
                  setItemToCopy(null);
                } else {
                  alert('Erreur copie');
                }
              }}
              className="bg-gray-600 text-white px-3 py-1 rounded flex items-center gap-2 hover:bg-gray-700"
            >
              <FiCopy /> Confirmer
            </button>
            <button
              onClick={() => setItemToCopy(null)}
              className="bg-gray-300 px-3 py-1 rounded flex items-center gap-2 text-gray-700 hover:bg-gray-400"
            >
              Annuler
            </button>
          </div>
        )}

{Object.keys(selectedFilters).filter(key => selectedFilters[key]).length > 0 ? (
  <div className="space-y-6">
    {Object.entries(groupedItems).map(([groupName, groupItems]) => (
      <div key={groupName} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <div 
          className="flex justify-between items-center cursor-pointer"
          onClick={() => {
            setGroupedItems(prev => ({
              ...prev,
              [groupName]: {
                items: prev[groupName].items,
                isOpen: !prev[groupName].isOpen
              }
            }));
          }}
        >
          <h3 className="text-lg font-semibold flex items-center">
            <FiFolder className="mr-2 text-yellow-500" />
            {groupName} <span className="ml-2 text-sm font-normal text-gray-500">({groupItems.items.length})</span>
          </h3>
          <span className="text-gray-500">
            {groupItems.isOpen ? <FiX size={18} /> : <FiFolder size={18} />}
          </span>
        </div>

        {groupItems.isOpen && (
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {groupItems.items.map((item, index) => (
              <div
                key={index}
                className="relative bg-white rounded-lg shadow p-4 flex flex-col items-center hover:shadow-md transition"
                title={item.name}
                onDoubleClick={() => {
                  if (item.is_dir) {
                    handleFolderClick(item.path);
                  } else if (item.name.toLowerCase().endsWith('.pdf')) {
                    const url = `http://localhost:8000/upload/file/${encodeURIComponent(item.name)}`;
                    setSelectedFile({
                      name: item.name,
                      url
                    });
                    fetchMetadata(item.name).then(data => setMetadata(data));
                  } else {
                    window.open(`http://localhost:8000/uploads/${item.path}`, '_blank');
                  }
                }}
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
              </div>
            ))}
          </div>
        )}
      </div>
    ))}
  </div>
) : (

  <div className="space-y-6">
    {/* Section Dossiers */}
    {displayItems.filter(item => item.is_dir).length > 0 && (
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FiFolder className="mr-2 text-yellow-500" />
          Dossiers
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {displayItems.filter(item => item.is_dir).map((item, index) => (
            <FolderItem 
              key={`dir-${index}`} 
              item={item} 
              onDoubleClick={() => handleFolderClick(item.path)}
              onMenuClick={() => setMenuOpenFor(item.path === menuOpenFor ? null : item.path)}
              menuOpen={menuOpenFor === item.path}
              menuRef={menuRef}
              onRename={() => renameItem(item)}
              onDelete={() => deleteItem(item)}
              onMove={() => setItemToMove(item)}
              onCopy={() => setItemToCopy(item)}
              onProperties={() => setSelectedItem(item)}
            />
          ))}
        </div>
      </div>
    )}

    {/* Section Fichiers */}
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <FiFileText className="mr-2 text-blue-500" />
        Fichiers
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
        {displayItems.filter(item => !item.is_dir).map((item, index) => (
          <FileItem
            key={`file-${index}`}
            item={item}
            onDoubleClick={() => {
              if (item.name.toLowerCase().endsWith('.pdf')) {
                const url = `http://localhost:8000/upload/file/${encodeURIComponent(item.name)}`;
                setSelectedFile({ name: item.name, url });
                fetchMetadata(item.name).then(data => setMetadata(data));
              } else {
                window.open(`http://localhost:8000/uploads/${item.path}`, '_blank');
              }
            }}
            onMenuClick={() => setMenuOpenFor(item.path === menuOpenFor ? null : item.path)}
            menuOpen={menuOpenFor === item.path}
            menuRef={menuRef}
            onRename={() => renameItem(item)}
            onDelete={() => deleteItem(item)}
            onDownload={() => downloadItem(item)}
            onMove={() => setItemToMove(item)}
            onCopy={() => setItemToCopy(item)}
            onProperties={() => setSelectedItem(item)}
          />
        ))}
      </div>
    </div>
  </div>
)}

      </div>

      {selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h3 className="text-lg font-semibold mb-4">Propriétés</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li><strong>Nom :</strong> {selectedItem.name}</li>
              <li><strong>Taille :</strong> {selectedItem.size || 'Calcul en cours...'}</li>
              <li><strong>Date de création :</strong> {selectedItem.creation_date || 'Non disponible'}</li>
              <li><strong>Chemin :</strong> {selectedItem.path}</li>
            </ul>
            <button onClick={() => setSelectedItem(null)} className="mt-4 px-3 py-1 bg-blue-600 text-white rounded">
              Fermer
            </button>
          </div>
        </div>
      )}

      {selectedFile && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div className="absolute inset-0 bg-black bg-opacity-50"></div>
          <div className="absolute inset-5 bg-white rounded-xl shadow-2xl flex flex-col">
            <div className="flex justify-between items-center border-b p-4">
              <h3 className="text-lg font-semibold text-gray-800 truncate">
                {selectedFile.name}
              </h3>
              <button
                onClick={() => {
                  setSelectedFile(null);
                  setMetadata(null);
                  setMetadataError(null);
                }}
                className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100"
              >
                <FiX size={24} />
              </button>
            </div>
            <div className="flex-1 flex overflow-hidden">
              <div className="flex-1 overflow-auto">
                <PdfPreview fileUrl={selectedFile.url} />
              </div>
              <div className="w-80 border-l overflow-auto">
                <MetadataPanel 
                  metadata={metadata} 
                  isLoading={metadataLoading}
                  error={metadataError}
                  filename={selectedFile?.name}
                  onRefresh={() => {
                    fetchMetadata(selectedFile.name).then(data => setMetadata(data));
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white rounded p-6 shadow-lg w-80">
            <h3 className="text-lg font-semibold mb-4">Créer un nouveau dossier</h3>
            <input
              type="text"
              placeholder="Nom du dossier"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 mb-4"
            />
            <div className="flex justify-end space-x-4">
              <button onClick={() => { setShowCreateModal(false); setNewFolderName(''); }} className="px-3 py-1 border rounded">
                Annuler
              </button>
              <button onClick={() => createFolder(newFolderName)} className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                Créer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dialogue de conflit de fichiers */}
      {conflictDialog.open && (
        <FileConflictDialog
          filename={conflictDialog.filename}
          onReplace={conflictDialog.onReplace}
          onRename={conflictDialog.onRename}
          onCancel={conflictDialog.onCancel}
        />
      )}

      {/* Dialogue de conflit de dossiers */}
      {folderConflictDialog.open && (
        <FolderConflictDialog
          folderName={folderConflictDialog.folderName}
          onReplace={folderConflictDialog.onReplace}
          onRename={folderConflictDialog.onRename}
          onMerge={folderConflictDialog.onMerge}
          onCancel={folderConflictDialog.onCancel}
        />
      )}

      {folderConflictDialogCreate.open && (
        <FolderConflictDialogCreate
          folderName={folderConflictDialogCreate.folderName}
          onReplace={folderConflictDialogCreate.onReplace}
          onRename={folderConflictDialogCreate.onRename}
          onCancel={folderConflictDialogCreate.onCancel}
        />
      )}
    </>
  );
};

export default MesDocuments;