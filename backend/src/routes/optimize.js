const express = require("express");
const router = express.Router();
const optimizeController = require("../controllers/optimizeController");

router.post("/", optimizeController.optimize);

module.exports = router;