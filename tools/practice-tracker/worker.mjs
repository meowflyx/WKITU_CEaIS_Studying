import {assets} from "./assets.mjs";
import {catalog} from "./catalog.mjs";
import {validEdit} from "./model.mjs";

const taskIds = new Set(catalog.flatMap(group =>
  group.tasks.map(task => `${group.subject}-${group.number}-${task.n}`)
));
const json = (value,status=200) => Response.json(value,{status,headers:{"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}});

async function taskApi(request,db,path) {
  const user = request.headers.get("oai-authenticated-user-id");
  if (!user) return json({error:"Требуется вход"},401);
  if (path === "/api/tasks" && request.method === "GET") {
    const {results} = await db.prepare("SELECT task_id, value FROM task_edits WHERE user_id = ?").bind(user).all();
    return json(Object.fromEntries(results.map(row => [row.task_id,JSON.parse(row.value)])));
  }
  const task = path.slice("/api/tasks/".length);
  if (!path.startsWith("/api/tasks/") || !taskIds.has(task)) return json({error:"Задание не найдено"},404);
  if (request.method !== "PUT") return json({error:"Метод не поддерживается"},405);
  if (request.headers.get("content-type")?.split(";")[0] !== "application/json") {
    return json({error:"Ожидается JSON"},415);
  }
  const body = await request.text();
  if (body.length > 30000) return json({error:"Запись слишком большая"},413);
  let value;
  try {
    value = JSON.parse(body);
  } catch {
    return json({error:"Некорректный JSON"},400);
  }
  if (!validEdit(value)) return json({error:"Некорректные поля"},400);
  const {status,priority,link,notes,minutes,planned,required,near} = value;
  await db.prepare(`INSERT INTO task_edits (user_id, task_id, value) VALUES (?, ?, ?)
    ON CONFLICT (user_id, task_id) DO UPDATE SET value = excluded.value`)
    .bind(user,task,JSON.stringify({status,priority,link,notes,minutes,planned,required,near})).run();
  return json({ok:true});
}

export default {
  async fetch(request,env) {
    const {pathname} = new URL(request.url);
    if (pathname === "/api/tasks" || pathname.startsWith("/api/tasks/")) {
      return taskApi(request,env.DB,pathname);
    }
    const asset = assets[pathname];
    if (!Object.hasOwn(assets,pathname)) return new Response("Страница не найдена",{status:404});
    if (!["GET","HEAD"].includes(request.method)) return new Response(null,{status:405});
    return new Response(request.method === "HEAD" ? null : asset.body,{headers:{
      "Content-Type":asset.type,"Cache-Control":"no-cache","X-Content-Type-Options":"nosniff",
      "Content-Security-Policy":"default-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'"
    }});
  }
};
