/* === Notes Panel — CRUD + Detail View JS === */
(function () {
  'use strict';

  const API        = window.NOTES_API_URL;
  const CSRF       = window.CALENDAR_CSRF;
  const list       = document.getElementById('notesList');
  const empty      = document.getElementById('notesEmpty');
  const countBadge = document.getElementById('notesCount');

  // Edit/Add modal
  const modal       = new bootstrap.Modal(document.getElementById('noteModal'));
  const modalTitle  = document.getElementById('noteModalTitle');
  const noteId      = document.getElementById('noteId');
  const noteTitle   = document.getElementById('noteTitle');
  const noteContent = document.getElementById('noteContent');
  const notePinned  = document.getElementById('notePinned');
  const colorPicker = document.getElementById('noteColorPicker');
  let selectedColor = 'gold';

  // Detail modal
  const detailModal      = new bootstrap.Modal(document.getElementById('noteDetailModal'));
  const detailContent    = document.getElementById('noteDetailContent');
  const detailTitle      = document.getElementById('noteDetailTitle');
  const detailBody       = document.getElementById('noteDetailBody');
  const detailDate       = document.getElementById('noteDetailDate');
  const detailPin        = document.getElementById('noteDetailPin');
  const detailEditBtn    = document.getElementById('noteDetailEditBtn');
  let   activeDetailCard = null;

  // === Color picker ===
  colorPicker.querySelectorAll('.note-color-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      colorPicker.querySelectorAll('.note-color-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedColor = btn.dataset.color;
    });
  });

  function setColor(color) {
    selectedColor = color;
    colorPicker.querySelectorAll('.note-color-btn').forEach(b =>
      b.classList.toggle('active', b.dataset.color === color)
    );
  }

  // === Helpers ===
  function csrfHeaders() {
    return { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF };
  }

  function updateCount() {
    const n = list.querySelectorAll('.note-card').length;
    countBadge.textContent = n;
    if (empty) empty.style.display = n === 0 ? 'block' : 'none';
  }

  function escape(str) {
    return (str || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function createCardHTML(note) {
    const pin     = note.pinned ? '<i class="bi bi-pin-angle-fill note-pin-icon"></i>' : '';
    const preview = note.content
      ? `<div class="note-preview">${escape(note.content)}</div>` : '';
    return `
      <div class="note-card note-color-${note.color}" data-id="${note.id}"
           data-title="${escape(note.title)}"
           data-content="${escape(note.content || '')}"
           data-color="${note.color}"
           data-pinned="${note.pinned ? 'true' : 'false'}"
           data-date="${note.updated_at}">
        <div class="note-card-head">
          <span class="note-title">${escape(note.title)}</span>
          <div class="note-actions">
            ${pin}
            <button class="note-btn note-btn-edit" data-id="${note.id}" title="แก้ไข"><i class="bi bi-pencil"></i></button>
            <button class="note-btn note-btn-del"  data-id="${note.id}" title="ลบ"><i class="bi bi-trash"></i></button>
          </div>
        </div>
        ${preview}
        <div class="note-footer">${note.updated_at}</div>
      </div>`;
  }

  // === Open Detail Modal (click card) ===
  function openDetail(card) {
    const color   = [...card.classList].find(c => c.startsWith('note-color-'))?.replace('note-color-', '') || 'gold';
    const title   = card.dataset.title   || card.querySelector('.note-title')?.textContent || '';
    const content = card.dataset.content || '';
    const date    = card.dataset.date    || card.querySelector('.note-footer')?.textContent || '';
    const pinned  = card.dataset.pinned === 'true';

    // Set color class on modal
    detailContent.className = detailContent.className
      .replace(/note-detail-\w+/g, '')
      .trim() + ` note-detail-${color}`;

    detailTitle.textContent = title;
    detailBody.textContent  = content || '(ไม่มีเนื้อหา)';
    detailDate.textContent  = date;
    detailPin.classList.toggle('d-none', !pinned);
    activeDetailCard = card;

    detailModal.show();
  }

  // Detail → Edit button
  detailEditBtn.addEventListener('click', () => {
    detailModal.hide();
    setTimeout(() => openEdit(activeDetailCard), 300);
  });

  // === Bind card events ===
  function bindCardEvents(card) {
    // Click card body → detail (ยกเว้น action buttons)
    card.addEventListener('click', e => {
      if (e.target.closest('.note-btn')) return;
      openDetail(card);
    });
    card.querySelector('.note-btn-edit').addEventListener('click', e => {
      e.stopPropagation();
      openEdit(card);
    });
    card.querySelector('.note-btn-del').addEventListener('click', e => {
      e.stopPropagation();
      deleteNote(card);
    });
  }

  // Bind existing cards on page load
  list.querySelectorAll('.note-card').forEach(bindCardEvents);
  updateCount();

  // === Open Add Modal ===
  document.getElementById('btnAddNote').addEventListener('click', () => {
    modalTitle.textContent = 'เพิ่ม Note';
    noteId.value      = '';
    noteTitle.value   = '';
    noteContent.value = '';
    notePinned.checked = false;
    setColor('gold');
    modal.show();
  });

  // === Open Edit Modal ===
  function openEdit(card) {
    const id      = card.dataset.id;
    const title   = card.dataset.title   || card.querySelector('.note-title')?.textContent || '';
    const content = card.dataset.content || '';
    const color   = [...card.classList].find(c => c.startsWith('note-color-'))?.replace('note-color-', '') || 'gold';
    const pinned  = card.dataset.pinned === 'true';

    modalTitle.textContent = 'แก้ไข Note';
    noteId.value       = id;
    noteTitle.value    = title;
    noteContent.value  = content;
    notePinned.checked = pinned;
    setColor(color);
    modal.show();
  }

  // === Save (Add / Edit) ===
  document.getElementById('btnSaveNote').addEventListener('click', async () => {
    const title = noteTitle.value.trim();
    if (!title) { noteTitle.focus(); return; }

    const payload = {
      title,
      content: noteContent.value.trim(),
      color:   selectedColor,
      pinned:  notePinned.checked,
    };

    const id     = noteId.value;
    const url    = id ? `${API}${id}/` : API;
    const method = id ? 'PATCH' : 'POST';

    try {
      const res  = await fetch(url, { method, headers: csrfHeaders(), body: JSON.stringify(payload) });
      const data = await res.json();
      if (!data.ok) return;

      const now = new Date().toLocaleString('th-TH', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });

      if (id) {
        const card = list.querySelector(`[data-id="${id}"]`);
        const tmp  = document.createElement('div');
        tmp.innerHTML = createCardHTML({ id, ...payload, updated_at: now });
        const newCard = tmp.firstElementChild;
        card.replaceWith(newCard);
        bindCardEvents(newCard);
      } else {
        const tmp = document.createElement('div');
        tmp.innerHTML = createCardHTML({ id: data.id, ...payload, updated_at: now });
        const newCard = tmp.firstElementChild;
        if (empty) list.insertBefore(newCard, empty);
        else list.prepend(newCard);
        bindCardEvents(newCard);
      }

      modal.hide();
      updateCount();
    } catch (e) { console.error(e); }
  });

  // === Delete ===
  async function deleteNote(card) {
    if (!confirm('ลบ Note นี้?')) return;
    const id = card.dataset.id;
    try {
      await fetch(`${API}${id}/`, { method: 'DELETE', headers: csrfHeaders() });
      card.remove();
      updateCount();
    } catch (e) { console.error(e); }
  }

})();
