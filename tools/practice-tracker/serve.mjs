import {createServer} from "node:http";
import {Readable} from "node:stream";
import {openDb} from "./local-db.mjs";
import "./build.mjs";

const {default:worker} = await import("./dist/server/index.js");
const port = Number(process.env.PORT || 4173);
const origin = `http://127.0.0.1:${port}`;
const DB = openDb("practice-tracker.sqlite");

createServer(async (incoming,outgoing) => {
  try {
    if (incoming.headers.host !== `127.0.0.1:${port}`
        || (incoming.headers.origin && incoming.headers.origin !== origin)) {
      outgoing.writeHead(403).end();
      return;
    }
    const headers = new Headers(incoming.headers);
    headers.set("oai-authenticated-user-id","local");
    const method = incoming.method;
    const body = method === "GET" || method === "HEAD" ? undefined : Readable.toWeb(incoming);
    const request = new Request(origin+incoming.url,{method,headers,body,duplex:"half"});
    const response = await worker.fetch(request,{DB});
    outgoing.writeHead(response.status,Object.fromEntries(response.headers));
    if (response.body) Readable.fromWeb(response.body).pipe(outgoing);
    else outgoing.end();
  } catch (error) {
    console.error(error);
    outgoing.writeHead(500).end("Ошибка журнала");
  }
}).listen(port,"127.0.0.1",() => console.log(origin));
