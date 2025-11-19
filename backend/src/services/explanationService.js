exports.explain = async (solution) => {
    const lines = solution.map(s =>
        `- ${s.product}: se eligió ${s.commerce} por precio $${s.price.toFixed(2)}`
    );

    return "Optimizacion completada:\n" + lines.join("\n")
};