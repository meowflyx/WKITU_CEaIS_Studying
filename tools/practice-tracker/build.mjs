import {mkdirSync,readFileSync,writeFileSync} from "node:fs";

const type = {html:"text/html",css:"text/css",mjs:"text/javascript"};
const files = ["index.html","style.css","app.mjs","catalog.mjs","model.mjs"];
const assets = Object.fromEntries(files.map(file => [file === "index.html" ? "/" : "/"+file,{
  type:type[file.split(".").at(-1)]+"; charset=utf-8",
  body:readFileSync(file,"utf8")
}]));
const worker = readFileSync("worker.mjs","utf8").split("\n").slice(3).join("\n");
const catalog = readFileSync("catalog.mjs","utf8").replaceAll("export const ","const ");
const model = readFileSync("model.mjs","utf8").replaceAll(/^export /gm,"");
mkdirSync("dist/server",{recursive:true});
writeFileSync("dist/server/index.js",`const assets = ${JSON.stringify(assets)};\n${catalog}\n${model}\n${worker}`);
