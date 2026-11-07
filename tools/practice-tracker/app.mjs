import {catalog,snapshot} from "/catalog.mjs";
import {statuses,subjects,priorities,repository,defaults,isMissing,compareQueue,validEdit} from "/model.mjs";

const pages = {
  all:["Все практики","Предметы, темы практик и задания из методичек.","▤"],
  open:["Незавершённые","Задания в плане, у которых ещё нет статуса «Готово».","◷"],
  missing:["Без материалов","Задания, для которых в снимке ветки нет файлов и в журнале нет добавленной ссылки.","◇"],
  next:["Что закрыть следующим","Сначала обязательные, затем почти готовые. В каждой группе первыми идут задачи с меньшим остатком времени.","↗"]
};
const tasks = catalog.flatMap(group => group.tasks.map(task => ({
  ...task, subject:group.subject, number:group.number, topic:group.title,
  id:`${group.subject}-${group.number}-${task.n}`
})));
const $ = selector => document.querySelector(selector);
const list = $("#list"), notice = $("#notice"), dialog = $("#editor"), form = $("#edit-form");
const input = name => form.elements.namedItem(name);
const search = $("#search");
let edits = {};
let subject = "";
let activeId = "";
let saving = false;
let ready = false;
let initialRender = true;
const groupState = new Map();

const escape = value => String(value).replace(/[&<>"']/g, char => ({
  "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
})[char]);
const tag = (text,variant="") => `<span class="tag ${variant}">${escape(text)}</span>`;
const getPage = () => Object.hasOwn(pages,location.hash.slice(1)) ? location.hash.slice(1) : "all";
const withEdit = task => ({...task,...defaults(task),...edits[task.id]});
const external = (url,label) => `<a href="${escape(url)}" target="_blank" rel="noopener">${label} ↗</a>`;
const sourceUrl = task => `${repository}/${task.folder ? "tree" : "blob"}/Andrey/${task.path.split("/").map(encodeURIComponent).join("/")}`;

function row(task,queue=false) {
  const scope = queue ? `${subjects[task.subject]} · Практика №${task.number} · ` : "";
  const files = task.path ? external(sourceUrl(task),"Файлы в GitHub") : "";
  const link = task.link ? external(task.link,"Добавленная ссылка") : "";
  const flags = [
    tag(statuses[task.status],task.status+" dot"),
    task.required && tag("Обязательное","required"),
    task.status !== "done" && task.near && tag("Почти готово"),
    task.planned && !task.required && tag("В плане"),
    task.priority !== 1 && tag(priorities[task.priority]+" приоритет"),
    isMissing(task) && tag("Без материалов","missing"),
    queue && tag(`${task.minutes} мин`)
  ].filter(Boolean).join("");
  return `<article class="row"><div><div class="sub">${scope}Задание ${task.n}</div>
    <h3>${escape(task.title)}</h3><div class="badges">${flags}</div>
    ${files || link ? `<div class="links">${files}${link}${task.formats?.join(" · ") || ""}</div>` : ""}
    ${task.notes ? `<p class="note">${escape(task.notes)}</p>` : ""}
    </div><button type="button" class="icon-button" data-edit="${task.id}" aria-label="Редактировать задание ${task.n}, ${escape(task.title)}" title="Редактировать">✎</button></article>`;
}

