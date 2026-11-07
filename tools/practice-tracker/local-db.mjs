import {DatabaseSync} from "node:sqlite";
import {readFileSync} from "node:fs";

export function openDb(filename) {
  const db = new DatabaseSync(filename);
  const migration = readFileSync(new URL("./drizzle/0000_task_edits.sql",import.meta.url),"utf8");
  db.exec(migration.replace("CREATE TABLE ","CREATE TABLE IF NOT EXISTS "));
  return {
    close:() => db.close(),
    prepare(query) {
      const statement = db.prepare(query);
      return {
        bind(...parameters) {
          return {
            all:() => ({results:statement.all(...parameters)}),
            run:() => statement.run(...parameters)
          };
        }
      };
    }
  };
}
