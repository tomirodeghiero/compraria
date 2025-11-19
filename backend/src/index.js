const express = require("express");
const cors = require("cors");

const optimizeRoute = require("./routes/optimize");
const productsRoute = require("./routes/products");
const healthRoute = require("./routes/health");

const app = express();
app.use(cors());
app.use(express.json());

// Rutas
app.use("/optimize", optimizeRoute);
app.use("/products", productsRoute);
app.use("/health", healthRoute);

const PORT = 3001;
app.listen(PORT, () => {
    console.log('Servidor Backend corriendo en puerto ${PORT}');
});