export const statuses = {todo:"Не начато", doing:"В работе", done:"Готово"};
export const subjects = {PLT:"ЯТП", ICT:"ИКТ"};
export const priorities = ["Низкий", "Обычный", "Высокий"];
export const repository = "https://github.com/meowflyx/WKITU_CEaIS_Studying";

export function defaults(task) {
  return {
    status:task.path ? "doing" : "todo", priority:1, link:"", notes:"",
    minutes:task.path ? 15 : task.minutes, planned:Boolean(task.path),
    required:false, near:Boolean(task.path)
  };
}

export function isMissing(task) {
  return !task.path && !task.link;
}

export function compareQueue(a,b) {
  return Number(b.required)-Number(a.required)
    || Number(b.near)-Number(a.near)
    || a.minutes-b.minutes
    || b.priority-a.priority
    || a.number-b.number
    || a.subject.localeCompare(b.subject)
    || a.n-b.n;
}

export function validEdit(value) {
  if (!value || !Object.hasOwn(statuses,value.status)
      || ![0,1,2].includes(value.priority)
      || !Number.isInteger(value.minutes) || value.minutes < 1 || value.minutes > 10000
      || typeof value.notes !== "string" || value.notes.length > 4000
      || typeof value.link !== "string" || value.link.length > 2048
      || !["planned","required","near"].every(key => typeof value[key] === "boolean")) return false;
  if (!value.link) return true;
  try {
    const link = new URL(value.link);
    return ["https:","http:"].includes(link.protocol) && !link.username && !link.password;
  } catch {
    return false;
  }
}
