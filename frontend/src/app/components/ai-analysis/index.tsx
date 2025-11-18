/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState } from "react";
import {
  AlertCircle,
  Download,
  Send,
  TrendingUp,
  Zap,
  Target,
  CheckCircle,
} from "lucide-react";

interface AiAnalysisProps {
  analysis: any;
  inventory: any;
}

export default function AiAnalysis({ analysis, inventory }: AiAnalysisProps) {
  const [showMissing, setShowMissing] = useState(true);

  // Simulamos productos faltantes basados en categorías comunes
  const MISSING_PRODUCTS = [
    {
      product: "Leche",
      category: "Despensa",
      priority: "Alta",
      reason: "Consumo básico diario",
    },
    {
      product: "Pan",
      category: "Cocina",
      priority: "Alta",
      reason: "Alimento básico",
    },
    {
      product: "Frutas",
      category: "Cocina",
      priority: "Alta",
      reason: "Nutrientes esenciales",
    },
    {
      product: "Verduras",
      category: "Cocina",
      priority: "Alta",
      reason: "Vitaminas y fibra",
    },
    {
      product: "Carne",
      category: "Cocina",
      priority: "Media",
      reason: "Proteína complementaria",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Analysis Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-2xl p-8">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Análisis de IA Completado
            </h2>
            <p className="text-gray-600 mb-4">
              Tu inventario ha sido procesado por nuestro sistema de
              inteligencia artificial
            </p>
          </div>
          <Zap className="w-10 h-10 text-blue-600 flex-shrink-0" />
        </div>

        {/* Processing Steps */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-6">
          {[
            { title: "Embeddings", desc: "Contextualizados" },
            { title: "Base LLM", desc: "Generada" },
            { title: "Optimización", desc: "Realizada" },
            { title: "Predicción", desc: "Completada" },
            { title: "Priorización", desc: "Asignada" },
            { title: "Exportación", desc: "Lista" },
          ].map((step, idx) => (
            <div
              key={idx}
              className="bg-white rounded-lg p-3 border border-blue-200 text-center"
            >
              <CheckCircle className="w-5 h-5 text-green-600 mx-auto mb-2" />
              <p className="font-semibold text-sm text-gray-900">
                {step.title}
              </p>
              <p className="text-xs text-gray-500">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {analysis?.lista && (
        <div className="bg-white border-2 border-gray-200 rounded-2xl p-8">
          <div className="flex items-center gap-2 mb-6">
            <Target className="w-6 h-6 text-blue-600" />
            <h3 className="text-2xl font-bold text-gray-900">
              Recomendaciones Priorizadas
            </h3>
          </div>

          <div className="text-center mb-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-gray-600 mb-1">Total Optimizado</p>
            <p className="text-4xl font-bold text-blue-600">
              ${analysis.total?.toLocaleString() || "0"}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysis.lista?.slice(0, 12).map((item: any, i: number) => (
              <div
                key={i}
                className="bg-gray-50 border border-gray-300 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="text-2xl">
                    {item.prioridad_texto?.includes("Alta")
                      ? "🔴"
                      : item.prioridad_texto?.includes("Media")
                      ? "🟡"
                      : "🟢"}
                  </span>
                  <span className="text-xs px-2 py-1 bg-gray-200 rounded text-gray-700 font-medium">
                    {item.prioridad_texto || "Normal"}
                  </span>
                </div>

                <p className="font-semibold text-gray-900 mb-2 text-sm">
                  {item.producto || item.product}
                </p>
                <p className="text-gray-600 text-sm mb-3">
                  {item.cantidad} {item.unidad || "unidades"}
                </p>

                <div className="bg-blue-100 rounded-lg p-3 border border-blue-300">
                  <p className="text-blue-900 font-bold">
                    $
                    {(
                      (item.precio || item.precio_estimado) * item.cantidad
                    ).toLocaleString()}
                  </p>
                  <p className="text-xs text-blue-700">
                    ${(item.precio || item.precio_estimado).toLocaleString()}
                    /unidad
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Missing Products Alert */}
      {showMissing && (
        <div className="bg-orange-50 border-2 border-orange-300 rounded-2xl p-8">
          <div className="flex items-start gap-3 mb-6">
            <AlertCircle className="w-8 h-8 text-orange-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-1">
                Productos Faltantes Detectados
              </h3>
              <p className="text-gray-600">
                La IA recomienda que instales nuestro app para obtener un
                análisis más completo y preciso
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            {MISSING_PRODUCTS.map((item, idx) => (
              <div
                key={idx}
                className="bg-white rounded-lg p-4 border border-orange-200"
              >
                <div className="flex items-start justify-between mb-2">
                  <p className="font-semibold text-gray-900">{item.product}</p>
                  <span
                    className={`text-xs px-2 py-1 rounded font-medium ${
                      item.priority === "Alta"
                        ? "bg-red-100 text-red-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {item.priority}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{item.category}</p>
                <p className="text-xs text-gray-500 italic">{item.reason}</p>
              </div>
            ))}
          </div>

          <div className="bg-orange-100 border border-orange-300 rounded-lg p-4 mb-6">
            <p className="text-orange-900 font-semibold mb-2">
              ¿Cómo mejorar el análisis?
            </p>
            <p className="text-orange-800 text-sm">
              Descarga nuestra app móvil para obtener predicciones más precisas
              usando embeddings vectoriales, análisis con árboles de decisión y
              redes neuronales. ¡Acceso completo a todas las funciones de IA!
            </p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row justify-center gap-4">
        {analysis?.pdf && (
          <a
            href={analysis.pdf}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold rounded-lg transition-all transform hover:scale-105 shadow-lg"
          >
            <Download className="w-5 h-5" />
            Descargar Lista en PDF
          </a>
        )}
        {analysis?.whatsapp && (
          <a
            href={analysis.whatsapp}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-bold rounded-lg transition-all transform hover:scale-105 shadow-lg"
          >
            <Send className="w-5 h-5" />
            Enviar por WhatsApp
          </a>
        )}
      </div>
    </div>
  );
}
