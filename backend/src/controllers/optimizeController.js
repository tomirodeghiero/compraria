const nlpService = require("../services/nlpService");
const priceService = require("../services/priceService");
const geneticService = require("../services/geneticService");
const preferencesModel = require("../services/preferencesModel");
const explanationService = require("../services/explanationService");

exports.optimize = async (req, res) => {
    try {
        const { products } = req.body;
        if (!products || !Array.isArray(products)) {
            return res.status(400).json({ error: "Debes enviar una lista de productos." });
        }

        // 1. Normalizar productos
        const normalized = await nlpService.normalizeProducts(products);

        // 2. Obtener precios
        const priceMatrix = await priceService.getPrices(normalized);

        // 3. Correr algoritmo genético
        const optimal = await geneticService.runOptimization(priceMatrix);

        // 4. Ajustar según preferencias
        const adjusted = await preferencesModel.adjustSolution(optimal);

        // 5. Explicación mediante LLM
        const explanation = await explanationService.explain(adjusted);

        res.json({
            input: products,
            normalized,
            solution: adjusted,
            explanation
        });

    } catch (error) {
        console.error("ERROR optimize:", error);
        res.status(500).json({ error: "Error interno del servidor." });
    }
};