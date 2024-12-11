import Alpine from "alpinejs";
import persist from "@alpinejs/persist";
import { marked } from "marked";
import { typeset, stringSimilarity, colorFromId } from "./src/utils";
import {
  postCreate,
  getEntries,
  getDrafts,
  getUsers,
  postSubmit,
  postDraft,
  deleteDraft,
} from "./src/api";
// import {
//   postCreate,
//   getEntries,
//   getDrafts,
//   getUsers,
//   postSubmit,
//   postDraft,
//   deleteDraft,
// } from "./src/mock";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function every(ms, fn, catchFn = console.error) {
  let running = true;
  const loop = async () => {
    const start = Date.now();
    try {
      await fn();
    } catch (err) {
      catchFn(err);
    }
    if (!running) return;
    const diff = Date.now() - start;
    await sleep(Math.max(0, ms - diff));
    return loop();
  };
  return [loop(), () => (running = false)];
}

Alpine.plugin(persist);
Alpine.data("App", function () {
  return {
    room_id: Info.room_id,
    user_id: Info.user_id,
    room_name: Info.room_name,
    entries: this.$persist([]).using(sessionStorage),
    drafts: this.$persist([]).using(sessionStorage),
    stack: this.$persist([]).using(sessionStorage),
    users: this.$persist([]).using(sessionStorage),
    async init() {
      every(1500, this.getData.bind(this));
    },
    async getData() {
      this.entries = await getEntries(this.room_id);
      this.drafts = await getDrafts(this.room_id);
      this.users = await getUsers(this.room_id);
      this.users = this.users.map((u) => ({ ...u, color: colorFromId(u.id) }));
    },
    async addEntry(name, text = "") {
      try {
        const data = await postCreate(this.room_id, name);
        this.pushEntry(data.id, name, text);
        return data.id;
      } catch (err) {
        console.error(err);
        throw err;
      }
    },
    pushEntry(id, name, text) {
      this.stack.push({ id, name, text, time: Date.now() });
    },
    changeEntry(id, name, text) {
      this.stack = this.stack.map((entry) => (entry.id === id ? { ...entry, name, text } : entry));
    },
    removeEntry(id) {
      this.stack = this.stack.filter((entry) => entry.id !== id);
    },
    colorFromId,
  };
});

Alpine.data("SearchBar", () => ({
  filter: "",
  filtered: [],
  init() {
    this.setFiltered();
    this.$watch("users", this.setFiltered.bind(this));
  },
  setFiltered() {
    this.filtered = this.getFiltered();
  },
  getFiltered() {
    const userMap = new Map(this.$data.users.map((u) => [u.id, u]));
    const all = [
      ...this.$data.entries.map((e) => ({
        ...e,
        isDraft: false,
        editor: userMap.get(e.editor).name,
        color: userMap.get(e.editor).color,
      })),
      ...this.$data.drafts.map((e) => ({
        ...e,
        isDraft: true,
        editor: userMap.get(e.editor).name,
        color: userMap.get(e.editor).color,
      })),
    ];
    let searched = all.sort((a, b) => b.time - a.time);
    const text = this.filter;
    searched = searched.map((entry) => ({
      ...entry,
      similarity: stringSimilarity(`${entry.name}@${entry.editor}\n${entry.text}`, text),
    }));
    searched = searched.sort((a, b) => b.similarity - a.similarity);
    return searched;
  },
}));

Alpine.data("Entry", ({ id, name, text, editor, time, isDraft, color }) => ({
  id,
  name,
  text,
  html: "",
  editor,
  time,
  isDraft,
  color,
  async init() {
    await this.render();
  },
  async render() {
    this.html = await marked.parse(this.text);
  },
  typesetEl(el) {
    typeset(() => [el]);
  },
  addSelf() {
    return this.$data.addEntry(this.name, this.text);
  },
}));

Alpine.data("Editor", ({ id, name, text, time }) => ({
  id,
  name,
  text,
  time,
  html: "",
  submitting: false,
  async init() {
    let previous = {text: "", name: ""};
    [this.loop, this.stop] = every(3000, async () => {
      if (previous.text === this.text && previous.name === this.name) return;
      await postDraft(
        this.$data.room_id,
        this.$data.user_id,
        this.id,
        this.name,
        this.text
      );
      previous = {text: this.text, name: this.name};
      this.$nextTick(() => this.$data.changeEntry(this.id, this.name, this.text));
    });
    await this.render();
  },
  async render() {
    this.html = await marked.parse(this.text);
  },
  typesetEl(el) {
    typeset(() => [el]);
  },
  async submitSelf() {
    this.stop();
    await this.loop;
    await postDraft(
      this.$data.room_id,
      this.$data.user_id,
      this.id,
      this.name,
      this.text
    );
    await postSubmit(this.$data.room_id, this.$data.user_id, this.id);
    this.$data.removeEntry(this.id);
  },
  async deleteSelf() {
    this.stop();
    await this.loop;
    await deleteDraft(this.$data.room_id, this.$data.user_id, this.id);
    this.$data.removeEntry(this.id);
  },
}));

window.Alpine = Alpine;
Alpine.start();
