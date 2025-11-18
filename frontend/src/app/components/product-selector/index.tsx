"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

interface ProductSelectorProps {
  selectedCategories: string[];
  onChange: (categories: string[]) => void;
}

const CATEGORIES = {
  Cocina: ["Aceite", "Arroz", "Pasta", "Harina", "Azúcar", "Sal", "Especias"],
  Despensa: ["Yerba", "Café", "Té", "Galletas", "Conservas", "Legumbres"],
  Bebidas: [
    "Agua",
    "Gaseosas",
    "Jugo",
    "Vino",
    "Cerveza",
    "Bebidas sin alcohol",
  ],
  Limpieza: [
    "Detergente",
    "Desinfectante",
    "Jabón",
    "Escoba",
    "Trapo",
    "Papel",
  ],
  "Higiene Personal": [
    "Jabón",
    "Champú",
    "Pasta dental",
    "Papel higiénico",
    "Pañuelos",
  ],
  Baño: ["Toallas", "Cortina", "Esponja", "Cepillo", "Accesorios"],
  Habitación: ["Almohadas", "Sábanas", "Colcha", "Cortinas", "Lámpara"],
  Electrónica: ["Bombillas", "Baterías", "Cables", "Adaptadores"],
};

export default function ProductSelector({
  selectedCategories,
  onChange,
}: ProductSelectorProps) {
  const [openCategory, setOpenCategory] = useState<string | null>(null);

  const toggleCategory = (category: string) => {
    const isSelected = selectedCategories.includes(category);
    if (isSelected) {
      onChange(selectedCategories.filter((c) => c !== category));
    } else {
      onChange([...selectedCategories, category]);
    }
    setOpenCategory(openCategory === category ? null : category);
  };

  return (
    <div className="space-y-2">
      {Object.entries(CATEGORIES).map(([category, products]) => (
        <div key={category}>
          <button
            onClick={() => toggleCategory(category)}
            className={`w-full flex items-center justify-between px-4 py-3 rounded-lg border transition-all ${
              selectedCategories.includes(category)
                ? "bg-cyan-500/20 border-cyan-400 text-cyan-100"
                : "bg-slate-700/30 border-slate-600 text-slate-300 hover:bg-slate-700/50"
            }`}
          >
            <span className="font-medium">{category}</span>
            <ChevronDown
              className={`w-5 h-5 transition-transform ${
                openCategory === category ? "rotate-180" : ""
              }`}
            />
          </button>

          {/* Dropdown Products */}
          {openCategory === category && (
            <div className="mt-2 pl-2 space-y-2 bg-slate-700/20 rounded-lg p-3 border border-slate-700/30">
              {products.map((product) => (
                <div
                  key={product}
                  className="flex items-center gap-2 px-3 py-2 rounded-md bg-slate-700/30 text-slate-300 text-sm"
                >
                  <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
                  {product}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
