const path = require('path');
const express = require('express');
const router = express.Router();

var red = false;
var yellow = false;
var green = false;

router.get('/set/:color', async (req, res) => {
  if (req.params.color == 'r') {
    red = true;
    yellow = false;
    green = false;
    res.json('Red activated');
  }
  if (req.params.color == 'y') {
    red = false;
    yellow = true;
    green = false;
    res.json('Yellow activated');
  }
  if (req.params.color == 'g') {
    red = false;
    yellow = false;
    green = true;
    res.json('Green activated');
  }
});

router.get('/red', async (req, res) => {
    res.json(red);
});

router.get('/green', async (req, res) => {
    res.json(green);
});

module.exports = router;