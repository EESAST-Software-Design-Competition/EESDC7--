const users = [
  { id: "{{user}}", name: "Editor 1" },
  { id: crypto.randomUUID(), name: "Editor 2" },
  { id: crypto.randomUUID(), name: "Editor 3" },
];

const sampleEntries = [
  {
    id: crypto.randomUUID(),
    name: "Formula 1",
    text: "Formula 1\n$x^2 + y^2 = z^2$",
    editor: users[0].id,
    time: 1629876543,
  },
  {
    id: crypto.randomUUID(),
    name: "Formula 2",
    text: "Formula 2\n$$\\frac{d}{dx} x^2 = 2x$$",
    editor: users[1].id,
    time: 1629876544,
  },
  {
    id: crypto.randomUUID(),
    name: "Formula 3",
    text: "Formula 3\n$$\\int x^2 dx = \\frac{1}{3}x^3 + C$$",
    editor: users[2].id,
    time: 1629876545,
  },
];

const sampleDrafts = [
  {
    id: crypto.randomUUID(),
    name: "Formula 4",
    text: "Formula 4\n$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$",
    editor: users[2].id,
    time: 1629876546,
  },
  {
    id: crypto.randomUUID(),
    name: "Formula 5",
    text: "Formula 5\n$$\\sum_{i=1}^{\\infty} \\frac{1}{i^2} = \\frac{\\pi^2}{6}$$",
    editor: users[1].id,
    time: 1629876547,
  },
  {
    id: crypto.randomUUID(),
    name: "Formula 6",
    text: "Formula 6\n\n$$\\sum_{i=1}^{\\infty} \\frac{1}{2^i} = 1$$",
    editor: users[0].id,
    time: 1629876548,
  },
];


function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
function nightmare(ms) {
  if (Math.random() < 0.8) return sleep(ms);
  return new Promise((_, reject) => setTimeout(() => reject("Nightmare!"), ms));
}

/*-------------------------------------------------------------------------*/

export function postCreate(roomId, name) {
  console.log(`Creating mock formula with name ${name} in room ${roomId}`);
  return new Promise((resolve, reject) => {
    nightmare(1000)
      .then(() => {
        resolve({ id: crypto.randomUUID() });
      })
      .catch(reject);
  });
}

export function getEntries(room_id) {
  console.log(`Geting mock entries for room ${room_id}`);
  const droppedEntries = sampleEntries.filter(() => Math.random() >= 0.0);
  return new Promise((resolve, reject) => {
    nightmare(1000)
      .then(() => {
        resolve(droppedEntries);
      })
      .catch(reject);
  });
}

export function getDrafts(room_id) {
  console.log(`Geting mock drafts for room ${room_id}`);
  const droppedDrafts = sampleDrafts.filter(() => Math.random() >= 0.2);
  return new Promise((resolve, reject) => {
    nightmare(1000)
      .then(() => {
        resolve(droppedDrafts);
      })
      .catch(reject);
  });
}

export function getUsers(room_id) {
  console.log(`Geting mock users for room ${room_id}`);
  return new Promise((resolve, reject) => {
    nightmare(1000)
      .then(() => {
        resolve(users);
      })
      .catch(reject);
  });
}

export async function postDraft(
  roomId,
  userId,
  formulaId,
  formulaName,
  formulaText
) {
  console.log(`Posting mock draft for room ${roomId} and user ${userId}`);
  const url = `/api/${roomId}/${userId}/${formulaId}`;
  const formData = new FormData();
  formData.append("name", formulaName);
  formData.append("text", formulaText);

  console.log("Fetching", url, {
    method: "POST",
    body: formData,
  });
  await nightmare(1000);
  console.log("OK");
  return;
}

export async function postSubmit(roomId, userId, formulaId) {
  console.log(`Posting mock submit for room ${roomId} and user ${userId}`);
  const url = `/api/${roomId}/${userId}/${formulaId}/submit`;

  console.log("Fetching", url, {
    method: "POST",
  });
  await nightmare(1000);
  console.log("OK");
  return;
}

export async function deleteDraft(roomId, userId, formulaId) {
  console.log(`Deleting mock draft for room ${roomId} and user ${userId}`);
  const url = `/api/${roomId}/${userId}/${formulaId}`;
  console.log("Fetching", url, {
    method: "DELETE",
  });
  await nightmare(1000);
  console.log("OK");
  return;
}
