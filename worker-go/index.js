// Short host for Tripwise links: https://go.tripwise-hub.workers.dev/<name>
// Forwards every request to the main worker "tripwise-bot" (service binding MAIN), so all short links,
// the link-in-bio page /ig and /check live in worker/index.js.
export default {
  fetch(req, env) {
    return env.MAIN.fetch(req);
  },
};
