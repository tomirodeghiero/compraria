exports.adjustSolution = async (solution) => {
    const commerceCount = {};
    solution.forEach(item => {
        commerceCount[item.commerce] = (commerceCount[item.commerce] || 0) + 1;
    });

    return solution;
}