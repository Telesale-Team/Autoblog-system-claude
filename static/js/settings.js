/* === Settings DB — Premium JS === */
(function () {
  'use strict';

  const toggle       = document.getElementById('dbToggle');
  const credSection  = document.getElementById('credSection');
  const sqliteInfo   = document.getElementById('sqliteInfo');
  const sqliteSave   = document.getElementById('sqliteSaveWrap');
  const engineWrap   = document.getElementById('engineWrap');
  const engineBadge  = document.getElementById('engineBadge');
  const lblSqlite    = document.getElementById('lblSqlite');
  const lblMysql     = document.getElementById('lblMysql');
  const statusPill   = document.getElementById('statusPill');
  const statusText   = document.getElementById('statusText');
  const cardPill     = document.getElementById('cardPill');
  const cardPillText = document.getElementById('cardPillText');
  const envUseMysql  = document.getElementById('envUseMysql');

  const btnTest    = document.getElementById('btnTest');
  const btnSave    = document.getElementById('btnSave');
  const btnSaveSql = document.getElementById('btnSaveSqlite');
  const spinner    = document.getElementById('spinner');
  const testOk     = document.getElementById('testOk');
  const testErr    = document.getElementById('testErr');
  const testOkMsg  = document.getElementById('testOkMsg');
  const testErrMsg = document.getElementById('testErrMsg');
  const restartBanner    = document.getElementById('restartBanner');
  const restartBannerSql = document.getElementById('restartBannerSqlite');
  const btnEye   = document.getElementById('btnEye');
  const eyeIcon  = document.getElementById('eyeIcon');
  const dbPass   = document.getElementById('dbPassword');

  /* ── Toggle engine ── */
  function applyToggle(mysql) {
    if (mysql) {
      credSection.classList.add('open');
      sqliteInfo.classList.remove('open');
      sqliteSave.classList.add('d-none');
      engineWrap.classList.add('mysql-active');
      engineBadge.textContent = 'Server Mode';
      lblSqlite.classList.remove('lit'); lblSqlite.classList.add('dim');
      lblMysql.classList.add('lit');     lblMysql.classList.remove('dim');
    } else {
      credSection.classList.remove('open');
      sqliteInfo.classList.add('open');
      sqliteSave.classList.remove('d-none');
      engineWrap.classList.remove('mysql-active');
      engineBadge.textContent = 'Local Dev Mode';
      lblMysql.classList.remove('lit'); lblMysql.classList.add('dim');
      lblSqlite.classList.add('lit');   lblSqlite.classList.remove('dim');
    }
    hideResults();
  }

  toggle.addEventListener('change', () => applyToggle(toggle.checked));

  /* ── Password show/hide ── */
  btnEye.addEventListener('click', () => {
    const show = dbPass.type === 'password';
    dbPass.type = show ? 'text' : 'password';
    eyeIcon.className = show ? 'bi bi-eye-slash' : 'bi bi-eye';
  });

  /* ── Helpers ── */
  function getCredentials() {
    return {
      host:     document.getElementById('dbHost').value.trim(),
      port:     parseInt(document.getElementById('dbPort').value) || 3306,
      name:     document.getElementById('dbName').value.trim(),
      user:     document.getElementById('dbUser').value.trim(),
      password: dbPass.value,
    };
  }

  function setLoading(on) {
    if (btnTest) btnTest.disabled = on;
    if (btnSave) btnSave.disabled = on;
    spinner.classList.toggle('d-none', !on);
  }

  function hideResults() {
    testOk.style.display = 'none';
    testErr.style.display = 'none';
    restartBanner.style.display = 'none';
  }

  function showPill(mysql, host) {
    const states = ['state-sqlite', 'state-mysql', 'state-error'];
    [statusPill, cardPill].forEach(el => el.classList.remove(...states));
    if (mysql) {
      [statusPill, cardPill].forEach(el => el.classList.add('state-mysql'));
      statusText.textContent   = 'MySQL — ' + host;
      cardPillText.textContent = 'MySQL Active';
      envUseMysql.textContent  = 'True';
    } else {
      [statusPill, cardPill].forEach(el => el.classList.add('state-sqlite'));
      statusText.textContent   = 'SQLite (Local Dev)';
      cardPillText.textContent = 'SQLite Active';
      envUseMysql.textContent  = 'False';
    }
  }

  function csrfToken() {
    return (document.cookie.split(';')
      .find(c => c.trim().startsWith('csrftoken=')) || '')
      .split('=')[1] || '';
  }

  async function postJSON(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
      body: JSON.stringify(data),
    });
    return res.json();
  }

  /* ── Test Connection ── */
  if (btnTest) {
    btnTest.addEventListener('click', async () => {
      hideResults();
      setLoading(true);
      try {
        const result = await postJSON(window.SETTINGS_URLS.testDb, getCredentials());
        if (result.ok) {
          testOkMsg.textContent = result.message;
          testOk.style.display = 'block';
        } else {
          testErrMsg.textContent = result.error;
          testErr.style.display = 'block';
        }
      } catch {
        testErrMsg.textContent = 'Network error — ไม่สามารถเชื่อมต่อได้';
        testErr.style.display = 'block';
      } finally {
        setLoading(false);
      }
    });
  }

  /* ── Save & Apply (MySQL) ── */
  if (btnSave) {
    btnSave.addEventListener('click', async () => {
      hideResults();
      setLoading(true);
      const creds = getCredentials();
      try {
        const result = await postJSON(window.SETTINGS_URLS.saveDb, { use_mysql: true, ...creds });
        if (result.ok) {
          restartBanner.style.display = 'block';
          showPill(true, creds.host);
        } else {
          testErrMsg.textContent = result.error;
          testErr.style.display = 'block';
        }
      } catch {
        testErrMsg.textContent = 'Network error';
        testErr.style.display = 'block';
      } finally {
        setLoading(false);
      }
    });
  }

  /* ── Apply SQLite ── */
  if (btnSaveSql) {
    btnSaveSql.addEventListener('click', async () => {
      setLoading(true);
      try {
        const result = await postJSON(window.SETTINGS_URLS.saveDb, { use_mysql: false });
        if (result.ok) {
          restartBannerSql.innerHTML =
            '<i class="bi bi-arrow-clockwise me-2"></i><strong>บันทึกแล้ว!</strong> ' +
            'กรุณา restart <code>runserver</code> เพื่อให้ settings มีผล';
          restartBannerSql.style.display = 'block';
          showPill(false, '');
        }
      } catch { /* silent */ }
      finally { setLoading(false); }
    });
  }

})();
