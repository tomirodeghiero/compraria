/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState } from "react";
import { Upload, ChevronDown, Plus, Trash2, Loader2 } from "lucide-react";

interface InventoryUploadProps {
  onSubmit: (data: any) => void;
  loading: boolean;
}

const CATEGORIES = {
  Cocina: [
    "Aceite",
    "Arroz",
    "Pasta",
    "Harina",
    "Azúcar",
    "Sal",
    "Fideos",
    "Enlatados",
  ],
  Despensa: [
    "Yerba",
    "Café",
    "Té",
    "Galletitas",
    "Conservas",
    "Legumbres",
    "Aceitunas",
  ],
  Bebidas: ["Agua", "Gaseosa", "Jugo", "Vino", "Cerveza", "Fernet"],
  Limpieza: [
    "Detergente",
    "Lavandina",
    "Jabón en pan",
    "Rollo de cocina",
    "Bolsas de residuos",
  ],
  "Higiene Personal": [
    "Jabón líquido",
    "Champú",
    "Pasta dental",
    "Papel higiénico",
    "Desodorante",
  ],
  Lácteos: ["Leche", "Queso", "Manteca", "Yogur", "Dulce de leche"],
  Carnicería: ["Carne picada", "Asado", "Pollo", "Chorizo", "Morcilla"],
};

interface SelectedProduct {
  category: string;
  product: string;
  quantity: number;
}

export default function InventoryUpload({
  onSubmit,
  loading,
}: InventoryUploadProps) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const [selectedProducts, setSelectedProducts] = useState<SelectedProduct[]>(
    []
  );
  const [budget, setBudget] = useState(85000);
  const [persons, setPersons] = useState(4);
  const [preferences, setPreferences] = useState(
    "mucho asado los domingos, sin TACC"
  );

  const toggleCategory = (category: string) => {
    setExpandedCategory(expandedCategory === category ? null : category);
  };

  const addProduct = (category: string, product: string) => {
    if (!selectedProducts.find((p) => p.product === product)) {
      setSelectedProducts([
        ...selectedProducts,
        { category, product, quantity: 0 },
      ]);
    }
  };

  const removeProduct = (product: string) => {
    setSelectedProducts(selectedProducts.filter((p) => p.product !== product));
  };

  const updateQuantity = (product: string, quantity: number) => {
    setSelectedProducts(
      selectedProducts.map((p) =>
        p.product === product ? { ...p, quantity: Math.max(0, quantity) } : p
      )
    );
  };

  const handleSubmit = () => {
    const inventario_actual = selectedProducts.reduce((acc, item) => {
      if (item.quantity > 0) {
        acc[item.product] = item.quantity;
      }
      return acc;
    }, {} as Record<string, number>);

    if (Object.keys(inventario_actual).length === 0) {
      alert("Por favor indicá la cantidad que tenés de al menos un producto");
      return;
    }

    onSubmit({
      inventario_actual,
      presupuesto: budget,
      personas: persons,
      preferencias: preferences,
    });
  };

  return (
    <div className="space-y-8">
      {/* Step 1: Select Products */}
      <div className="bg-gray-50 border-2 border-gray-200 rounded-2xl p-8">
        <div className="flex items-center gap-2 mb-6">
          <div className="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full font-semibold text-sm">
            1
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            ¿Qué tenés en casa ahora?
          </h2>
        </div>

        <div className="space-y-3">
          {Object.entries(CATEGORIES).map(([category, products]) => (
            <div key={category}>
              <button
                onClick={() => toggleCategory(category)}
                className="w-full flex items-center justify-between px-6 py-4 bg-white border-2 border-gray-300 rounded-xl hover:border-blue-400 hover:shadow-md transition-all font-medium text-black"
              >
                <span className="text-lg">{category}</span>
                <ChevronDown
                  className={`w-6 h-6 transition-transform ${
                    expandedCategory === category ? "rotate-180" : ""
                  }`}
                />
              </button>

              {expandedCategory === category && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 p-4 bg-blue-50 rounded-xl border-2 border-blue-200">
                  {products.map((product) => {
                    const selected = selectedProducts.find(
                      (p) => p.product === product
                    );
                    return (
                      <button
                        key={product}
                        onClick={() =>
                          selected
                            ? removeProduct(product)
                            : addProduct(category, product)
                        }
                        className={`p-4 rounded-lg border-2 font-medium transition-all ${
                          selected
                            ? "bg-blue-600 text-white border-blue-600 shadow-lg"
                            : "bg-white text-gray-800 border-gray-300 hover:border-blue-400 hover:bg-blue-50"
                        }`}
                      >
                        {selected ? "✓ " : "+ "} {product}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Selected Products with Quantity */}
      {selectedProducts.length > 0 && (
        <div className="text-black from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-2xl p-8">
          <h3 className="text-2xl font-bold mb-6 text-center">
            Cantidad actual en casa ({selectedProducts.length} productos)
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {selectedProducts.map((item) => (
              <div
                key={item.product}
                className="bg-white rounded-xl p-5 border-2 border-blue-200 flex items-center justify-between"
              >
                <div>
                  <p className="font-bold text-gray-900">{item.product}</p>
                  <p className="text-sm text-gray-600">{item.category}</p>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={item.quantity}
                    onChange={(e) =>
                      updateQuantity(
                        item.product,
                        parseFloat(e.target.value) || 0
                      )
                    }
                    className="w-24 px-3 py-2 border-2 border-gray-300 rounded-lg text-center font-semibold"
                    placeholder="0"
                  />
                  <button
                    onClick={() => removeProduct(item.product)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Budget, Persons, Preferences */}
      <div className="bg-gray-50 border-2 border-gray-200 rounded-2xl p-8 text-black">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <label className="block text-lg font-bold mb-3">
              💰 Presupuesto mensual
            </label>
            <input
              type="number"
              className="w-full px-5 py-4 border-2 border-gray-300 rounded-xl text-xl font-bold text-center"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
            />
            <p className="text-center mt-2 text-gray-600">
              ${budget.toLocaleString()}
            </p>
          </div>
          <div>
            <label className="block text-lg font-bold mb-3">
              👥 Personas en casa
            </label>
            <input
              type="number"
              className="w-full px-5 py-4 border-2 border-gray-300 rounded-xl text-xl font-bold text-center"
              value={persons}
              onChange={(e) => setPersons(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="block text-lg font-bold mb-3">
              ❤️ Preferencias
            </label>
            <input
              type="text"
              className="w-full px-5 py-4 border-2 border-gray-300 rounded-xl"
              placeholder="ej: vegetariano, mucho fernet..."
              value={preferences}
              onChange={(e) => setPreferences(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={loading || selectedProducts.length === 0}
        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 text-white text-2xl font-bold py-6 rounded-2xl flex items-center justify-center gap-4 transition-all transform hover:scale-105 disabled:scale-100 shadow-2xl"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin w-10 h-10" />
            <span>La IA está pensando qué comprarte...</span>
          </>
        ) : (
          <>
            <Upload className="w-10 h-10" />
            <span>¡ANALIZAR MI DESPENSA CON IA!</span>
          </>
        )}
      </button>
    </div>
  );
}
