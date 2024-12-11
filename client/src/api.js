//TODO: remove throws, change API return type to data | null

async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  return await response.json();
}

export async function postCreate(roomId, formulaName) {
  const url = `/api/${roomId}/create`;
  const formData = new FormData();
  formData.append("name", formulaName);

  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  return await response.json();
}

export async function getEntries(roomId) {
  return await fetchJSON(`/api/${roomId}/entries`);
}

export async function getUsers(roomId) {
  return await fetchJSON(`/api/${roomId}/users`);
}

export async function getDrafts(roomId) {
  return await fetchJSON(`/api/${roomId}/drafts`);
}

export async function postDraft(roomId, userId, formulaId, formulaName, formulaText) {
  const url = `/api/${roomId}/${userId}/${formulaId}`;
  const formData = new FormData();
  formData.append("name", formulaName);
  formData.append("text", formulaText);

  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  return await response.json();
}

export async function postSubmit(roomId, userId, formulaId) {
  const url = `/api/${roomId}/${userId}/${formulaId}/submit`;

  const response = await fetch(url, {
    method: "POST",
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  return await response.json();
}

export async function deleteDraft(roomId, userId, formulaId) {
  const url = `/api/${roomId}/${userId}/${formulaId}`;
  const response = await fetch(url, {
    method: "DELETE",
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
}