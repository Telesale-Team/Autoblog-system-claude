/* =============================================================
   calendar.js — Work Calendar (FullCalendar 6)
   =============================================================
   ข้อมูลจาก Django template (window globals):
     window.CALENDAR_CSRF       — CSRF token สำหรับ API calls
     window.CALENDAR_API_URL    — URL ของ /owner/api/events/
     window.CALENDAR_EVENTS     — JSON array ของ system events จาก DB

   โครงสร้าง:
     1. CAT_CFG          — สี + ไอคอน + filter group ของแต่ละ category
     2. Phase Timeline   — highlight phase ปัจจุบันใน phase bar
     3. sysEvents        — แปลง rawEvents → FullCalendar format
     4. FullCalendar     — init calendar + event sources 2 แหล่ง
     5. Revenue Progress — คำนวณ % งานเสร็จ → progress bar
     6. API helpers      — POST / PATCH / DELETE functions
     7. Toast + XP       — notification popup
     8. Detail modal     — เปิด/ปิด modal เมื่อคลิก event
     9. Edit modal       — form เพิ่ม/แก้ไขงาน
    10. Filter tabs      — กรอง event ตาม category
    11. Mark as Done     — checkbox กดเสร็จ → PATCH is_completed
   ============================================================= */

document.addEventListener('DOMContentLoaded', function () {

  /* ── เลื่อน subheader ไปอยู่ระหว่าง toolbar กับ grid (ก่อน fc-view-harness) ── */
  function mountSubheader() {
    const viewHarness = document.querySelector('#calendar .fc-view-harness');
    const sub         = document.getElementById('cal-subheader');
    if (viewHarness && sub) viewHarness.insertAdjacentElement('beforebegin', sub);
  }


  /* ── Month/Year Picker ───────────────────────────────────────────── */
  const pickMonth = document.getElementById('calPickMonth');
  const pickYear  = document.getElementById('calPickYear');
  const pickGo    = document.getElementById('calPickGo');

  // สร้าง year options ย้อนหลัง 3 ปี ไปข้างหน้า 3 ปี
  const thisYear = new Date().getFullYear();
  for (let y = thisYear - 3; y <= thisYear + 3; y++) {
    const opt = document.createElement('option');
    opt.value = y;
    opt.textContent = y + 543; // แสดงเป็น พ.ศ.
    if (y === thisYear) opt.selected = true;
    pickYear.appendChild(opt);
  }
  // set current month
  pickMonth.value = new Date().getMonth();

  // กด Go หรือ Enter
  function jumpToDate() {
    const m = parseInt(pickMonth.value);
    const y = parseInt(pickYear.value);
    cal.gotoDate(new Date(y, m, 1));
  }
  pickGo.addEventListener('click', jumpToDate);
  pickMonth.addEventListener('change', jumpToDate);
  pickYear.addEventListener('change', jumpToDate);

  /* Init Bootstrap tooltips — filter tabs + stat cards */
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el, { trigger: 'hover', delay: { show: 400, hide: 100 } });
  });

  /* ── [0] Django globals ───────────────────────────────────────── */
  const csrf = window.CALENDAR_CSRF;
  const API  = window.CALENDAR_API_URL;

  /* ── [1] CAT_CFG — สี + ไอคอน ของแต่ละประเภทงาน ─────────────────
     palette: Gold (#c9a96e / #b8924f) สำหรับ milestone/priority
              Navy-Blue derive (#2d4373 → #9eb3c2) สำหรับทุก category อื่น
     filterGroup: ใช้ match กับ data-filter ใน filter tabs HTML         */
  /* bsIcon = Bootstrap Icon class ที่ตรงกับ Stat Cards
     icon   = emoji fallback (ใช้ใน category badge ของ modal)            */
  const CAT_CFG = {
    milestone:    { color: '#c9a96e', label: 'แผน (Roadmap)',  icon: '🎯', bsIcon: 'bi-flag-fill',              filterGroup: 'milestone'                    },
    action:       { color: '#60a5fa', label: 'งานต้องทำ',      icon: '⚡', bsIcon: 'bi-lightning-charge-fill',  filterGroup: 'action'                       },
    article:      { color: '#34d399', label: 'Actual',          icon: '📝', bsIcon: 'bi-newspaper',               filterGroup: 'actual'                       },
    lead:         { color: '#10b981', label: 'Actual',          icon: '👤', bsIcon: 'bi-person-check-fill',       filterGroup: 'actual'                       },
    recurring:    { color: '#a78bfa', label: 'Recurring',       icon: '🔄', bsIcon: 'bi-arrow-repeat',            filterGroup: 'recurring'                    },
    content_plan: { color: '#fbbf24', label: 'Content',         icon: '📄', bsIcon: 'bi-file-text-fill',          filterGroup: 'content'                      },
    backlog:      { color: '#f59e0b', label: 'Content',         icon: '🗓️', bsIcon: 'bi-calendar2-week',          filterGroup: 'content'                      },
    general:      { color: '#94a3b8', label: 'งานของฉัน',      icon: '📌', bsIcon: 'bi-pin-fill',                filterGroup: 'user-event', userOwned: true   },
    priority:     { color: '#c9a96e', label: 'งานสำคัญ',       icon: '🔥', bsIcon: 'bi-exclamation-circle-fill', filterGroup: 'user-event', userOwned: true   },
    meeting:      { color: '#818cf8', label: 'ประชุม',          icon: '👥', bsIcon: 'bi-people-fill',             filterGroup: 'user-event', userOwned: true   },
    delivery:     { color: '#2dd4bf', label: 'ส่งมอบงาน',      icon: '📦', bsIcon: 'bi-box-seam',                filterGroup: 'user-event', userOwned: true   },
    personal:     { color: '#94a3b8', label: 'ส่วนตัว',         icon: '🙋', bsIcon: 'bi-person-heart',            filterGroup: 'user-event', userOwned: true   },
  };
  /* ถ้า category ไม่ match ใน CAT_CFG ใช้ milestone เป็น fallback */
  function getCfg(cat) { return CAT_CFG[cat] || { color: '#c9a96e', label: cat, icon: '•', bsIcon: 'bi-flag-fill', filterGroup: 'milestone' }; }

  /* Inject CSS class สีไอคอนใน Filter Toolbar — ใช้ cal-icon-* จาก dashboard-base.css */
  document.querySelectorAll('#legendBar .filter-btn [data-cat]').forEach(function (icon) {
    icon.classList.add('cal-icon-' + icon.dataset.cat);
  });

  /* สร้าง HTML icon element — ใช้ cal-icon-* class แทน inline style */
  function iconHtml(cat) {
    const c = getCfg(cat);
    return '<i class="bi ' + c.bsIcon + ' cal-ev-icon cal-icon-' + cat + '"></i>';
  }

  /* ── [2] Phase Journey — highlight phase ปัจจุบัน ────────────────
     อ่าน data-phase-start / data-phase-end จาก HTML แต่ละ .phase-step
     แล้วเพิ่ม badge ลงใน .phase-badge-slot ภายใน step นั้น           */
  const today = new Date();
  document.querySelectorAll('#phaseBar .phase-step').forEach(function (el, idx) {
    const s = new Date(el.dataset.phaseStart), e = new Date(el.dataset.phaseEnd);
    const slot = el.querySelector('.phase-badge-slot');
    if (today >= s && today <= e) {
      el.classList.add('phase-active');
      if (slot) slot.innerHTML = '<span class="phase-active-badge">&#9654; LEVEL ' + (idx + 1) + '</span>';
    } else if (today > e) {
      el.classList.add('phase-done');
      if (slot) slot.innerHTML = '<span class="phase-done-badge">&#10003; DONE</span>';
    } else {
      if (slot) slot.innerHTML = '<span class="phase-lock-badge">&#128274;</span>';
    }
  });

  /* ── [3] sysEvents — แปลง rawEvents → FullCalendar format ──────────
     rawEvents = window.CALENDAR_EVENTS (inject จาก Django template)
     - is_completed=true  → สีเทา #475569 + class fc-event-completed
     - is_completed=false → สีตาม category  + class fc-event-pending   */
  const rawEvents = window.CALENDAR_EVENTS || [];
  const PENDING_COLOR = '#3b82f6';   // Blue-500 — งานยังไม่ทำ
  const DONE_COLOR    = '#64748b';   // Slate-500 — งานเสร็จแล้ว

  const sysEvents = rawEvents.map(function (e) {
    const completed = !!e.is_completed;
    return Object.assign({}, e, {
      color:      completed ? DONE_COLOR : PENDING_COLOR,
      borderColor:'transparent',
      classNames: completed ? ['fc-event-completed'] : ['fc-event-pending'],
      editable:   false,
      extendedProps: {
        description: e.description  || '',
        category:    e.category     || 'milestone',
        isSystem:    true,
        isCompleted: completed,
      },
    });
  });

  /* ── [4] FullCalendar — init ──────────────────────────────────────
     eventSources มี 2 แหล่ง:
       Source 1 (sysEvents) — static array จาก Django (milestone/action/etc.)
       Source 2 (API)       — user-created events จาก DB ผ่าน REST API
     activeFilter   — ค่าจาก filter tab ที่กดอยู่                          */
  let activeFilter    = 'all';
  let currentViewType = 'dayGridMonth'; /* อัพเดทโดย datesSet callback */

  const cal = new FullCalendar.Calendar(document.getElementById('calendar'), {
    initialView:   'dayGridMonth',
    initialDate:   today,
    locale:        'th',
    firstDay:      1,        /* เริ่มต้นสัปดาห์ที่วันจันทร์ */
    height:        'auto',
    headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,listMonth' },
    buttonText:    { today: 'วันนี้', month: 'เดือน', listMonth: 'รายการ' },
    /* งานยังไม่เสร็จอยู่บนสุด เรียงตาม start time, งานเสร็จลงล่าง */
    eventOrder: function (a, b) {
      const aDone = !!(a.extendedProps && a.extendedProps.isCompleted);
      const bDone = !!(b.extendedProps && b.extendedProps.isCompleted);
      if (aDone !== bDone) return aDone ? 1 : -1;   /* pending ก่อน done */
      return (a.start || 0) - (b.start || 0);        /* เรียงตามเวลา */
    },

    dayMaxEvents:  false,

    eventSources: [

      /* Source 1: System events — กรองตาม activeFilter + showRecurring */
      {
        events: function (fetchInfo, success) {
          let evts = sysEvents;


          if (activeFilter === 'done') {
            evts = evts.filter(function (e) { return e.extendedProps && e.extendedProps.isCompleted; });
          } else if (activeFilter !== 'all') {
            // match category ตรงๆ จาก DB value
            evts = evts.filter(function (e) {
              const cat = (e.extendedProps && e.extendedProps.category) || e.category || '';
              return cat === activeFilter;
            });
          }
          success(evts);
        },
        editable: false,
      },

      /* Source 2: User events — fetch จาก REST API ตาม date range ที่ calendar แสดง */
      {
        events: function (fetchInfo, successCb, failureCb) {
          const params = new URLSearchParams({ start: fetchInfo.startStr, end: fetchInfo.endStr });
          fetch(API + '?' + params.toString(), { headers: { 'X-CSRFToken': csrf } })
            .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
            .then(function (data) {

              /* กรอง user events ตาม activeFilter */
              let filtered = data;
              if (activeFilter === 'done') {
                filtered = data.filter(function (e) { return e.extendedProps && e.extendedProps.isCompleted; });
              } else if (activeFilter !== 'all') {
                filtered = data.filter(function (e) {
                  const cat = (e.extendedProps && e.extendedProps.category) || 'general';
                  return cat === activeFilter;
                });
              }

              successCb(filtered.map(function (e) {
                const done = !!(e.extendedProps && e.extendedProps.isCompleted);
                return {
                  id:          'db_' + e.id,
                  title:       e.title,
                  start:       e.start, end: e.end, allDay: e.allDay,
                  color:       done ? DONE_COLOR : PENDING_COLOR,
                  borderColor: 'transparent',
                  classNames:  done ? ['fc-cat-user-event','fc-event-completed'] : ['fc-cat-user-event','fc-event-pending'],
                  extendedProps: Object.assign({}, e.extendedProps, {
                    isSystem: false,
                    dbId:     e.id,   /* เก็บ DB pk ไว้ใช้ PATCH/DELETE */
                  }),
                };
              }));
            })
            .catch(function () { failureCb(); showToast('โหลด events ไม่สำเร็จ', true); });
        },
        editable: true, /* user events drag & drop ได้ */
      },
    ],

    /* eventContent: render Bootstrap Icon + title
       recurring เมื่อ showRecurring=true → dot indicator (เล็กกว่า)
       ทุก event อื่น → Bootstrap Icon + title ปกติ                   */
    eventContent: function (arg) {
      const cat  = (arg.event.extendedProps && arg.event.extendedProps.category) || 'milestone';
      const cfg  = getCfg(cat);
      const isMonthView = arg.view ? arg.view.type === 'dayGridMonth' : currentViewType === 'dayGridMonth';


      const done   = !!(arg.event.extendedProps && arg.event.extendedProps.isCompleted);
      const evId   = arg.event.extendedProps && (arg.event.extendedProps.dbId || arg.event.id);
      const canToggle = !!(evId && !String(evId).startsWith('temp'));

      /* Default: Bootstrap Icon (สี category) + title + toggle */
      return {
        html: '<div class="fc-event-inner">'
            + '<i class="bi ' + (cfg.bsIcon || 'bi-flag-fill') + ' cal-ev-icon"'
            + ' style="color:' + cfg.color + ';opacity:1;filter:brightness(1.15);">'
            + '</i>'
            + '<span class="fc-event-title-text">' + arg.event.title + '</span>'
            + (canToggle
              ? '<button class="fc-ev-toggle" data-id="' + evId + '" data-done="' + done + '" title="' + (done ? 'ยกเลิกเสร็จ' : 'เสร็จแล้ว') + '">'
                + '<i class="bi ' + (done ? 'bi-check-circle-fill' : 'bi-circle') + '"></i>'
                + '</button>'
              : '')
            + '</div>',
      };
    },

    /* eventDidMount: เรียกทุกครั้งที่ event render บน calendar */
    eventDidMount: function (info) {

      /* Toggle done button บน card */
      const toggleBtn = info.el.querySelector('.fc-ev-toggle');
      if (toggleBtn) {
        toggleBtn.addEventListener('click', function (e) {
          e.stopPropagation(); /* ไม่ trigger eventClick */
          const evId   = toggleBtn.dataset.id;
          const isDone = toggleBtn.dataset.done === 'true';
          const newDone = !isDone;
          fetch(API + evId + '/', {
            method:  'PATCH',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
            body:    JSON.stringify({ is_completed: newDone }),
          }).then(function (r) { if (!r.ok) throw new Error(); })
            .then(function () {
              /* อัพเดท local sysEvents ทันที */
              const idx = sysEvents.findIndex(function (e) { return String(e.id) === String(evId); });
              if (idx !== -1) {
                sysEvents[idx].extendedProps = Object.assign({}, sysEvents[idx].extendedProps, { isCompleted: newDone });
                sysEvents[idx].color      = newDone ? DONE_COLOR : PENDING_COLOR;
                sysEvents[idx].classNames = [newDone ? 'fc-event-completed' : 'fc-event-pending'];
              }
              updateRevenueProgress(newDone ? 1 : -1);
              cal.refetchEvents();
            });
        });
      }

      /* tooltip แสดง description เมื่อ hover */
      const desc = info.event.extendedProps.description;
      if (desc) info.el.setAttribute('title', desc);

      /* งานเสร็จ → เทาจาง ไม่ต้องใส่ hot/countdown */
      if (info.event.extendedProps.isCompleted) {
        info.el.classList.add('fc-event-completed');
        info.el.classList.remove('fc-event-pending');
        return;
      }

      /* งาน pending → เส้นเขียวซ้าย */
      info.el.classList.add('fc-event-pending');


      const days = Math.ceil((info.event.start - new Date()) / 86400000);

      /* Glowing effect สำหรับงานที่จะมาใน 3 วัน */
      if (days >= 0 && days <= 3) info.el.classList.add('fc-event-hot');

      /* Countdown badge สำหรับงานที่จะมาใน 7 วัน */
      if (days >= 0 && days <= 7) {
        const badge = document.createElement('span');
        badge.className = 'evt-countdown';
        badge.textContent = days === 0 ? 'วันนี้!' : days + 'd';
        const titleEl = info.el.querySelector('.fc-event-title');
        if (titleEl) titleEl.appendChild(badge);
      }
    },

    /* datesSet: เรียกทุกครั้งที่เปลี่ยน view หรือ navigate */
    datesSet: function (info) {
      currentViewType = info.view.type;
      if (info.view.type === 'listMonth') {
        setTimeout(reformatListView, 50);
      } else if (info.view.type === 'dayGridMonth') {
        setTimeout(applyDayCollapse, 80);
      }
    },

    /* dateClick ปิด — เพิ่มงานผ่านปุ่ม + เท่านั้น */
    eventClick: function (info) { openDetailModal(info.event); },         /* คลิก event → เปิด detail modal */

    /* Drag & Drop: เฉพาะ user events (isSystem=false) → PATCH start date */
    eventDrop: function (info) {
      const props = info.event.extendedProps || {};
      if (props.isSystem) { info.revert(); return; }
      const dbId = props.dbId || (info.event.id.startsWith('db_') ? info.event.id.slice(3) : null);
      if (!dbId) { info.revert(); return; }
      apiPatch(dbId, { start: info.event.startStr, allDay: info.event.allDay })
        .catch(function () { info.revert(); showToast('บันทึกไม่สำเร็จ', true); });
    },
  });

  cal.render();
  mountSubheader(); /* เลื่อน picker ใต้ toolbar */

  /* ── [5] Road to Revenue Progress Bar ────────────────────────────
     นับ sysEvents ที่ is_completed=true / total → แสดงเป็น %
     เรียก updateRevenueProgress() ทุกครั้งที่ mark done ด้วย          */
  function updateRevenueProgress(doneDelta) {
    /* อัพเดต CAL_DONE เมื่อ toggle (doneDelta = +1 หรือ -1) */
    if (doneDelta !== undefined) window.CAL_DONE = (window.CAL_DONE || 0) + doneDelta;
    var total = window.CAL_TOTAL || sysEvents.length;
    var done  = window.CAL_DONE  !== undefined ? window.CAL_DONE : sysEvents.filter(function (e) { return e.extendedProps && e.extendedProps.isCompleted; }).length;
    const pct   = total > 0 ? Math.round((done / total) * 100) : 0;
    const fill     = document.getElementById('rpFill');
    const pctEl    = document.getElementById('rpPct');
    const statusEl = document.getElementById('rpStatus');
    if (fill)     fill.style.width = pct + '%';
    if (pctEl)    pctEl.textContent = pct + '%';
    if (statusEl) statusEl.textContent = done + ' จาก ' + total + ' งานเสร็จแล้ว — ' + (total - done) + ' งานเหลือถึง Revenue';
  }
  setTimeout(updateRevenueProgress, 300); /* รอ cal.render() ก่อน */

  /* ── [6] API helpers — ส่ง request ไป /owner/api/events/ ────────── */
  function apiPost(data)     { return fetch(API, { method: 'POST',  headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }, body: JSON.stringify(data) }).then(function (r) { return r.json(); }); }
  function apiPatch(id, data){ return fetch(API + id + '/', { method: 'PATCH',  headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }, body: JSON.stringify(data) }).then(function (r) { return r.json(); }); }
  function apiDelete(id)     { return fetch(API + id + '/', { method: 'DELETE', headers: { 'X-CSRFToken': csrf } }).then(function (r) { return r.json(); }); }

  /* ── [7] Toast notification + XP pop ─────────────────────────────
     showToast(msg, isErr)
       isErr=false → navy background + "+50 XP ⚡" animation
       isErr=true  → red background                                    */
  function showToast(msg, isErr) {
    const t = document.getElementById('calToast');
    t.textContent = msg;
    t.className = 'cal-toast show ' + (isErr ? 'err' : 'ok');
    clearTimeout(t._tid);
    t._tid = setTimeout(function () { t.classList.remove('show'); }, 2500);
    if (!isErr) {
      const xp = document.createElement('span');
      xp.className = 'xp-pop';
      xp.textContent = '+50 XP ⚡';
      document.body.appendChild(xp);
      setTimeout(function () { xp.remove(); }, 1300);
    }
  }

  /* ── [8] Detail Modal (Todo-style) ───────────────────────────────
     openDetailModal(event) — รับ FullCalendar Event object
     - แสดง title, category badge, date, overdue, description
     - checkbox circle (btnMarkDone) → กดเสร็จได้เลย
     - ปุ่ม Edit / Delete เฉพาะ user events (system events ไม่มีปุ่มลบ)

     State:
       activeDbId       — DB pk ของ user event ที่กำลังดูอยู่ (null = system event)
       activeEventProps — extendedProps + rawTitle + sysEvtId ของ event นั้น
       detailModal      — Bootstrap Modal instance                        */
  let activeDbId = null, activeEventProps = null, detailModal = null;

  function openDetailModal(event) {
    const props    = event.extendedProps || {};
    const isSystem = props.isSystem === true;
    activeDbId = props.dbId ? String(props.dbId) : null;
    activeEventProps = Object.assign({}, props, {
      isSystem: isSystem,
      rawTitle: event.title,
      startStr: event.startStr || '',
      sysEvtId: isSystem ? (event.id || null) : null, /* id ใน DB สำหรับ system events */
    });

    /* category badge — ใช้ ds-badge.cal-{category} จาก dashboard-base.css */
    const catKey = props.category || 'milestone';
    const c = getCfg(catKey);
    document.getElementById('modalCatBadge').innerHTML =
      '<span class="ds-badge cal-' + catKey + '"><i class="bi ' + c.bsIcon + '" style="font-size:.7rem;"></i> ' + c.label + '</span>';

    /* title + done state */
    const titleEl = document.getElementById('modalTitle');
    titleEl.textContent = event.title;

    /* date + overdue badge (ซ่อนถ้างานเสร็จแล้ว) */
    const dateStr   = event.startStr || '';
    const overdueEl = document.getElementById('modalOverdue');
    document.getElementById('modalDate').textContent = dateStr;
    if (!props.isCompleted && dateStr) {
      const todayMid = new Date(); todayMid.setHours(0,0,0,0);
      overdueEl.classList.toggle('d-none', new Date(dateStr + 'T00:00:00') >= todayMid);
    } else {
      overdueEl.classList.add('d-none');
    }

    /* ผู้ทำงาน — แสดงเฉพาะเมื่อมีข้อมูล */
    const assignedChip = document.getElementById('modalAssigned');
    const assignedName = props.assignedTo || '';
    if (assignedName) {
      document.getElementById('modalAssignedName').textContent = assignedName;
      assignedChip.classList.remove('d-none');
    } else {
      assignedChip.classList.add('d-none');
    }

    /* description — ถ้ามี | คั่นให้แสดงเป็น bullet list */
    const descEl = document.getElementById('modalDesc');
    const desc   = props.description || '';
    if (desc.includes('|')) {
      descEl.innerHTML = desc.split('|').map(function (s) {
        return '<div class="modal-desc-item">' + s.trim() + '</div>';
      }).join('');
    } else {
      descEl.textContent = desc;
    }

    /* reset delete confirm panel */
    document.getElementById('deleteConfirm').classList.add('d-none');
    document.getElementById('modalBody').classList.remove('d-none');

    /* checkbox state */
    const isCompleted = !!props.isCompleted;
    const markDoneBtn = document.getElementById('btnMarkDone');
    if (isCompleted) {
      markDoneBtn.classList.add('is-done'); markDoneBtn.disabled = true; titleEl.classList.add('is-done');
    } else {
      markDoneBtn.classList.remove('is-done'); markDoneBtn.disabled = false; titleEl.classList.remove('is-done');
    }

    /* toggle switch state */
    const toggleSwitch = document.getElementById('toggleDone');
    const toggleLabel  = document.getElementById('toggleDoneLabel');
    if (toggleSwitch) {
      toggleSwitch.checked = isCompleted;
      toggleLabel.textContent = isCompleted ? 'เสร็จแล้ว ✓' : 'ยังไม่เสร็จ';
      toggleLabel.style.color = isCompleted ? 'var(--brand-green,#10b981)' : 'var(--brand-muted,#94a3b8)';
    }

    /* action row: แสดง/ซ่อน Edit + Delete */
    const notice  = document.getElementById('modalReadonlyNotice');
    const actions = document.getElementById('modalUserActions');
    if (activeDbId || isSystem) {
      actions.classList.remove('d-none'); notice.classList.add('d-none');
      const deleteBtn = document.getElementById('btnDeleteEvent');
      if (isSystem) { deleteBtn.classList.add('d-none'); } else { deleteBtn.classList.remove('d-none'); }
    } else {
      notice.classList.remove('d-none'); actions.classList.add('d-none');
    }

    detailModal = new bootstrap.Modal(document.getElementById('eventModal'));
    detailModal.show();
  }

  /* Edit — เปิด Edit modal พร้อมข้อมูลเดิม
     System event → strip emoji จาก title แล้ว POST ใหม่ (ไม่ได้ edit ใน DB โดยตรง)
     User event   → fetch ข้อมูลล่าสุดจาก API ก่อนเปิด form                        */
  document.getElementById('btnEditEvent').addEventListener('click', function () {
    if (!activeEventProps) return;
    detailModal && detailModal.hide();
    if (activeEventProps.isSystem) {
      const rawTitle = (activeEventProps.rawTitle || '').replace(/^[\u{1F000}-\u{1FFFF}][️]?\s*/u, '').trim();
      openEditModal({ id: activeDbId || null, title: rawTitle, start: activeEventProps.startStr || '',
        extendedProps: { category: activeEventProps.category || 'milestone', description: activeEventProps.description || '' } }, null);
      return;
    }
    if (!activeDbId) return;
    fetch(API + '?start=2020-01-01&end=2030-01-01', { headers: { 'X-CSRFToken': csrf } })
      .then(function (r) { return r.json(); })
      .then(function (list) {
        const evt = list.find(function (e) { return String(e.id) === String(activeDbId); });
        if (evt) openEditModal(evt, null);
      });
  });

  /* Delete — แสดง confirm panel ก่อนลบจริง */
  document.getElementById('btnDeleteEvent').addEventListener('click', function () {
    document.getElementById('modalBody').classList.add('d-none');
    document.getElementById('modalUserActions').classList.add('d-none');
    document.getElementById('deleteConfirm').classList.remove('d-none');
  });

  document.getElementById('btnConfirmDelete').addEventListener('click', function () {
    if (!activeDbId) return;
    apiDelete(activeDbId)
      .then(function () { detailModal && detailModal.hide(); cal.refetchEvents(); showToast('ลบงานแล้ว'); })
      .catch(function () { showToast('ลบไม่สำเร็จ', true); });
  });

  document.getElementById('btnCancelDelete').addEventListener('click', function () {
    document.getElementById('deleteConfirm').classList.add('d-none');
    document.getElementById('modalBody').classList.remove('d-none');
    document.getElementById('modalUserActions').classList.remove('d-none');
  });

  /* ── [9] Add / Edit Modal ─────────────────────────────────────────
     openEditModal(evtData, prefillDate)
       evtData=null          → เพิ่มงานใหม่ (prefillDate จาก dateClick)
       evtData.id=null       → system event ที่ยังไม่อยู่ใน DB → POST ใหม่
       evtData.id=<number>   → edit user event ที่มีอยู่ใน DB → PATCH      */
  let editingDbId = null;

  function openEditModal(evtData, prefillDate) {
    editingDbId = (evtData && evtData.id) ? evtData.id : null;
    document.getElementById('editModalHeading').textContent =
      editingDbId ? 'แก้ไขงาน' : (evtData ? 'แก้ไข (บันทึกเป็นงานของฉัน)' : 'เพิ่มงานใหม่');
    document.getElementById('editTitle').value    = evtData ? evtData.title : '';
    document.getElementById('editDate').value     = evtData ? (evtData.start || '').slice(0,10) : (prefillDate || '');
    document.getElementById('editCategory').value = evtData ? ((evtData.extendedProps && evtData.extendedProps.category) || 'general') : 'general';
    document.getElementById('editDesc').value     = evtData ? ((evtData.extendedProps && evtData.extendedProps.description) || '') : '';
    document.getElementById('editError').classList.add('d-none');
    new bootstrap.Modal(document.getElementById('editEventModal')).show();
  }

  var btnAddEvent = document.getElementById('btnAddEvent');
  if (btnAddEvent) btnAddEvent.addEventListener('click', function () { openEditModal(null, null); });

  document.getElementById('btnSaveEvent').addEventListener('click', function () {
    const title = document.getElementById('editTitle').value.trim();
    const dt    = document.getElementById('editDate').value;
    if (!title || !dt) { document.getElementById('editError').classList.remove('d-none'); return; }
    document.getElementById('editError').classList.add('d-none');

    const payload = {
      title:       title,
      start:       dt + 'T00:00:00',
      allDay:      true,
      category:    document.getElementById('editCategory').value,
      description: document.getElementById('editDesc').value.trim(),
    };

    const btn = document.getElementById('btnSaveEvent');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>กำลังบันทึก...';

    const promise = editingDbId ? apiPatch(editingDbId, payload) : apiPost(payload);
    promise
      .then(function (data) {
        if (data.error) { showToast(data.error, true); return; }
        bootstrap.Modal.getInstance(document.getElementById('editEventModal')).hide();
        cal.refetchEvents();
        showToast(editingDbId ? 'บันทึกการแก้ไขแล้ว' : 'เพิ่มงานแล้ว');
      })
      .catch(function () { showToast('บันทึกไม่สำเร็จ กรุณาลองใหม่', true); })
      .finally(function () { btn.disabled = false; btn.innerHTML = '<i class="bi bi-check2 me-1"></i>บันทึก'; });
  });

  /* ── [9.5] Month View — collapse day cells ที่มี events > 4 ─────────── */
  var DAY_MAX = 4;
  function applyDayCollapse() {
    if (currentViewType !== 'dayGridMonth') return;

    document.querySelectorAll('#calendar .fc-daygrid-day').forEach(function(cell) {
      var events = cell.querySelectorAll('.fc-daygrid-event-harness');
      if (events.length <= DAY_MAX) {
        /* ลบปุ่มถ้ามี (กรณี filter ทำให้งานน้อยลง) */
        var oldBtn = cell.querySelector('.fc-day-collapse-btn');
        if (oldBtn) oldBtn.remove();
        return;
      }

      var extra    = events.length - DAY_MAX;
      var expanded = cell.dataset.dayExpanded === '1';

      /* สร้างปุ่มครั้งเดียว — CSS จัดการซ่อน/แสดง */
      if (!cell.querySelector('.fc-day-collapse-btn')) {
        var btn = document.createElement('div');
        btn.className = 'fc-day-collapse-btn';
        btn.innerHTML = '+ ' + extra + ' เพิ่มเติม ▼';
        var eventsEl = cell.querySelector('.fc-daygrid-day-events');
        if (eventsEl) eventsEl.appendChild(btn);

        btn.addEventListener('click', function(e) {
          e.stopPropagation();
          var isExpanded = cell.dataset.dayExpanded === '1';
          /* ปิดช่องอื่นทั้งหมดก่อน */
          document.querySelectorAll('#calendar .fc-daygrid-day[data-day-expanded="1"]').forEach(function(other) {
            if (other === cell) return;
            other.dataset.dayExpanded = '';
            var otherBtn = other.querySelector('.fc-day-collapse-btn');
            if (otherBtn) {
              var otherExtra = parseInt(otherBtn.dataset.extra || '0');
              otherBtn.innerHTML = '+ ' + otherExtra + ' เพิ่มเติม ▼';
            }
          });
          cell.dataset.dayExpanded = isExpanded ? '' : '1';
          btn.dataset.extra = extra;
          btn.innerHTML = isExpanded ? ('+ ' + extra + ' เพิ่มเติม ▼') : '▲ ย่อ';
        });
      }
    });
  }

  /* ── [10] List View — reformat day headers + collapse > 6 events ──── */
  function reformatListView() {
    reformatListHeaders();
    applyListCollapse();
  }

  /* แปลงหัว list view เป็น "วันศุกร์ 1 เดือนพฤษภาคม 2569" */
  function reformatListHeaders() {
    document.querySelectorAll('#calendar .fc-list-day[data-date]').forEach(function (dayRow) {
      const dateStr = dayRow.dataset.date;
      if (!dateStr || dayRow.dataset.reformatted) return;
      dayRow.dataset.reformatted = '1';

      var d = new Date(dateStr + 'T12:00:00');
      var weekday = d.toLocaleDateString('th-TH-u-ca-buddhist', { weekday: 'long' });     /* วันศุกร์ */
      var day     = d.toLocaleDateString('th-TH-u-ca-buddhist', { day: 'numeric' });      /* 1 */
      var month   = d.toLocaleDateString('th-TH-u-ca-buddhist', { month: 'long' });       /* พฤษภาคม */
      var year    = d.toLocaleDateString('th-TH-u-ca-buddhist', { year: 'numeric' });     /* 2569 */
      var label   = weekday + ' ' + day + ' เดือน' + month + ' ' + year;

      var cushion = dayRow.querySelector('.fc-list-day-cushion');
      if (cushion) {
        cushion.innerHTML =
          '<span class="fc-list-day-text" style="font-size:.82rem;font-weight:700;color:var(--app-primary);">' +
          label + '</span>';
      }
    });
  }

  /* ย่อ/ขยาย event ถ้าวันนั้นมีมากกว่า 6 รายการ */
  var LIST_MAX = 6;
  function applyListCollapse() {
    /* ลบ collapse buttons เก่าออกก่อน */
    document.querySelectorAll('#calendar .fc-list-collapse-row').forEach(function (el) { el.remove(); });
    /* reset hidden events */
    document.querySelectorAll('#calendar .fc-list-event[data-collapsed]').forEach(function (el) {
      el.style.display = '';
      delete el.dataset.collapsed;
    });

    var rows     = Array.from(document.querySelectorAll('#calendar .fc-list-table tbody tr'));
    var dayMap   = [];   /* [{day: tr, events: [tr, ...]}] */
    var current  = null;

    rows.forEach(function (row) {
      if (row.classList.contains('fc-list-day')) {
        current = { day: row, events: [] };
        dayMap.push(current);
      } else if (row.classList.contains('fc-list-event') && current) {
        current.events.push(row);
      }
    });

    dayMap.forEach(function (group) {
      if (group.events.length <= LIST_MAX) return;
      var extra = group.events.length - LIST_MAX;

      /* ซ่อน event ที่เกิน */
      group.events.slice(LIST_MAX).forEach(function (ev) {
        ev.style.display = 'none';
        ev.dataset.collapsed = '1';
      });

      /* สร้าง toggle row */
      var toggleRow = document.createElement('tr');
      toggleRow.className = 'fc-list-collapse-row';
      toggleRow.innerHTML =
        '<td colspan="4" style="padding:.5rem 1rem;">' +
        '<button class="filter-btn" style="font-size:.78rem;width:100%;justify-content:center;" data-expanded="false">' +
        '<i class="bi bi-chevron-down me-1"></i>ดูเพิ่มอีก ' + extra + ' รายการ' +
        '</button></td>';

      /* แทรกหลัง event ตัวสุดท้ายที่ show */
      var anchor = group.events[LIST_MAX - 1];
      if (!anchor) return;
      anchor.insertAdjacentElement('afterend', toggleRow);

      toggleRow.querySelector('button').addEventListener('click', function () {
        var expanded = this.dataset.expanded === 'true';
        group.events.slice(LIST_MAX).forEach(function (ev) {
          ev.style.display = expanded ? 'none' : '';
        });
        this.dataset.expanded = expanded ? 'false' : 'true';
        this.innerHTML = expanded
          ? '<i class="bi bi-chevron-down me-1"></i>ดูเพิ่มอีก ' + extra + ' รายการ'
          : '<i class="bi bi-chevron-up me-1"></i>ย่อ';
      });
    });
  }

  /* ── [10] Filter Tabs ─────────────────────────────────────────────
     ใช้ event.setProp('display') แทน refetchEvents()
     เพราะ refetchEvents กับ function-based source ใน FC6 มีปัญหา cache */
  function applyFilter() {
    cal.getEvents().forEach(function (event) {
      const props       = event.extendedProps || {};
      const isCompleted = !!props.isCompleted;
      const cat         = props.category || 'general';

      var show;
      if (activeFilter === 'all') {
        show = true;
      } else if (activeFilter === 'done') {
        show = isCompleted;
      } else {
        show = cat === activeFilter;
      }
      event.setProp('display', show ? 'auto' : 'none');
    });
  }

  document.getElementById('legendBar').addEventListener('click', function (e) {
    const item = e.target.closest('.filter-btn');
    if (!item) return;
    document.querySelectorAll('#legendBar .filter-btn').forEach(function (el) { el.classList.remove('active'); });
    item.classList.add('active');
    activeFilter = item.dataset.filter;
    applyFilter();
    if (currentViewType === 'listMonth') setTimeout(reformatListView, 50);
    if (currentViewType === 'dayGridMonth') setTimeout(applyDayCollapse, 80);
  });


  /* ── [11] Mark as Done ────────────────────────────────────────────
     กด checkbox circle (btnMarkDone) → PATCH is_completed=true
     User event  → PATCH ผ่าน apiPatch(activeDbId)
     System event → PATCH โดยตรงด้วย sysEvtId (DB pk ของ CalendarEvent)
     หลัง PATCH: อัพเดท sysEvents local copy → updateRevenueProgress()  */
  /* Toggle switch — สลับ done/undone */
  document.getElementById('toggleDone').addEventListener('change', function () {
    if (!activeDbId && !activeEventProps) return;
    const newDone = this.checked;
    const label   = document.getElementById('toggleDoneLabel');
    const titleEl = document.getElementById('modalTitle');
    label.textContent = newDone ? 'เสร็จแล้ว ✓' : 'ยังไม่เสร็จ';
    label.style.color = newDone ? 'var(--brand-green,#10b981)' : 'var(--brand-muted,#94a3b8)';
    titleEl.classList.toggle('is-done', newDone);

    const sysId   = activeEventProps && activeEventProps.sysEvtId;
    const patchId = activeDbId || sysId;
    if (!patchId) return;
    const patchUrl = API + patchId + '/';

    fetch(patchUrl, {
      method:  'PATCH',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body:    JSON.stringify({ is_completed: newDone }),
    }).then(function (r) { if (!r.ok) throw new Error(); })
      .then(function () {
        /* อัพเดท local sysEvents ทันที — ไม่ต้อง full page reload */
        const idx = sysEvents.findIndex(function (e) {
          return String(e.id) === String(patchId);
        });
        if (idx !== -1) {
          sysEvents[idx].extendedProps = Object.assign({}, sysEvents[idx].extendedProps, { isCompleted: newDone });
          sysEvents[idx].color      = newDone ? DONE_COLOR : PENDING_COLOR;
          sysEvents[idx].classNames = [newDone ? 'fc-event-completed' : 'fc-event-pending'];
        }
        updateRevenueProgress(newDone ? 1 : -1);
        showToast(newDone ? 'งานเสร็จแล้ว!' : 'ยกเลิกสถานะเสร็จแล้ว');
        setTimeout(function () { detailModal && detailModal.hide(); cal.refetchEvents(); }, 350);
      })
      .catch(function () { showToast('บันทึกไม่สำเร็จ', true); });
  });

  document.getElementById('btnMarkDone').addEventListener('click', function () {
    if (!activeDbId && !activeEventProps) return;

    /* visual feedback ทันที ก่อน API response */
    function onDone() {
      const btn = document.getElementById('btnMarkDone');
      const ttl = document.getElementById('modalTitle');
      btn.classList.add('is-done'); btn.disabled = true; ttl.classList.add('is-done');
      setTimeout(function () { detailModal && detailModal.hide(); cal.refetchEvents(); }, 350);
      showToast('งานเสร็จแล้ว!');
    }

    /* User event */
    if (activeDbId) {
      apiPatch(activeDbId, { is_completed: true }).then(onDone).catch(function () { showToast('บันทึกไม่สำเร็จ', true); });
      return;
    }

    /* System event */
    if (activeEventProps && activeEventProps.isSystem && activeEventProps.sysEvtId) {
      fetch(API + activeEventProps.sysEvtId + '/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({ is_completed: true }),
      })
        .then(function (r) { if (!r.ok) throw new Error(); })
        .then(function () {
          /* อัพเดท local sysEvents เพื่อไม่ต้อง reload */
          const idx = sysEvents.findIndex(function (e) { return String(e.id) === String(activeEventProps.sysEvtId); });
          if (idx !== -1) {
            sysEvents[idx].extendedProps = Object.assign({}, sysEvents[idx].extendedProps, { isCompleted: true });
            sysEvents[idx].color      = '#475569';
            sysEvents[idx].classNames = ['fc-event-completed'];
          }
          updateRevenueProgress();
          onDone();
        })
        .catch(function () { showToast('บันทึกไม่สำเร็จ', true); });
    } else {
      showToast('event นี้ mark ไม่ได้', true);
    }
  });

}); /* end DOMContentLoaded */
