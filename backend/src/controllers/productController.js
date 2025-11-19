const priceService = require("../services/priceService");

exports.getProducts = async (req, res) => {
    try {
        const products = await priceService.getAllProducts();
        res.json(products);
    } catch (error) {
        res.status(500).json({ error: "No se pudieron obtener los productos." });
    }
};