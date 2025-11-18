/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { Download, Send } from "lucide-react";

interface RecommendationResultsProps {
  resultado: any;
}

export default function RecommendationResults({
  resultado,
}: RecommendationResultsProps) {
  return (
    <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-8">
      {/* Title */}
      <div className="text-center mb-8">
        <h2 className="text-3xl md:text-4xl font-bold text-slate-100 mb-2">
          ¡Recomendaciones Generadas! 🎯
        </h2>
        <p className="text-slate-400">
          Total optimizado:{" "}
          <span className="text-2xl font-bold text-cyan-400">
            ${resultado.total?.toLocaleString() || "0"}
          </span>
        </p>
      </div>

      {/* Products Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {resultado.lista?.slice(0, 12).map((item: any, i: number) => (
          <div
            key={i}
            className="bg-gradient-to-br from-slate-700/40 to-slate-800/40 border border-slate-700/50 rounded-xl p-5 hover:border-cyan-400/30 transition-all group"
          >
            {/* Priority Badge */}
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">
                {item.prioridad_texto?.includes("Alta")
                  ? "🔴"
                  : item.prioridad_texto?.includes("Media")
                  ? "🟡"
                  : "🟢"}
              </span>
              <span className="text-xs px-2 py-1 bg-slate-600/50 rounded text-slate-300">
                {item.prioridad_texto || "Normal"}
              </span>
            </div>

            {/* Product Info */}
            <p className="font-semibold text-slate-100 mb-2 text-sm">
              {item.producto || item.product}
            </p>
            <p className="text-slate-400 text-sm mb-3">
              {item.cantidad} {item.unidad || "unidades"}
            </p>

            {/* Price */}
            <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-lg p-3 border border-cyan-500/30">
              <p className="text-cyan-300 font-bold text-lg">
                $
                {(
                  (item.precio || item.precio_estimado) * item.cantidad
                ).toLocaleString()}
              </p>
              <p className="text-xs text-slate-400">
                ${(item.precio || item.precio_estimado).toLocaleString()}/unidad
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row justify-center gap-4">
        {resultado.pdf && (
          <a
            href={resultado.pdf}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-3 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-lg transition-all transform hover:scale-105 shadow-lg"
          >
            <Download className="w-5 h-5" />
            Descargar PDF
          </a>
        )}
        {resultado.whatsapp && (
          <a
            href={resultado.whatsapp}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-3 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold rounded-lg transition-all transform hover:scale-105 shadow-lg"
          >
            <Send className="w-5 h-5" />
            Enviar por WhatsApp
          </a>
        )}
      </div>
    </div>
  );
}
