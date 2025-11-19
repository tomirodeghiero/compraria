const fs = require("fs");
const path = require("path");

exports.getPrices = async (normalizedProducts) => {
    const mock = normalizedProducts.map(p => ({
        product: p,
        options: [
            { commerce: "Super Uno", price: Math.random()*1000+500 },
            { commerce: "Despensa Ana", price: Math.random()*1000+500 },
            { commerce: "MaxMarket", price: Math.random()*1000+500 }
        ]
    }));

    return mock;
};

exports.getAllProducts = async () => {
    return ["fideos", "arroz", "lavandina", "yerba", "azucar"];
};