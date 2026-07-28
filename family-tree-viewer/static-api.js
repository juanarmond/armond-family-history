import { loadTreeData } from "./data-loader.js";

const nativeFetch = window.fetch.bind(window);
let treePromise = null;

window.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input?.url;
  if (url === "/api/tree") {
    treePromise ||= loadTreeData();
    try {
      const payload = await treePromise;
      return new Response(JSON.stringify(payload), {
        status: 200,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      });
    }
  }
  return nativeFetch(input, init);
};

await import("./app.js");
