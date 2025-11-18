/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import InventoryUpload from "./components/inventory-upload";
import AiAnalysis from "./components/ai-analysis";

export default function Home() {
  const [currentStep, setCurrentStep] = useState<"upload" | "analysis">(
    "upload"
  );
  const [inventory, setInventory] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleInventorySubmit = async (inventoryData: any) => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/generar-lista", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inventoryData),
      });

      if (!res.ok) throw new Error("Error del servidor");

      const data = await res.json();
      setAnalysis(data);
      setInventory(inventoryData);
      setCurrentStep("analysis");
    } catch (error: any) {
      alert("Error: " + (error.message || "No se pudo conectar al backend"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="w-8 h-8 text-blue-600" />
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900">
              ComprAR-IA
            </h1>
            <Sparkles className="w-8 h-8 text-blue-500" />
          </div>
          <p className="text-center text-lg text-gray-600 mb-2">
            La IA que recomienda qué comprar para tu hogar
          </p>
          <p className="text-center text-sm text-gray-500">
            Joaquín Mezzano & Tomás Rodeghiero – Inteligencia Artificial – UNRC
            2025
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        {currentStep === "upload" ? (
          <InventoryUpload onSubmit={handleInventorySubmit} loading={loading} />
        ) : (
          <>
            <button
              onClick={() => {
                setCurrentStep("upload");
                setAnalysis(null);
              }}
              className="mb-6 px-6 py-3 text-blue-600 hover:text-blue-800 font-medium border border-blue-300 rounded-xl hover:bg-blue-50 transition"
            >
              ← Volver a subir inventario
            </button>
            <AiAnalysis analysis={analysis} inventory={inventory} />
          </>
        )}
      </main>
    </div>
  );
}
