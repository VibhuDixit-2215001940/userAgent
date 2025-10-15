// server.js
const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// simple in-memory store (demo only)
let submissions = [];

app.post('/receive', (req, res) => {
  const payload = req.body || {};
  const received = {
    id: Date.now(),
    receivedAt: new Date().toISOString(),
    ip: req.ip,
    payload
  };
  submissions.unshift(received);
  if (submissions.length > 50) submissions.pop();
  console.log('Received:', received);
  res.json({status: 'ok', received});
});

// optional route to view recent submissions in simple HTML
app.get('/submissions', (req, res) => {
  res.json(submissions);
});

// default: serve index.html from /public
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Receiver listening on port ${port}`);
});
