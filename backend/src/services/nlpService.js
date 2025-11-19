const axios = require("axios");

exports.normalizeProducts = async (products) => {
    return products.map(p => p.toLowerCase().trim());
};