function render() {
  const page = getPage();
  const [heading,description] = pages[page];
  const all = tasks.map(withEdit);
  const planned = all.filter(task => task.planned || task.required);
  const open = planned.filter(task => task.status !== "done");
  const done = all.filter(task => task.status === "done");
  const missing = all.filter(isMissing);
  const sets = {all,open,missing,next:open};
  const query = search.value.toLocaleLowerCase("ru").trim();
  const visible = sets[page].filter(task => (!subject || subject === task.subject) &&
    query.split(/\s+/).every(word => `${subjects[task.subject]} ${task.topic} практика ${task.number} задание ${task.n} ${task.title} ${task.notes}`.toLocaleLowerCase("ru").includes(word)));
  $("#nav").innerHTML = Object.entries(pages).map(([key,[label,,icon]]) =>
    `<a href="#${key}" ${key === page ? 'aria-current="page"' : ""}><span aria-hidden="true">${icon}</span>${label}</a>`).join("");
  $("#kicker").textContent = `ЖУРНАЛ / 0${Object.keys(pages).indexOf(page)+1}`;
  $("#heading").textContent = heading;
  $("#description").textContent = description;
  $("#stats").innerHTML = [["В плане",planned.length,"open"],["Готово",done.length,"all"],["Незавершённые",open.length,"open"],["Без материалов",missing.length,"missing"]].map(([label,count,key]) =>
    `<a class="stat" href="#${key}"><strong>${count}</strong><span>${label}</span></a>`).join("");
  notice.textContent = page === "all"
    ? "Методички содержат варианты. В план изначально включены задания с файлами в GitHub. Статус сдачи можно отметить вручную."
    : page === "next"
      ? "Чтобы поставить задание в очередь, отметьте «В плане» или «Обязательное» в редакторе. Время можно уточнить там же."
      : "";
  notice.hidden = !notice.textContent;
  if (!visible.length) {
    list.innerHTML = `<div class="empty">${query || subject ? "По этим фильтрам ничего не найдено." : "В этом разделе пока нет заданий."}</div>`;
  } else if (page === "next") {
    list.innerHTML = visible.sort(compareQueue).map((task,index) =>
      `<div class="queue-item"><div class="number">${index+1}</div>${row(task,true)}</div>`).join("");
  } else {
    list.innerHTML = Object.entries(subjects).map(([code,label]) => {
      const groups = catalog.filter(group => group.subject === code).map(group => {
        const items = visible.filter(task => task.subject === code && task.number === group.number);
        if (!items.length) return "";
        const key = `${page}-${code}-${group.number}`;
        const expanded = query || (groupState.get(key) ?? group.number === 1);
        return `<details class="group" data-group="${key}" ${expanded ? "open" : ""}>
          <summary><span class="number">${String(group.number).padStart(2,"0")}</span><span class="group-title">${escape(group.title)}</span><span class="group-count">${items.length} / ${group.tasks.length}</span></summary>
          ${items.map(task => row(task)).join("")}</details>`;
      }).join("");
      return groups ? `<h3 class="section-label">${label} / ПРАКТИКИ</h3>${groups}` : "";
    }).join("");
  }
  if (initialRender) {
    list.setAttribute("aria-busy","false");
    initialRender = false;
  }
}

list.addEventListener("toggle",event => {
  if (event.target.matches("details[data-group]") && !search.value.trim()) {
    groupState.set(event.target.dataset.group,event.target.open);
  }
},true);
list.addEventListener("click",event => {
  const button = event.target.closest("[data-edit]");
  if (!button || !ready) return;
  const task = withEdit(tasks.find(task => task.id === button.dataset.edit));
  activeId = task.id;
  $("#edit-context").textContent = `${subjects[task.subject]} / ПРАКТИКА ${task.number} / ЗАДАНИЕ ${task.n}`;
  $("#edit-title").textContent = task.title;
  $("#save-error").textContent = "";
  for (const key of Object.keys(defaults(task))) {
    const field = input(key);
    if (field.type === "checkbox") field.checked = task[key];
    else field.value = task[key];
  }
  dialog.showModal();
});

for (const selector of ["#close-edit","#cancel-edit"]) $(selector).addEventListener("click",() => {
  if (!saving) dialog.close();
});
dialog.addEventListener("cancel",event => { if (saving) event.preventDefault(); });
form.addEventListener("submit",async event => {
  event.preventDefault();
  if (saving) return;
  const value = {
    status:input("status").value, priority:Number(input("priority").value),
    link:input("link").value.trim(), notes:input("notes").value.trim(), minutes:input("minutes").valueAsNumber,
    planned:input("planned").checked, required:input("required").checked, near:input("near").checked
  };
  const error = $("#save-error");
  if (!validEdit(value)) {
    error.textContent = "Проверьте поля. Для ссылки подходят адреса http:// и https://.";
    return;
  }
  saving = true;
  const submit = form.querySelector('[type="submit"]');
  submit.disabled = true;
  error.textContent = "";
  try {
    const response = await fetch(`/api/tasks/${activeId}`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(value)});
    if (!response.ok) throw new Error("save");
    edits[activeId] = value;
    dialog.close();
    render();
    (list.querySelector(`[data-edit="${activeId}"]`) || $("#heading")).focus({preventScroll:true});
  } catch {
    error.textContent = "Не удалось сохранить. Проверьте подключение и повторите.";
  } finally {
    submit.disabled = false;
    saving = false;
  }
});

$("#subjects").addEventListener("click",event => {
  const button = event.target.closest("[data-subject]");
  if (!button || !ready) return;
  subject = button.dataset.subject;
  for (const item of $("#subjects").children) item.setAttribute("aria-pressed",item === button);
  render();
});
search.addEventListener("input",() => { if (ready) render(); });
window.addEventListener("hashchange",() => { if (ready) render(); });
$("#snapshot").textContent = `GitHub · Andrey · ${snapshot}`;
try {
  const response = await fetch("/api/tasks");
  if (!response.ok) throw new Error("load");
  edits = await response.json();
  ready = true;
  render();
} catch {
  notice.textContent = "Журнал не загрузился. Обновите страницу, чтобы повторить.";
  notice.classList.add("failure");
  list.setAttribute("aria-busy","false");
}
