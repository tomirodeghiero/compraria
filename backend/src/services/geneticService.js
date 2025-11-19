exports.runOptimization = async (priceMatrix) => {
    const simulation = priceMatrix.map(p => {
        const best = p.options.reduce((a, b) => a.price < b.price ? a : b);
        return {
            product: p.product,
            commerce: best.commerce,
            price: best.price
        };
    });

    return simulation;
};