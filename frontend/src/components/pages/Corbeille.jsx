import React, { useEffect, useState } from "react";
import { FiFolder, FiFileText, FiRotateCw, FiTrash2, FiInfo } from "react-icons/fi";


const Corbeille = () => {
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetchTrashItems();
  }, []);

  const fetchTrashItems = async () => {
    try {
      const res = await fetch("http://localhost:8000/trash/");
      if (!res.ok) throw new Error("Erreur chargement corbeille");
      const data = await res.json();
      setItems(data);  
    } catch (err) {
      console.error("Erreur chargement corbeille", err);
    }
  };
  

  const restoreItem = async (item) => {
    try {
      const res = await fetch("http://localhost:8000/trash/restore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: item.id }),
      });
      if (!res.ok) throw new Error("Erreur restauration");
      alert("Restauré avec succès");
      fetchTrashItems();
    } catch (e) {
      alert("Erreur lors de la restauration");
      console.error(e);
    }
  };
  
  

  const deleteItemForever = async (item) => {
    const confirm = window.confirm(`Supprimer définitivement '${item.name}' ?`);
    if (!confirm) return;
    try {
      const res = await fetch("http://localhost:8000/trash/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: item.id }),
      });
      if (!res.ok) throw new Error("Erreur suppression");
      fetchTrashItems();
    } catch (err) {
      alert("Erreur suppression");
      console.error(err);
    }
  };
  

  const emptyTrash = async () => {
    const confirm = window.confirm("Voulez-vous vraiment vider toute la corbeille ?");
    if (!confirm) return;
    try {
      const res = await fetch("http://localhost:8000/trash/empty", {
        method: "POST",
      });
      if (!res.ok) throw new Error("Erreur vidage");
      fetchTrashItems();
    } catch (err) {
      alert("Erreur vidage");
      console.error(err);
    }
  };

  const [selectedItem, setSelectedItem] = useState(null);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
      <h2 className="text-3xl font-semibold text-gray-800 mb-8">Corbeille</h2>
        <button
          onClick={emptyTrash}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Vider la corbeille
        </button>
      </div>

      {items.length === 0 ? (
        <p className="text-gray-500">La corbeille est vide.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {items.map((item, index) => (
            <div
            key={index}
            className="relative bg-white rounded-lg shadow-sm p-4 flex flex-col items-center "
            title={item.name}

            
          >
            <div className="text-red-500 mb-3">
              {item.is_dir ? <FiFolder size={40} /> : <FiFileText size={40} />}
            </div>
            <p className="text-center text-sm font-medium text-gray-700 truncate w-full">
              {item.name}
            </p>
            <div className="flex space-x-3 mt-3">
              <button
                onClick={() => restoreItem(item)}
                title="Restaurer"
                className="text-green-600 hover:text-green-800"
              >
                <FiRotateCw size={18} />
              </button>
              <button
                onClick={() => deleteItemForever(item)}
                title="Supprimer définitivement"
                className="text-red-600 hover:text-red-800"
              >
                <FiTrash2 size={18} />
              </button>
              <button
                onClick={() => setSelectedItem(item)}
                title="Propriétés"
                className="text-gray-600 hover:text-gray-800"
              >
                <FiInfo size={18} />
              </button>
            </div>
          </div>          
          ))}
          {selectedItem && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg w-96">
              <h3 className="text-lg font-semibold mb-4">Propriétés</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li><strong>Nom :</strong> {selectedItem.name}</li>
                <li><strong>Type :</strong> {selectedItem.is_dir ? "Dossier" : "Fichier"}</li>
                <li><strong>Taille :</strong> {selectedItem.size || "—"}</li>
                <li><strong>Chemin original :</strong> {selectedItem.original_path || "Inconnu"}</li>
                <li><strong>Créé le :</strong> {selectedItem.creation_date || "Inconnu"}</li>
                <li><strong>Supprimé le :</strong> {selectedItem.deleted_at || "Inconnu"}</li>
              </ul>
              <div className="flex justify-end mt-4">
                <button
                  onClick={() => setSelectedItem(null)}
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Fermer
                </button>
              </div>
            </div>
          </div>
        )}
        </div>
      )}
    </div>
  );
};

export default Corbeille;
