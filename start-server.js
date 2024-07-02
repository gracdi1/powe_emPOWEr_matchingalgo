const httpServer = require('http-server');
const path = require('path');

const server = httpServer.createServer({
  root: path.join(__dirname, 'public'),
});

server.listen(3000, () => {
  console.log('Server is listening on http://localhost:3000');
});
