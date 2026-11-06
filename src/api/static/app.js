/* VetCare 24 · Panel de la clínica
   Interfaz para recepción, veterinarios y administración. Consume la misma API REST
   que documenta Swagger (/docs): no duplica reglas de negocio, solo las muestra.
   Las reglas (10 jaulas, celular único, nota firmada, traslapes, State Machine) las
   decide el dominio y llegan aquí como respuestas 409 que se explican en lenguaje claro. */
'use strict';

(() => {
  // ------------------------------------------------------------------ íconos
  const ICONS = {
    paw: '<g stroke="none" fill="currentColor"><ellipse cx="6.5" cy="9" rx="2" ry="2.6"/><ellipse cx="10.2" cy="5.8" rx="2" ry="2.6"/><ellipse cx="13.8" cy="5.8" rx="2" ry="2.6"/><ellipse cx="17.5" cy="9" rx="2" ry="2.6"/><path d="M12 11.2c-3 0-5.6 3.3-5.6 5.6 0 1.8 1.4 2.6 2.9 2.2 1-.3 1.6-.8 2.7-.8s1.7.5 2.7.8c1.5.4 2.9-.4 2.9-2.2 0-2.3-2.6-5.6-5.6-5.6z"/></g>',
    home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    users: '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-3.9 3.1-7 7-7s7 3.1 7 7"/><path d="M16 4a4 4 0 0 1 0 8"/><path d="M22 21c0-3-1.8-5.5-4.5-6.5"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4M16 3v4M3 10h18"/>',
    bed: '<path d="M3 20V6"/><path d="M3 16h18v4"/><path d="M21 16v-4a3 3 0 0 0-3-3h-7v7"/><circle cx="7" cy="11.5" r="2"/>',
    chart: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    bell: '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 8 3 8H3s3-1 3-8"/><path d="M10 20a2 2 0 0 0 4 0"/>',
    stetho: '<path d="M6 3v6a4 4 0 0 0 8 0V3"/><path d="M10 13v2a5 5 0 0 0 10 0v-2"/><circle cx="20" cy="11" r="2"/>',
    siren: '<path d="M7 18v-6a5 5 0 0 1 10 0v6"/><path d="M5 21h14v-3H5z"/><path d="M12 3V2M4.2 6.2l-.7-.7M19.8 6.2l.7-.7M2 12h1M21 12h1"/>',
    code: '<path d="m8 6-6 6 6 6M16 6l6 6-6 6"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    x: '<path d="M6 6l12 12M18 6 6 18"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    phone: '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M11 18h2"/>',
    check: '<path d="m5 12 5 5 9-10"/>',
    checkCircle: '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    alert: '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17.5v.5"/>',
    ban: '<circle cx="12" cy="12" r="9"/><path d="m5.6 5.6 12.8 12.8"/>',
    lock: '<rect x="4" y="10" width="16" height="11" rx="2.5"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    file: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
    heart: '<path d="M3 12h4l2-5 4 10 2-5h6"/>',
    thermo: '<path d="M10 14V5a2 2 0 0 1 4 0v9a4 4 0 1 1-4 0z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    download: '<path d="M12 4v11M7 10l5 5 5-5M4 20h16"/>',
    refresh: '<path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/>',
    chevL: '<path d="m15 6-6 6 6 6"/>',
    chevR: '<path d="m9 6 6 6-6 6"/>',
    door: '<path d="M14 3H6v18h8"/><path d="M14 12h7M18 8l4 4-4 4"/>',
    syringe: '<path d="m18 2 4 4M15 5l4 4M17 7 8 16l-3 1 1-3 9-9M9 9l2 2M12 6l2 2M2 22l4-4"/>',
    scalpel: '<path d="M20 4 8 16l-4 4h6l3-3"/><path d="m14 10 6-6"/>',
    merge: '<path d="M6 3v6a6 6 0 0 0 6 6h6"/><path d="M6 21v-6"/><path d="m15 12 3 3-3 3"/>',
    sparkles: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
    whatsapp: '<path d="M4 20l1.3-3.9A8 8 0 1 1 8 19z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 1c-1-.5-1.8-1.3-2.3-2.3l1-1-1-2L9 9.5z"/>',
    edit: '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    pen: '<path d="M3 21c3 0 4-2 6-2s3 2 6 2"/><path d="M14 4l4 4-7 7H7v-4z"/>',
    trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
  };
  const icon = (name, cls = '') => `<svg class="i ${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ''}</svg>`;
  const hydrateIcons = (root = document) => {
    root.querySelectorAll('[data-icon]').forEach((el) => {
      if (el.dataset.iconDone) return;
      el.insertAdjacentHTML('afterbegin', icon(el.dataset.icon));
      el.dataset.iconDone = '1';
    });
  };

  // ------------------------------------------------------------------ utilidades
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pad = (n) => String(n).padStart(2, '0');
  const isoDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const isoLocal = (d) => `${isoDate(d)}T${pad(d.getHours())}:${pad(d.getMinutes())}:00`;
  const hoy = () => isoDate(new Date());
  const addDays = (iso, n) => { const d = new Date(`${iso}T12:00:00`); d.setDate(d.getDate() + n); return isoDate(d); };
  const parse = (iso) => new Date(String(iso).length === 10 ? `${iso}T00:00:00` : iso);
  const fmtHora = (iso) => parse(iso).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false });
  const fmtFecha = (iso, opts = { weekday: 'long', day: 'numeric', month: 'long' }) => parse(iso).toLocaleDateString('es-MX', opts);
  const fmtFechaCorta = (iso) => parse(iso).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
  const fmtFechaHora = (iso) => `${fmtFechaCorta(iso)} · ${fmtHora(iso)}`;
  const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : '');
  const iniciales = (nombre) => String(nombre || '?').replace(/^(dra?\.|dr\.)\s*/i, '').split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase() || '?';
  const fmtCel = (c) => String(c || '').replace(/^(\d{2})(\d{4})(\d{4})$/, '$1 $2 $3');
  const soloDigitos = (s) => String(s || '').replace(/\D/g, '');
  const avatarClase = (especie) => ({ perro: 'av-perro', gato: 'av-gato' }[String(especie || '').toLowerCase()] || 'av-otro');
  const edad = (fecha) => {
    if (!fecha) return '';
    const n = parse(fecha); const h = new Date();
    let meses = (h.getFullYear() - n.getFullYear()) * 12 + h.getMonth() - n.getMonth();
    if (h.getDate() < n.getDate()) meses -= 1;
    if (meses < 1) return 'menos de 1 mes';
    if (meses < 12) return `${meses} ${meses === 1 ? 'mes' : 'meses'}`;
    const a = Math.floor(meses / 12);
    return `${a} ${a === 1 ? 'año' : 'años'}`;
  };
  const TIPOS = {
    consulta: { label: 'Consulta', dur: '30 min', icon: 'stetho', badge: 'b-blue' },
    vacuna: { label: 'Vacuna', dur: '15 min', icon: 'syringe', badge: 'b-mint' },
    cirugia: { label: 'Cirugía', dur: '2 h', icon: 'scalpel', badge: 'b-amber' },
  };
  const ESTADOS = {
    PROGRAMADA: { label: 'En espera', badge: 'b-amber' },
    EN_ATENCION: { label: 'En atención', badge: 'b-mint' },
    COMPLETADA: { label: 'Completada', badge: 'b-ink' },
    CANCELADA: { label: 'Cancelada', badge: 'b-gray' },
  };

  // ------------------------------------------------------------------ memoria local
  // La API no expone "listar clientes", así que el panel recuerda lo que ya vio
  // (solo como atajo de captura; la fuente de verdad sigue siendo la API).
  const store = {
    get(k, d) { try { const v = localStorage.getItem(`vc24.${k}`); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(`vc24.${k}`, JSON.stringify(v)); } catch (e) { /* almacenamiento no disponible */ } },
  };
  const mem = {
    vets: [],
    vet: store.get('vet', ''),
    mascotas: store.get('mascotas', {}),
    citas: store.get('citas', {}),
    clientes: store.get('clientes', []),
  };
  function recordarExpediente(exp) {
    exp.mascotas.forEach((m) => {
      mem.mascotas[m.id] = { id: m.id, nombre: m.nombre, especie: m.especie, raza: m.raza, alergias: m.alergias || [], propietario: exp.nombre, celular: exp.celular, visto: Date.now() };
    });
    store.set('mascotas', mem.mascotas);
    mem.clientes = [{ celular: exp.celular, nombre: exp.nombre, mascotas: exp.mascotas.length }, ...mem.clientes.filter((c) => c.celular !== exp.celular)].slice(0, 8);
    store.set('clientes', mem.clientes);
  }
  function olvidarMascota(id) { delete mem.mascotas[id]; store.set('mascotas', mem.mascotas); }
  function recordarCita(c) { mem.citas[c.id] = c; store.set('citas', mem.citas); }
  async function mascotaInfo(id) {
    if (mem.mascotas[id]) return mem.mascotas[id];
    try {
      const h = await api('GET', `/mascotas/${encodeURIComponent(id)}/historial`);
      mem.mascotas[id] = { id, nombre: h.mascota.nombre, especie: h.mascota.especie, raza: h.mascota.raza, alergias: h.mascota.alergias, propietario: h.propietario, celular: h.celular, visto: Date.now() };
      store.set('mascotas', mem.mascotas);
      return mem.mascotas[id];
    } catch (e) {
      return { id, nombre: 'Paciente', especie: '', propietario: '', celular: '' };
    }
  }
  async function completarNombres(root) {
    const nodos = $$('[data-mascota]', root);
    await Promise.all(nodos.map(async (n) => {
      const m = await mascotaInfo(n.dataset.mascota);
      const campo = n.dataset.campo || 'nombre';
      if (campo === 'avatar') { n.textContent = iniciales(m.nombre); n.className = `avatar ${avatarClase(m.especie)}`; }
      else if (campo === 'propietario') n.textContent = m.propietario || '';
      else if (campo === 'dueno') n.textContent = m.propietario ? `${m.propietario} · ${fmtCel(m.celular)}` : '';
      else n.textContent = m.nombre;
    }));
  }
  const vetNombre = (id) => (mem.vets.find((v) => v.id === id) || {}).nombre || 'Veterinario';

  // ------------------------------------------------------------------ API
  class ApiError extends Error {
    constructor(status, titulo, detalle, codigo) { super(detalle); this.status = status; this.titulo = titulo; this.detalle = detalle; this.codigo = codigo; }
  }
  const TITULOS = {
    ClienteExistenteException: 'Este celular ya está registrado',
    CapacidadMaximaJaulasAlcanzada: 'No hay jaulas disponibles',
    TraslapeDeCitas: 'Ese horario ya está ocupado',
    TransicionInvalida: 'Esa acción no está permitida',
    NotaFirmadaInmutable: 'La nota ya está firmada',
    PacienteYaInternado: 'El paciente ya está internado',
    PacienteNoInternado: 'El paciente no está internado',
    ConflictoDeConcurrencia: 'Alguien más hizo un cambio',
  };
  const CAMPOS = { celular: 'Celular', nombre: 'Nombre', especie: 'Especie', peso: 'Peso', inicio: 'Fecha y hora', diagnostico: 'Diagnóstico', motivo_ingreso: 'Motivo de ingreso', temperatura: 'Temperatura', frecuencia_cardiaca: 'Frecuencia cardiaca', frecuencia_respiratoria: 'Frecuencia respiratoria', cedula: 'Cédula', veterinario_id: 'Veterinario', mascota_id: 'Paciente', desde: 'Desde', hasta: 'Hasta' };
  function aError(status, data) {
    if (data && typeof data === 'object' && data.error) {
      const titulo = TITULOS[data.error] || (status === 404 ? 'No lo encontramos' : status === 422 ? 'Revisa los datos' : 'No se pudo completar');
      return new ApiError(status, titulo, data.detalle, data.error);
    }
    if (status === 422 && data && Array.isArray(data.detail)) {
      const partes = data.detail.map((d) => {
        const campo = (d.loc || []).filter((x) => typeof x === 'string' && x !== 'body' && x !== 'query').pop();
        const msg = String(d.msg || '').replace(/^Value error, /, '');
        return campo ? `${CAMPOS[campo] || campo}: ${msg}` : msg;
      });
      return new ApiError(422, 'Revisa los datos', partes.join(' · '), 'Validacion');
    }
    return new ApiError(status, 'Algo salió mal', `El servidor respondió ${status}.`, 'Http');
  }
  async function api(method, path, body) {
    let res;
    try {
      res = await fetch(path, { method, headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
    } catch (e) {
      throw new ApiError(0, 'Sin conexión', 'No pudimos contactar al servidor. Si está en Render, puede tardar unos segundos en despertar.', 'Red');
    }
    const tipo = res.headers.get('content-type') || '';
    const data = tipo.includes('json') ? await res.json() : await res.text();
    if (!res.ok) throw aError(res.status, data);
    return data;
  }

  // ------------------------------------------------------------------ UI: toasts, modal, errores
  function toast(tipo, titulo, msg = '') {
    const el = document.createElement('div');
    el.className = `toast ${tipo}`;
    el.innerHTML = `${icon(tipo === 'ok' ? 'checkCircle' : tipo === 'err' ? 'ban' : 'alert')}<div><b>${esc(titulo)}</b>${msg ? `<span>${esc(msg)}</span>` : ''}</div>`;
    $('#toasts').appendChild(el);
    setTimeout(() => { el.style.transition = 'opacity .3s'; el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, tipo === 'err' ? 6500 : 4200);
  }
  function abrirModal(titulo, html, { ancho = false } = {}) {
    $('#modalTitle').textContent = titulo;
    const body = $('#modalBody');
    body.innerHTML = html;
    $('.modal').classList.toggle('wide', ancho);
    $('#modal').hidden = false;
    hydrateIcons(body);
    const primero = body.querySelector('input:not([type=hidden]), select, textarea');
    if (primero) primero.focus({ preventScroll: true });
    return body;
  }
  function cerrarModal() { $('#modal').hidden = true; $('#modalBody').innerHTML = ''; }
  function alertaHTML(err, extra = '') {
    const regla = err.status === 409;
    return `<div class="alert-box ${regla ? 'red' : 'amber'}">${icon(regla ? 'ban' : 'alert')}<div class="grow"><h3>${esc(err.titulo)}</h3><p>${esc(err.detalle)}</p>${regla ? '<p class="muted" style="margin-top:6px;font-size:12px">Regla de negocio del dominio · HTTP 409</p>' : ''}${extra}</div></div>`;
  }
  function mostrarError(err, contenedor) {
    if (!(err instanceof ApiError)) { console.error(err); err = new ApiError(0, 'Algo salió mal', 'Ocurrió un error inesperado.', 'JS'); }
    if (contenedor) { contenedor.innerHTML = alertaHTML(err); contenedor.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); return; }
    if (err.status === 409) {
      const b = abrirModal('Regla de negocio', `${alertaHTML(err)}<div class="row end"><button class="btn btn-primary" data-close>Entendido</button></div>`);
      hydrateIcons(b);
    } else toast('err', err.titulo, err.detalle);
  }
  async function ocupado(btn, fn) {
    const html = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span>${esc(btn.dataset.busy || 'Guardando…')}`;
    try { return await fn(); } finally { if (btn.isConnected) { btn.disabled = false; btn.innerHTML = html; } }
  }
  const cargando = (txt = 'Cargando…') => `<div class="loading"><span class="spinner"></span>${esc(txt)}</div>`;
  const vacio = (ico, titulo, texto, accion = '') => `<div class="empty"><div class="big">${icon(ico)}</div><h3>${esc(titulo)}</h3><p style="margin:0;max-width:420px">${esc(texto)}</p>${accion}</div>`;

  // ------------------------------------------------------------------ veterinarios
  async function cargarVets() {
    try { mem.vets = await api('GET', '/veterinarios'); } catch (e) { mem.vets = []; }
    if (!mem.vets.some((v) => v.id === mem.vet)) mem.vet = (mem.vets[0] || {}).id || '';
    store.set('vet', mem.vet);
    const sel = $('#vetActual');
    sel.innerHTML = mem.vets.length
      ? mem.vets.map((v) => `<option value="${esc(v.id)}" ${v.id === mem.vet ? 'selected' : ''}>${esc(v.nombre)}</option>`).join('')
      : '<option value="">Sin veterinarios</option>';
  }
  const vetOptions = (sel = mem.vet) => mem.vets.map((v) => `<option value="${esc(v.id)}" ${v.id === sel ? 'selected' : ''}>${esc(v.nombre)}</option>`).join('');
  function exigirVet() {
    if (mem.vets.length) return true;
    abrirModal('Primero registra un veterinario', `${vacio('stetho', 'No hay veterinarios', 'Las citas, emergencias, notas e ingresos se asignan a un veterinario. Registra uno o carga los datos de demostración.')}<div class="row end"><a class="btn btn-primary" href="#/equipo" data-close>Ir a Veterinarios</a></div>`);
    return false;
  }

  // ------------------------------------------------------------------ selector de paciente
  function selectorPacienteHTML(preId = '') {
    const recientes = Object.values(mem.mascotas).sort((a, b) => (b.visto || 0) - (a.visto || 0)).slice(0, 12);
    return `<div class="field" data-pp>
      <label>Paciente</label>
      <div class="row" style="flex-wrap:nowrap">
        <div class="input-icon grow">${icon('phone')}<input class="input" data-pp-cel inputmode="numeric" placeholder="Celular del dueño para buscar"></div>
        <button class="btn btn-ghost" type="button" data-pp-buscar>${icon('search')}Buscar</button>
      </div>
      <div class="chips" data-pp-lista>${chipsPacientes(recientes, preId)}</div>
      <span class="hint">${recientes.length ? 'Toca un paciente para seleccionarlo.' : 'Busca al dueño por celular para ver sus mascotas.'}</span>
      <input type="hidden" data-pp-valor value="${esc(preId)}">
    </div>`;
  }
  function chipsPacientes(lista, sel) {
    return lista.map((m) => `<button type="button" class="chip ${m.id === sel ? 'on' : ''}" data-pp-id="${esc(m.id)}"><span class="avatar ${avatarClase(m.especie)}" style="width:22px;height:22px;border-radius:7px;font-size:11px">${esc(iniciales(m.nombre))}</span>${esc(m.nombre)}<span class="muted" style="font-weight:400">· ${esc(String(m.propietario || '').split(' ')[0])}</span></button>`).join('');
  }
  function activarSelector(root, alCambiar = () => {}) {
    const caja = $('[data-pp]', root);
    const lista = $('[data-pp-lista]', caja);
    const valor = $('[data-pp-valor]', caja);
    lista.addEventListener('click', (e) => {
      const b = e.target.closest('[data-pp-id]');
      if (!b) return;
      valor.value = b.dataset.ppId;
      $$('.chip', lista).forEach((c) => c.classList.toggle('on', c === b));
      alCambiar(valor.value);
    });
    const buscar = async () => {
      const cel = soloDigitos($('[data-pp-cel]', caja).value);
      if (!cel) return;
      lista.innerHTML = '<span class="muted">Buscando…</span>';
      try {
        const exp = await api('GET', `/expedientes/${cel}`);
        recordarExpediente(exp);
        lista.innerHTML = exp.mascotas.length ? chipsPacientes(exp.mascotas.map((m) => mem.mascotas[m.id]), valor.value) : '<span class="muted">Ese cliente aún no tiene mascotas registradas.</span>';
        if (exp.mascotas.length === 1) $('[data-pp-id]', lista).click();
      } catch (err) {
        lista.innerHTML = `<span class="muted">${esc(err.status === 404 ? 'No hay un cliente con ese celular.' : err.detalle)}</span>`;
      }
    };
    $('[data-pp-buscar]', caja).addEventListener('click', buscar);
    $('[data-pp-cel]', caja).addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); buscar(); } });
    return () => valor.value;
  }

  // ------------------------------------------------------------------ flujos (modales)
  function modalNuevaCita({ mascotaId = '', fecha = '' } = {}) {
    if (!exigirVet()) return;
    const f0 = fecha && fecha >= hoy() ? fecha : hoy();
    const body = abrirModal('Agendar cita', `
      ${selectorPacienteHTML(mascotaId)}
      <div class="field"><label>Servicio</label>
        <div class="seg" data-tipo>${Object.entries(TIPOS).map(([k, t], i) => `<button type="button" data-v="${k}" class="${i === 0 ? 'on' : ''}">${icon(t.icon)}${t.label}<small>${t.dur}</small></button>`).join('')}</div>
        <span class="hint">La duración la asigna el sistema según el servicio (US-01).</span>
      </div>
      <div class="form-grid">
        <div class="field"><label>Veterinario</label><select class="select input" data-vet>${vetOptions()}</select></div>
        <div class="field"><label>Fecha</label><input class="input" type="date" data-fecha min="${hoy()}" value="${f0}"></div>
      </div>
      <div class="field"><label>Horarios disponibles</label><div data-slots>${cargando('Buscando espacios libres…')}</div></div>
      <div data-err></div>
      <div class="row between"><span class="muted" data-resumen>Elige paciente y horario.</span><button class="btn btn-mint btn-lg" data-ok data-busy="Agendando…">${icon('check')}Agendar cita</button></div>
    `, { ancho: true });
    let tipo = 'consulta'; let slot = '';
    const pacienteSel = activarSelector(body, () => resumen());
    const resumen = () => {
      const m = mem.mascotas[pacienteSel()];
      $('[data-resumen]', body).textContent = slot ? `${m ? m.nombre : 'Paciente'} · ${TIPOS[tipo].label} · ${fmtFecha(slot)} a las ${fmtHora(slot)}` : 'Elige paciente y horario.';
    };
    const cargarSlots = async () => {
      slot = ''; resumen();
      const caja = $('[data-slots]', body);
      caja.innerHTML = cargando('Buscando espacios libres…');
      try {
        const fecha = $('[data-fecha]', body).value;
        const vet = $('[data-vet]', body).value;
        let libres = await api('GET', `/citas/espacios-libres?fecha=${fecha}&veterinario_id=${encodeURIComponent(vet)}&tipo=${tipo}`);
        const ahora = new Date();
        libres = libres.filter((s) => parse(s.inicio) > ahora);
        caja.innerHTML = libres.length ? `<div class="slots">${libres.map((s) => `<button type="button" class="slot" data-slot="${esc(s.inicio)}">${fmtHora(s.inicio)}</button>`).join('')}</div>` : vacio('calendar', 'Sin horarios libres', 'Prueba otro día u otro veterinario. Horario de servicio: 08:00 a 20:00.');
      } catch (err) { caja.innerHTML = alertaHTML(err); }
    };
    $('[data-slots]', body).addEventListener('click', (e) => {
      const b = e.target.closest('[data-slot]');
      if (!b) return;
      slot = b.dataset.slot;
      $$('.slot', body).forEach((s) => s.classList.toggle('on', s === b));
      resumen();
    });
    $('[data-tipo]', body).addEventListener('click', (e) => {
      const b = e.target.closest('[data-v]');
      if (!b) return;
      tipo = b.dataset.v;
      $$('[data-tipo] button', body).forEach((x) => x.classList.toggle('on', x === b));
      cargarSlots();
    });
    $('[data-fecha]', body).addEventListener('change', cargarSlots);
    $('[data-vet]', body).addEventListener('change', cargarSlots);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      const err = $('[data-err]', body); err.innerHTML = '';
      if (!pacienteSel()) return mostrarError(new ApiError(422, 'Falta el paciente', 'Selecciona la mascota que tendrá la cita.'), err);
      if (!slot) return mostrarError(new ApiError(422, 'Falta el horario', 'Selecciona uno de los horarios disponibles.'), err);
      try {
        const r = await api('POST', '/citas', { mascota_id: pacienteSel(), veterinario_id: $('[data-vet]', body).value, tipo, inicio: slot });
        recordarCita(r.cita);
        cerrarModal();
        toast('ok', 'Cita agendada', `${fmtFecha(r.cita.inicio)} de ${fmtHora(r.cita.inicio)} a ${fmtHora(r.cita.fin)}. Se programaron los recordatorios por WhatsApp.`);
        if (ruta().nombre === 'agenda') { estadoAgenda.fecha = r.cita.inicio.slice(0, 10); render(); } else if (ruta().nombre === 'inicio') render();
      } catch (er) { mostrarError(er, err); if (er.codigo === 'TraslapeDeCitas') cargarSlots(); }
    }));
    cargarSlots();
  }

  function modalEmergencia(mascotaId = '') {
    if (!exigirVet()) return;
    const body = abrirModal('Registrar emergencia', `
      <div class="alert-box red">${icon('siren')}<div><h3>Atención inmediata</h3><p>La emergencia pasa al primer lugar de la cola y se alerta al veterinario (US-03).</p></div></div>
      ${selectorPacienteHTML(mascotaId)}
      <div class="field"><label>Veterinario que atiende</label><select class="select input" data-vet>${vetOptions()}</select></div>
      <div data-err></div>
      <button class="btn btn-danger btn-lg" data-ok data-busy="Registrando…">${icon('siren')}Registrar emergencia</button>
    `);
    const pacienteSel = activarSelector(body);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      const err = $('[data-err]', body); err.innerHTML = '';
      if (!pacienteSel()) return mostrarError(new ApiError(422, 'Falta el paciente', 'Selecciona la mascota que llegó de urgencia.'), err);
      try {
        const r = await api('POST', '/emergencias', { mascota_id: pacienteSel(), veterinario_id: $('[data-vet]', body).value });
        recordarCita(r.cita);
        const m = await mascotaInfo(r.cita.mascota_id);
        const b = abrirModal('Emergencia registrada', `
          <div style="text-align:center;display:flex;flex-direction:column;align-items:center;gap:8px;padding:8px 0 4px">
            <div class="ring" style="--p:100;--ring-color:var(--red)"><div><b>#${r.posicion_en_cola}</b><small>en la cola</small></div></div>
            <h3 style="margin:8px 0 0;font-family:var(--display);font-size:22px">${esc(m.nombre)} será atendido primero</h3>
            <p class="muted" style="margin:0">${esc(r.mensaje)} · ${esc(vetNombre(r.cita.veterinario_id))}</p>
          </div>
          <div class="row end"><button class="btn btn-ghost" data-close>Cerrar</button><a class="btn btn-primary" href="#/agenda" data-close>${icon('calendar')}Ver agenda</a></div>`);
        hydrateIcons(b);
        if (ruta().nombre === 'agenda' || ruta().nombre === 'inicio') { estadoAgenda.fecha = r.cita.inicio.slice(0, 10); render(); }
      } catch (er) { mostrarError(er, err); }
    }));
  }

  function modalInternar(mascotaId = '') {
    if (!exigirVet()) return;
    const body = abrirModal('Internar paciente', `
      ${selectorPacienteHTML(mascotaId)}
      <div class="field"><label>Veterinario responsable</label><select class="select input" data-vet>${vetOptions()}</select></div>
      <div class="field"><label>Motivo de ingreso</label><textarea class="input" data-motivo placeholder="Ej. Observación postoperatoria, deshidratación…"></textarea></div>
      <div data-err></div>
      <div class="row end"><button class="btn btn-ghost" data-close>Cancelar</button><button class="btn btn-mint btn-lg" data-ok data-busy="Internando…">${icon('bed')}Internar</button></div>
    `);
    const pacienteSel = activarSelector(body);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      const err = $('[data-err]', body); err.innerHTML = '';
      if (!pacienteSel()) return mostrarError(new ApiError(422, 'Falta el paciente', 'Selecciona la mascota que se va a internar.'), err);
      const motivo = $('[data-motivo]', body).value.trim();
      if (!motivo) return mostrarError(new ApiError(422, 'Falta el motivo', 'Escribe por qué se interna al paciente.'), err);
      try {
        const r = await api('POST', '/hospitalizacion/ingresos', { mascota_id: pacienteSel(), veterinario_id: $('[data-vet]', body).value, motivo_ingreso: motivo });
        const j = r.jaulas.find((x) => x.mascota_id === pacienteSel());
        const m = await mascotaInfo(pacienteSel());
        cerrarModal();
        toast('ok', `${m.nombre} quedó internado`, `Jaula ${j ? j.numero : ''} · ocupación ${r.ocupadas}/${r.capacidad}`);
        if (ruta().nombre === 'hospitalizacion' || ruta().nombre === 'inicio') render();
      } catch (er) {
        if (er.codigo === 'CapacidadMaximaJaulasAlcanzada') {
          err.innerHTML = alertaHTML(er, '<p style="margin-top:8px">La operación se revirtió y la ocupación sigue en <b>10/10</b>. Da de alta a un paciente para liberar una jaula.</p>');
          hydrateIcons(err);
        } else mostrarError(er, err);
      }
    }));
  }

  function modalNuevoCliente(celular = '') {
    const body = abrirModal('Nuevo cliente', `
      <div class="form-grid">
        <div class="field full"><label>Nombre completo</label><input class="input" data-nombre placeholder="Ej. Ana Martínez"></div>
        <div class="field full"><label>Celular</label><div class="input-icon">${icon('phone')}<input class="input" data-cel inputmode="numeric" placeholder="10 dígitos" value="${esc(celular)}"></div><span class="hint">Es el dato único del cliente: no puede repetirse (US-04).</span></div>
      </div>
      <div data-err></div>
      <div class="row end"><button class="btn btn-ghost" data-close>Cancelar</button><button class="btn btn-primary btn-lg" data-ok data-busy="Registrando…">${icon('check')}Registrar y agregar mascota</button></div>
    `);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      const err = $('[data-err]', body); err.innerHTML = '';
      const cel = soloDigitos($('[data-cel]', body).value);
      try {
        const exp = await api('POST', '/expedientes', { nombre: $('[data-nombre]', body).value.trim(), celular: cel });
        recordarExpediente(exp);
        toast('ok', 'Cliente registrado', `${exp.nombre} · ${fmtCel(exp.celular)}`);
        location.hash = `#/recepcion/${exp.celular}`;
        setTimeout(() => modalMascota(exp.celular, exp.nombre), 250);
      } catch (er) {
        if (er.codigo === 'ClienteExistenteException') {
          err.innerHTML = alertaHTML(er, `<div class="row" style="margin-top:10px"><a class="btn btn-primary btn-sm" href="#/recepcion/${esc(cel)}" data-close>${icon('file')}Abrir su expediente</a></div>`);
          hydrateIcons(err);
        } else mostrarError(er, err);
      }
    }));
  }

  function modalMascota(celular, dueno = '') {
    const body = abrirModal(`Agregar mascota${dueno ? ` · ${dueno}` : ''}`, `
      <div class="form-grid">
        <div class="field"><label>Nombre</label><input class="input" data-f="nombre" placeholder="Ej. Firulais"></div>
        <div class="field"><label>Especie</label><select class="select input" data-f="especie"><option value="perro">Perro</option><option value="gato">Gato</option><option value="ave">Ave</option><option value="conejo">Conejo</option><option value="otro">Otro</option></select></div>
        <div class="field"><label>Raza</label><input class="input" data-f="raza" placeholder="Opcional"></div>
        <div class="field"><label>Sexo</label><select class="select input" data-f="sexo"><option value="">Sin especificar</option><option>Macho</option><option>Hembra</option></select></div>
        <div class="field"><label>Fecha de nacimiento</label><input class="input" type="date" data-f="fecha_nacimiento" max="${hoy()}"></div>
        <div class="field"><label>Peso (kg)</label><input class="input" type="number" step="0.1" min="0" data-f="peso" placeholder="Opcional"></div>
        <div class="field full"><label>Alergias</label><input class="input" data-f="alergias" placeholder="Separadas por coma, ej. penicilina, pollo"><span class="hint">Se mostrarán en rojo en todo el sistema.</span></div>
      </div>
      <div data-err></div>
      <div class="row end"><button class="btn btn-ghost" data-close>Cerrar</button><button class="btn btn-mint btn-lg" data-ok data-busy="Guardando…">${icon('plus')}Agregar mascota</button></div>
    `);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      const err = $('[data-err]', body); err.innerHTML = '';
      const v = (k) => $(`[data-f="${k}"]`, body).value.trim();
      const datos = { nombre: v('nombre'), especie: v('especie'), raza: v('raza'), sexo: v('sexo'), alergias: v('alergias') ? v('alergias').split(',').map((s) => s.trim()).filter(Boolean) : [] };
      if (v('fecha_nacimiento')) datos.fecha_nacimiento = v('fecha_nacimiento');
      if (v('peso')) datos.peso = v('peso');
      try {
        const exp = await api('POST', `/expedientes/${celular}/mascotas`, datos);
        recordarExpediente(exp);
        cerrarModal();
        toast('ok', `${datos.nombre} agregado`, `Ahora ${exp.nombre} tiene ${exp.mascotas.length} ${exp.mascotas.length === 1 ? 'mascota' : 'mascotas'}.`);
        if (ruta().nombre === 'recepcion') render();
      } catch (er) { mostrarError(er, err); }
    }));
  }

  function modalFusion(exp) {
    const opts = (sel) => exp.mascotas.map((m) => `<option value="${esc(m.id)}" ${m.id === sel ? 'selected' : ''}>${esc(m.nombre)} · ${esc(m.especie)}${m.raza ? ` · ${esc(m.raza)}` : ''}</option>`).join('');
    const body = abrirModal('Fusionar expedientes duplicados', `
      <div class="alert-box amber">${icon('merge')}<div><h3>¿La misma mascota quedó registrada dos veces?</h3><p>El historial del duplicado pasa al expediente que se conserva y el duplicado se elimina (US-05).</p></div></div>
      <div class="form-grid">
        <div class="field"><label>Duplicado (se elimina)</label><select class="select input" data-origen>${opts(exp.mascotas[exp.mascotas.length - 1].id)}</select></div>
        <div class="field"><label>Se conserva</label><select class="select input" data-destino>${opts(exp.mascotas[0].id)}</select></div>
      </div>
      <div data-err></div>
      <div class="row end"><button class="btn btn-ghost" data-close>Cancelar</button><button class="btn btn-primary btn-lg" data-ok data-busy="Fusionando…">${icon('merge')}Fusionar</button></div>
    `);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      const err = $('[data-err]', body); err.innerHTML = '';
      const origen = $('[data-origen]', body).value; const destino = $('[data-destino]', body).value;
      if (origen === destino) return mostrarError(new ApiError(422, 'Elige dos mascotas distintas', 'El duplicado y el expediente que se conserva no pueden ser el mismo.'), err);
      try {
        const r = await api('POST', `/expedientes/${exp.celular}/mascotas/fusion`, { origen_id: origen, destino_id: destino });
        olvidarMascota(origen); recordarExpediente(r);
        cerrarModal(); toast('ok', 'Expedientes fusionados', 'El historial quedó en un solo expediente.');
        render();
      } catch (er) { mostrarError(er, err); }
    }));
  }

  // ------------------------------------------------------------------ páginas
  async function pgInicio(view) {
    const [ocu, cola, signos, avisos] = await Promise.allSettled([
      api('GET', '/hospitalizacion/ocupacion'),
      api('GET', `/citas/cola?fecha=${hoy()}`),
      api('GET', '/hospitalizacion/signos-pendientes?horas=4'),
      api('GET', '/notificaciones'),
    ]);
    const o = ocu.value || { ocupadas: 0, capacidad: 10, disponibles: 10, porcentaje: 0 };
    const c = cola.value || []; const s = signos.value || []; const a = (avisos.value || []).slice(-5).reverse();
    c.forEach(recordarCita);
    const h = new Date().getHours();
    const saludo = h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches';
    const vet = mem.vets.find((v) => v.id === mem.vet);
    const emergencias = c.filter((x) => x.es_emergencia).length;
    const nivel = o.ocupadas >= o.capacidad ? 'full' : o.ocupadas >= 8 ? 'warn' : '';
    view.innerHTML = `
      ${mem.vets.length ? '' : `<div class="card" style="border-color:#BFE9DD;background:#F3FBF8"><div class="row between"><div class="row" style="flex-wrap:nowrap"><div class="avatar av-otro">${icon('sparkles')}</div><div><h3 style="margin:0;font-family:var(--display)">¡Bienvenido! El sistema está vacío</h3><p class="sub">Registra un veterinario o carga datos de ejemplo para recorrer el sistema.</p></div></div><div class="row"><a class="btn btn-ghost" href="#/equipo">${icon('stetho')}Registrar veterinario</a><button class="btn btn-mint" data-demo data-busy="Cargando…">${icon('sparkles')}Cargar datos de demostración</button></div></div></div>`}
      <section class="hero">
        <div><h2>${saludo}${vet ? `, ${esc(vet.nombre)}` : ''}</h2><p>${cap(fmtFecha(hoy()))}. Esto es lo que pasa hoy en la clínica.</p></div>
        <div class="row">
          <button class="btn btn-mint btn-lg" data-accion="cita">${icon('calendar')}Nueva cita</button>
          <a class="btn btn-ghost btn-lg" href="#/recepcion">${icon('search')}Buscar cliente</a>
          <button class="btn btn-ghost btn-lg" data-accion="internar">${icon('bed')}Internar</button>
        </div>
      </section>
      <section class="grid g-4">
        <a class="card kpi" href="#/hospitalizacion" style="text-decoration:none;color:inherit">
          <div class="kpi-top"><span class="kpi-label">Jaulas ocupadas</span><span class="kpi-ico" style="background:var(--teal-soft);color:var(--teal)">${icon('bed')}</span></div>
          <div class="kpi-num">${o.ocupadas}<small> / ${o.capacidad}</small></div>
          <div class="bar ${nivel}"><span style="width:${(o.ocupadas / o.capacidad) * 100}%"></span></div>
        </a>
        <a class="card kpi" href="#/agenda" style="text-decoration:none;color:inherit">
          <div class="kpi-top"><span class="kpi-label">Pacientes en espera hoy</span><span class="kpi-ico" style="background:var(--blue-soft);color:var(--blue-text)">${icon('clock')}</span></div>
          <div class="kpi-num">${c.length}</div><span class="muted" style="font-size:13px">Citas programadas en la cola</span>
        </a>
        <a class="card kpi" href="#/agenda" style="text-decoration:none;color:inherit">
          <div class="kpi-top"><span class="kpi-label">Emergencias activas</span><span class="kpi-ico" style="background:var(--red-soft);color:var(--red-text)">${icon('siren')}</span></div>
          <div class="kpi-num" style="${emergencias ? 'color:var(--red-text)' : ''}">${emergencias}</div><span class="muted" style="font-size:13px">Siempre van primero en la cola</span>
        </a>
        <a class="card kpi" href="#/hospitalizacion" style="text-decoration:none;color:inherit">
          <div class="kpi-top"><span class="kpi-label">Signos vitales pendientes</span><span class="kpi-ico" style="background:var(--amber-soft);color:var(--amber-text)">${icon('heart')}</span></div>
          <div class="kpi-num" style="${s.length ? 'color:var(--amber-text)' : ''}">${s.length}</div><span class="muted" style="font-size:13px">Toma vencida (más de 4 h)</span>
        </a>
      </section>
      <section class="grid g-side">
        <div class="card">
          <div class="card-head"><h2>Siguientes en la cola</h2><a class="btn btn-ghost btn-sm" href="#/agenda">Ver agenda ${icon('chevR')}</a></div>
          ${c.length ? `<div class="list">${c.slice(0, 6).map((x) => `
            <div class="list-item">
              <span class="avatar av-otro" data-mascota="${esc(x.mascota_id)}" data-campo="avatar">·</span>
              <div class="grow"><div class="title" data-mascota="${esc(x.mascota_id)}">Paciente</div><div class="muted ellipsis" style="font-size:13px">${esc(vetNombre(x.veterinario_id))}</div></div>
              ${x.es_emergencia ? `<span class="badge b-red">${icon('siren')}Emergencia</span>` : `<span class="badge ${TIPOS[x.tipo].badge}">${TIPOS[x.tipo].label}</span>`}
              <span class="mono" style="font-weight:600">${fmtHora(x.inicio)}</span>
            </div>`).join('')}</div>` : vacio('calendar', 'Nadie en espera', 'Las citas programadas para hoy aparecerán aquí, con las emergencias primero.', `<button class="btn btn-mint" data-accion="cita">${icon('plus')}Agendar cita</button>`)}
        </div>
        <div class="card">
          <div class="card-head"><h2>Últimos avisos</h2><a class="btn btn-ghost btn-sm" href="#/avisos">Ver todos ${icon('chevR')}</a></div>
          ${a.length ? `<div class="list">${a.map((n) => `
            <div class="list-item"><span class="avatar ${n.tipo.startsWith('alerta') ? 'b-red' : 'av-otro'}">${icon(n.tipo === 'alerta_emergencia' ? 'siren' : n.tipo === 'alerta_capacidad' ? 'bed' : 'whatsapp')}</span>
            <div class="grow"><div class="title ellipsis">${esc(etiquetaAviso(n.tipo))}</div><div class="muted ellipsis" style="font-size:13px">${esc(textoAviso(n))}</div></div></div>`).join('')}</div>` : vacio('bell', 'Sin avisos todavía', 'Al agendar citas se programan recordatorios por WhatsApp automáticamente.')}
        </div>
      </section>`;
    completarNombres(view);
  }

  async function pgRecepcion(view, celular) {
    view.innerHTML = `
      <section class="card search-hero">
        <div><h2 style="margin:0;font-family:var(--display);font-size:24px">¿Quién llega a la clínica?</h2><p class="sub">Busca al cliente por su celular. Si no existe, lo registras en un paso.</p></div>
        <form class="row" data-buscar>
          <div class="input-icon grow">${icon('phone')}<input class="input input-xl" data-cel inputmode="numeric" placeholder="Celular del cliente" value="${esc(celular || '')}" autocomplete="off"></div>
          <button class="btn btn-primary btn-lg" type="submit">${icon('search')}Buscar</button>
          <button class="btn btn-ghost btn-lg" type="button" data-nuevo>${icon('plus')}Nuevo cliente</button>
        </form>
        ${mem.clientes.length ? `<div class="chips"><span class="muted" style="font-size:13px;align-self:center">Recientes:</span>${mem.clientes.map((c) => `<a class="chip" href="#/recepcion/${esc(c.celular)}">${esc(c.nombre)} · ${esc(fmtCel(c.celular))}</a>`).join('')}</div>` : ''}
      </section>
      <section data-resultado></section>`;
    $('[data-buscar]', view).addEventListener('submit', (e) => {
      e.preventDefault();
      const cel = soloDigitos($('[data-cel]', view).value);
      if (cel) location.hash = `#/recepcion/${cel}`;
    });
    $('[data-nuevo]', view).addEventListener('click', () => modalNuevoCliente(soloDigitos($('[data-cel]', view).value)));
    const res = $('[data-resultado]', view);
    if (!celular) {
      res.innerHTML = `<div class="card">${vacio('users', 'Busca o registra un cliente', 'Desde el expediente del cliente puedes agregar mascotas, agendar citas, registrar emergencias e internar pacientes.')}</div>`;
      return;
    }
    res.innerHTML = `<div class="card">${cargando('Buscando expediente…')}</div>`;
    let exp;
    try { exp = await api('GET', `/expedientes/${encodeURIComponent(celular)}`); }
    catch (err) {
      if (err.status === 404) {
        res.innerHTML = `<div class="card">${vacio('search', 'No encontramos ese celular', `No hay ningún cliente con el número ${fmtCel(celular)}. ¿Es un cliente nuevo?`, `<button class="btn btn-mint btn-lg" data-registrar>${icon('plus')}Registrar cliente nuevo</button>`)}</div>`;
        $('[data-registrar]', res).addEventListener('click', () => modalNuevoCliente(celular));
      } else res.innerHTML = `<div class="card">${alertaHTML(err)}</div>`;
      return;
    }
    recordarExpediente(exp);
    res.innerHTML = `
      <div class="card stack" style="gap:20px">
        <div class="row between">
          <div class="owner"><span class="avatar av-ink">${esc(iniciales(exp.nombre))}</span><div><h2>${esc(exp.nombre)}</h2><div class="row" style="gap:8px;margin-top:4px"><span class="badge b-gray">${icon('phone')}${esc(fmtCel(exp.celular))}</span><span class="badge b-mint">${exp.mascotas.length} ${exp.mascotas.length === 1 ? 'mascota' : 'mascotas'}</span><span class="badge b-blue">${exp.notas.length} ${exp.notas.length === 1 ? 'nota clínica' : 'notas clínicas'}</span></div></div></div>
          <div class="row">${exp.mascotas.length > 1 ? `<button class="btn btn-ghost" data-fusion>${icon('merge')}Fusionar duplicados</button>` : ''}<button class="btn btn-mint" data-agregar>${icon('plus')}Agregar mascota</button></div>
        </div>
        ${exp.mascotas.length ? `<div class="pets">${exp.mascotas.map((m) => `
          <article class="pet">
            <div class="pet-head"><span class="avatar ${avatarClase(m.especie)}">${esc(iniciales(m.nombre))}</span><div class="grow"><h3>${esc(m.nombre)}</h3><div class="muted" style="font-size:13px">${esc(cap(m.especie))}${m.raza ? ` · ${esc(m.raza)}` : ''}${m.sexo ? ` · ${esc(m.sexo)}` : ''}</div></div></div>
            <div class="chips">${m.fecha_nacimiento ? `<span class="badge b-gray">${esc(edad(m.fecha_nacimiento))}</span>` : ''}${m.peso ? `<span class="badge b-gray">${esc(m.peso)} kg</span>` : ''}${(m.alergias || []).map((al) => `<span class="badge allergy">${icon('alert')}Alergia: ${esc(al)}</span>`).join('')}</div>
            <div class="pet-actions">
              <button class="btn btn-primary btn-sm" data-cita="${esc(m.id)}">${icon('calendar')}Cita</button>
              <button class="btn btn-danger btn-sm" data-emergencia="${esc(m.id)}">${icon('siren')}Emergencia</button>
              <a class="btn btn-ghost btn-sm" href="#/expediente/${esc(m.id)}">${icon('file')}Expediente</a>
              <button class="btn btn-ghost btn-sm" data-internar="${esc(m.id)}">${icon('bed')}Internar</button>
            </div>
          </article>`).join('')}</div>` : vacio('paw', 'Aún no tiene mascotas', 'Agrega la primera mascota para poder agendarle citas.', `<button class="btn btn-mint" data-agregar>${icon('plus')}Agregar mascota</button>`)}
      </div>`;
    $$('[data-agregar]', res).forEach((b) => b.addEventListener('click', () => modalMascota(exp.celular, exp.nombre)));
    const f = $('[data-fusion]', res); if (f) f.addEventListener('click', () => modalFusion(exp));
    res.addEventListener('click', (e) => {
      const b = e.target.closest('[data-cita],[data-emergencia],[data-internar]');
      if (!b) return;
      if (b.dataset.cita) modalNuevaCita({ mascotaId: b.dataset.cita });
      else if (b.dataset.emergencia) modalEmergencia(b.dataset.emergencia);
      else modalInternar(b.dataset.internar);
    });
  }

  const estadoAgenda = { fecha: hoy() };
  async function pgAgenda(view) {
    const fecha = estadoAgenda.fecha;
    let cola = [];
    try { cola = await api('GET', `/citas/cola?fecha=${fecha}`); } catch (err) { mostrarError(err); }
    cola.forEach(recordarCita);
    const enCola = new Set(cola.map((c) => c.id));
    const delDia = Object.values(mem.citas).filter((c) => c.inicio.slice(0, 10) === fecha && !enCola.has(c.id));
    const atencion = delDia.filter((c) => c.estado === 'EN_ATENCION').sort((a, b) => a.inicio.localeCompare(b.inicio));
    const finales = delDia.filter((c) => c.estado === 'COMPLETADA' || c.estado === 'CANCELADA').sort((a, b) => a.inicio.localeCompare(b.inicio));
    const tarjeta = (c) => {
      const t = TIPOS[c.tipo] || TIPOS.consulta;
      const acciones = c.estado === 'PROGRAMADA'
        ? `<button class="btn btn-mint btn-sm" data-t="aprobar" data-id="${esc(c.id)}">${icon('stetho')}Atender</button><button class="btn btn-ghost btn-sm" data-t="cancelar" data-id="${esc(c.id)}">Cancelar</button>`
        : c.estado === 'EN_ATENCION'
          ? `<button class="btn btn-primary btn-sm" data-t="completar" data-id="${esc(c.id)}">${icon('check')}Completar</button><button class="btn btn-ghost btn-sm" data-t="cancelar" data-id="${esc(c.id)}">Cancelar</button>`
          : `<span class="badge ${ESTADOS[c.estado].badge}">${ESTADOS[c.estado].label}</span>`;
      return `<article class="appt ${c.es_emergencia && c.estado === 'PROGRAMADA' ? 'emergency' : ''}">
        <div class="row between"><span class="appt-time">${fmtHora(c.inicio)}<span class="muted" style="font-weight:500;font-size:14px"> – ${fmtHora(c.fin)}</span></span>${c.es_emergencia ? `<span class="badge b-red">${icon('siren')}Emergencia</span>` : `<span class="badge ${t.badge}">${icon(t.icon)}${t.label}</span>`}</div>
        <div class="row" style="flex-wrap:nowrap"><span class="avatar av-otro" data-mascota="${esc(c.mascota_id)}" data-campo="avatar">·</span><div class="grow"><a class="title" style="color:inherit;text-decoration:none" href="#/expediente/${esc(c.mascota_id)}" data-mascota="${esc(c.mascota_id)}">Paciente</a><div class="muted ellipsis" style="font-size:13px" data-mascota="${esc(c.mascota_id)}" data-campo="dueno"></div></div></div>
        <div class="row between" style="font-size:13px"><span class="muted">${icon('stetho')} ${esc(vetNombre(c.veterinario_id))}</span>${c.requiere_reprogramacion ? `<span class="badge b-amber">${icon('alert')}Reprogramar</span>` : ''}</div>
        <div class="appt-actions">${acciones}</div>
      </article>`;
    };
    const columna = (titulo, color, items, vacioTxt) => `<div class="col"><div class="col-head"><h3><span class="dot" style="background:${color}"></span>${titulo}</h3><span class="badge b-gray">${items.length}</span></div>${items.length ? items.map(tarjeta).join('') : `<p class="muted" style="text-align:center;margin:30px 0;font-size:14px">${vacioTxt}</p>`}</div>`;
    view.innerHTML = `
      <section class="card row between">
        <div class="row">
          <button class="icon-btn" data-dia="-1" aria-label="Día anterior">${icon('chevL')}</button>
          <input class="input" type="date" data-fecha value="${fecha}" style="width:auto">
          <button class="icon-btn" data-dia="1" aria-label="Día siguiente">${icon('chevR')}</button>
          <button class="btn btn-ghost btn-sm" data-hoy ${fecha === hoy() ? 'disabled' : ''}>Hoy</button>
          <h2 style="margin:0 0 0 8px;font-family:var(--display);font-size:20px">${cap(fmtFecha(fecha))}</h2>
        </div>
        <div class="row"><button class="btn btn-danger" data-accion="emergencia">${icon('siren')}Emergencia</button><button class="btn btn-mint" data-accion="cita">${icon('plus')}Nueva cita</button></div>
      </section>
      <section class="board">
        ${columna('En espera', 'var(--amber)', cola, 'Sin pacientes en espera')}
        ${columna('En atención', 'var(--mint)', atencion, 'Nadie en consulta ahora')}
        ${columna('Finalizadas', '#9AA5B1', finales, 'Aún no hay citas finalizadas')}
      </section>
      <p class="muted" style="margin:0;font-size:13px">${icon('lock')} Los botones solo ofrecen las transiciones válidas de la State Machine: <b>Atender</b> (PROGRAMADA → EN_ATENCION), <b>Completar</b> (EN_ATENCION → COMPLETADA) y <b>Cancelar</b>.</p>`;
    $('[data-fecha]', view).addEventListener('change', (e) => { estadoAgenda.fecha = e.target.value || hoy(); render(); });
    $$('[data-dia]', view).forEach((b) => b.addEventListener('click', () => { estadoAgenda.fecha = addDays(fecha, Number(b.dataset.dia)); render(); }));
    $('[data-hoy]', view).addEventListener('click', () => { estadoAgenda.fecha = hoy(); render(); });
    $('.board', view).addEventListener('click', (e) => {
      const b = e.target.closest('[data-t]');
      if (!b) return;
      ocupado(b, async () => {
        try {
          const c = await api('POST', `/citas/${b.dataset.id}/transiciones`, { accion: b.dataset.t });
          recordarCita(c);
          const m = await mascotaInfo(c.mascota_id);
          toast('ok', { aprobar: 'En atención', completar: 'Cita completada', cancelar: 'Cita cancelada' }[b.dataset.t], `${m.nombre} · ${fmtHora(c.inicio)}`);
          render();
        } catch (err) { mostrarError(err); }
      });
    });
    completarNombres(view);
  }

  async function pgHospitalizacion(view) {
    const [o, pend] = await Promise.all([api('GET', '/hospitalizacion/ocupacion'), api('GET', '/hospitalizacion/signos-pendientes?horas=4').catch(() => [])]);
    const pendientes = new Map(pend.map((p) => [p.mascota_id, p]));
    const lleno = o.ocupadas >= o.capacidad;
    const color = lleno ? 'var(--red)' : o.ocupadas >= 8 ? 'var(--amber)' : 'var(--mint)';
    view.innerHTML = `
      <section class="card capacity">
        <div class="ring" style="--p:${(o.ocupadas / o.capacidad) * 100};--ring-color:${color}"><div><b>${o.ocupadas}/${o.capacidad}</b><small>ocupadas</small></div></div>
        <div class="stack" style="gap:8px">
          <h2 style="margin:0;font-family:var(--display);font-size:24px">${lleno ? 'Hospitalización llena' : `${o.disponibles} ${o.disponibles === 1 ? 'jaula disponible' : 'jaulas disponibles'}`}</h2>
          <p class="sub">Capacidad máxima de 10 pacientes internados (regla BR-002). Los signos vitales se toman cada 4 a 6 horas.</p>
          <div class="bar ${lleno ? 'full' : o.ocupadas >= 8 ? 'warn' : ''}" style="max-width:520px"><span style="width:${(o.ocupadas / o.capacidad) * 100}%"></span></div>
        </div>
        <div class="stack"><button class="btn btn-mint btn-lg" data-accion="internar">${icon('bed')}Internar paciente</button><button class="btn btn-ghost" data-refrescar>${icon('refresh')}Actualizar</button></div>
      </section>
      ${lleno ? `<div class="full-banner">${icon('ban')}Capacidad máxima alcanzada: no se pueden internar más pacientes hasta dar de alta a uno.</div>` : ''}
      <section class="cages">
        ${o.jaulas.map((j) => {
          if (!j.mascota_id) return `<button type="button" class="cage" data-libre style="cursor:pointer;font:inherit;text-align:left"><span class="num">JAULA ${pad(j.numero)}</span><span class="free">${icon('plus')}Disponible</span></button>`;
          const p = pendientes.get(j.mascota_id);
          return `<article class="cage busy ${p ? 'alert' : ''}">
            <span class="num">JAULA ${pad(j.numero)}</span>
            <div class="row" style="flex-wrap:nowrap;gap:10px"><span class="avatar av-otro" data-mascota="${esc(j.mascota_id)}" data-campo="avatar">·</span><div class="grow" style="min-width:0"><h4 class="ellipsis"><a href="#/expediente/${esc(j.mascota_id)}" style="color:inherit;text-decoration:none" data-mascota="${esc(j.mascota_id)}">Paciente</a></h4><div class="muted ellipsis" style="font-size:12px" data-mascota="${esc(j.mascota_id)}" data-campo="propietario"></div></div></div>
            ${p ? `<span class="badge b-amber">${icon('heart')}Signos vencidos · ${Math.round(p.horas_desde_ultima_toma)} h</span>` : `<span class="badge b-mint">${icon('heart')}Signos al día</span>`}
            <div class="cage-actions"><button class="btn btn-ghost btn-sm" data-signos="${esc(j.mascota_id)}">${icon('thermo')}Signos</button><button class="btn btn-ghost btn-sm" data-alta="${esc(j.mascota_id)}" data-jaula="${j.numero}">${icon('door')}Alta</button></div>
          </article>`;
        }).join('')}
      </section>`;
    $('[data-refrescar]', view).addEventListener('click', () => render());
    $('.cages', view).addEventListener('click', (e) => {
      if (e.target.closest('[data-libre]')) return modalInternar();
      const s = e.target.closest('[data-signos]'); if (s) return modalSignos(s.dataset.signos);
      const a = e.target.closest('[data-alta]'); if (a) return modalAlta(a.dataset.alta, a.dataset.jaula);
    });
    completarNombres(view);
  }

  async function modalSignos(mascotaId) {
    const m = await mascotaInfo(mascotaId);
    const body = abrirModal(`Signos vitales · ${m.nombre}`, `
      <div class="form-grid">
        <div class="field full"><label>Temperatura (°C)</label><div class="input-icon">${icon('thermo')}<input class="input" type="number" step="0.1" data-temp placeholder="38.5"></div></div>
        <div class="field"><label>Frecuencia cardiaca (lpm)</label><div class="input-icon">${icon('heart')}<input class="input" type="number" data-fc placeholder="90"></div><span class="hint">Rango válido: 20 a 300</span></div>
        <div class="field"><label>Frecuencia respiratoria (rpm)</label><input class="input" type="number" data-fr placeholder="24"><span class="hint">Rango válido: 5 a 120</span></div>
      </div>
      <div data-err></div>
      <div class="row end"><button class="btn btn-ghost" data-close>Cancelar</button><button class="btn btn-mint btn-lg" data-ok data-busy="Guardando…">${icon('check')}Registrar toma</button></div>`);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      const err = $('[data-err]', body); err.innerHTML = '';
      try {
        await api('POST', '/hospitalizacion/signos-vitales', { mascota_id: mascotaId, temperatura: $('[data-temp]', body).value, frecuencia_cardiaca: Number($('[data-fc]', body).value), frecuencia_respiratoria: Number($('[data-fr]', body).value) });
        cerrarModal(); toast('ok', 'Signos registrados', `${m.nombre} · próxima toma en 4 a 6 horas`); render();
      } catch (er) { mostrarError(er, err); }
    }));
  }

  async function modalAlta(mascotaId, jaula) {
    const m = await mascotaInfo(mascotaId);
    const body = abrirModal('Dar de alta', `
      <div class="alert-box mint">${icon('door')}<div><h3>¿Dar de alta a ${esc(m.nombre)}?</h3><p>La jaula ${esc(jaula)} quedará disponible para otro paciente.</p></div></div>
      <div data-err></div>
      <div class="row end"><button class="btn btn-ghost" data-close>Cancelar</button><button class="btn btn-primary btn-lg" data-ok data-busy="Procesando…">${icon('check')}Confirmar alta</button></div>`);
    $('[data-ok]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
      try { await api('POST', `/hospitalizacion/altas/${encodeURIComponent(mascotaId)}`); cerrarModal(); toast('ok', `${m.nombre} fue dado de alta`, `Jaula ${jaula} disponible`); render(); }
      catch (er) { mostrarError(er, $('[data-err]', body)); }
    }));
  }

  async function pgExpediente(view, mascotaId) {
    if (!mascotaId) { location.hash = '#/recepcion'; return; }
    const h = await api('GET', `/mascotas/${encodeURIComponent(mascotaId)}/historial`);
    const m = h.mascota;
    mem.mascotas[m.id] = { id: m.id, nombre: m.nombre, especie: m.especie, raza: m.raza, alergias: m.alergias, propietario: h.propietario, celular: h.celular, visto: Date.now() };
    store.set('mascotas', mem.mascotas);
    $('#pageTitle').textContent = `Expediente de ${m.nombre}`;
    const notas = [...h.notas].sort((a, b) => b.creada_en.localeCompare(a.creada_en));
    view.innerHTML = `
      <section class="grid g-side">
        <div class="card">
          <div class="card-head"><div><h2>Historia clínica</h2><p class="sub">${notas.length} ${notas.length === 1 ? 'nota' : 'notas'} · las notas firmadas no se pueden modificar (US-08)</p></div><button class="btn btn-mint" data-nueva>${icon('plus')}Nueva nota</button></div>
          ${notas.length ? `<div class="timeline">${notas.map((n) => `
            <article class="note ${n.estado === 'FIRMADA' ? 'signed' : ''}">
              <div class="row between"><h4>${esc(n.diagnostico)}</h4>${n.estado === 'FIRMADA' ? `<span class="badge b-mint">${icon('lock')}Firmada</span>` : `<span class="badge b-amber">${icon('edit')}Borrador</span>`}</div>
              <div class="muted" style="font-size:13px">${esc(fmtFechaHora(n.creada_en))} · ${esc(vetNombre(n.veterinario_id))}</div>
              ${n.notas ? `<p style="margin:0">${esc(n.notas)}</p>` : ''}
              ${n.receta && n.receta.length ? `<div class="rx"><b style="font-size:13px;color:var(--muted)">RECETA</b>${n.receta.map((r) => `<div class="rx-item">${icon('file')}<div><b>${esc(r.medicamento)}</b> · ${esc(r.dosis)}${r.indicaciones ? `<div class="muted" style="font-size:13px">${esc(r.indicaciones)}</div>` : ''}</div></div>`).join('')}</div>` : ''}
              ${n.estado === 'FIRMADA' ? `<div class="seal">${icon('pen')}<span>Firmada digitalmente por <b>${esc(vetNombre(n.firmada_por))}</b>${n.sello ? ` · sello <span class="mono">${esc(String(n.sello).slice(0, 16))}…</span>` : ''}</span></div>` : ''}
              <div class="row">
                <button class="btn btn-ghost btn-sm" data-editar="${esc(n.id)}">${icon(n.estado === 'FIRMADA' ? 'lock' : 'edit')}Editar</button>
                ${n.estado !== 'FIRMADA' ? `<button class="btn btn-primary btn-sm" data-firmar="${esc(n.id)}" data-busy="Firmando…">${icon('pen')}Firmar</button>` : ''}
              </div>
            </article>`).join('')}</div>` : vacio('file', 'Sin notas clínicas', 'Registra la primera consulta, diagnóstico o receta de este paciente.')}
        </div>
        <aside class="stack" style="gap:20px">
          <div class="card stack" style="gap:16px">
            <div class="owner"><span class="avatar ${avatarClase(m.especie)}">${esc(iniciales(m.nombre))}</span><div><h2>${esc(m.nombre)}</h2><div class="muted">${esc(cap(m.especie))}${m.raza ? ` · ${esc(m.raza)}` : ''}${m.sexo ? ` · ${esc(m.sexo)}` : ''}</div></div></div>
            <div class="grid g-2" style="gap:10px">
              <div class="rx"><span class="muted" style="font-size:12px">EDAD</span><b>${esc(edad(m.fecha_nacimiento) || '—')}</b></div>
              <div class="rx"><span class="muted" style="font-size:12px">PESO</span><b>${m.peso ? `${esc(m.peso)} kg` : '—'}</b></div>
            </div>
            <div class="stack" style="gap:6px"><span class="muted" style="font-size:12px;font-weight:600">ALERGIAS</span><div class="chips">${(m.alergias || []).length ? m.alergias.map((a) => `<span class="badge allergy">${icon('alert')}${esc(a)}</span>`).join('') : '<span class="muted" style="font-size:14px">Sin alergias registradas</span>'}</div></div>
            <a class="list-item" href="#/recepcion/${esc(h.celular)}" style="text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:12px;padding:12px"><span class="avatar av-ink">${esc(iniciales(h.propietario))}</span><div class="grow"><div class="title">${esc(h.propietario)}</div><div class="muted" style="font-size:13px">${esc(fmtCel(h.celular))}</div></div>${icon('chevR')}</a>
          </div>
          <div class="card stack">
            <button class="btn btn-primary" data-cita>${icon('calendar')}Agendar cita</button>
            <button class="btn btn-ghost" data-internar>${icon('bed')}Internar</button>
            <button class="btn btn-danger" data-emergencia>${icon('siren')}Emergencia</button>
          </div>
        </aside>
      </section>`;
    $('[data-nueva]', view).addEventListener('click', () => modalNota(m));
    $('[data-cita]', view).addEventListener('click', () => modalNuevaCita({ mascotaId: m.id }));
    $('[data-internar]', view).addEventListener('click', () => modalInternar(m.id));
    $('[data-emergencia]', view).addEventListener('click', () => modalEmergencia(m.id));
    view.addEventListener('click', (e) => {
      const ed = e.target.closest('[data-editar]');
      if (ed) return modalNota(m, notas.find((n) => n.id === ed.dataset.editar));
      const fi = e.target.closest('[data-firmar]');
      if (fi) {
        if (!exigirVet()) return;
        ocupado(fi, async () => {
          try { await api('POST', `/notas/${fi.dataset.firmar}/firma`, { veterinario_id: mem.vet }); toast('ok', 'Nota firmada', `Firmada por ${vetNombre(mem.vet)}. Desde ahora es inmutable.`); render(); }
          catch (er) { mostrarError(er); }
        });
      }
    });
  }

  function filaReceta(r = {}) {
    return `<div class="rx-row" data-rx><input class="input" data-med placeholder="Medicamento" value="${esc(r.medicamento || '')}"><input class="input" data-dosis placeholder="Dosis" value="${esc(r.dosis || '')}"><input class="input" data-ind placeholder="Indicaciones" value="${esc(r.indicaciones || '')}"><button type="button" class="icon-btn" data-quitar aria-label="Quitar">${icon('trash')}</button></div>`;
  }
  function modalNota(m, nota = null) {
    if (!nota && !exigirVet()) return;
    const editar = Boolean(nota);
    const body = abrirModal(editar ? `Editar nota · ${m.nombre}` : `Nueva nota · ${m.nombre}`, `
      ${editar && nota.estado === 'FIRMADA' ? `<div class="alert-box amber">${icon('lock')}<div><h3>Esta nota ya está firmada</h3><p>Puedes intentar guardar cambios, pero el dominio los rechazará: una nota firmada es inmutable.</p></div></div>` : ''}
      <div class="form-grid">
        <div class="field full"><label>Diagnóstico</label><input class="input" data-diag value="${esc(nota ? nota.diagnostico : '')}" placeholder="Ej. Otitis externa"></div>
        <div class="field full"><label>Notas de la consulta</label><textarea class="input" data-notas placeholder="Hallazgos, tratamiento, observaciones…">${esc(nota ? nota.notas : '')}</textarea></div>
        ${editar ? '' : `<div class="field"><label>Peso actual (kg)</label><input class="input" type="number" step="0.1" min="0" data-peso placeholder="Opcional"></div>
        <div class="field"><label>Veterinario</label><select class="select input" data-vet>${vetOptions()}</select></div>
        <div class="field full"><label>Alergias nuevas</label><input class="input" data-alergias placeholder="Separadas por coma (opcional)"></div>`}
      </div>
      <div class="field"><label>Receta</label><div class="stack" style="gap:8px" data-receta>${(nota && nota.receta.length ? nota.receta : [{}]).map(filaReceta).join('')}</div><button type="button" class="btn btn-ghost btn-sm" style="align-self:flex-start" data-mas>${icon('plus')}Agregar medicamento</button></div>
      <div data-err></div>
      <div class="row end">${editar ? `<button class="btn btn-ghost" data-close>Cancelar</button><button class="btn btn-primary btn-lg" data-guardar data-busy="Guardando…">${icon('check')}Guardar cambios</button>` : `<button class="btn btn-ghost btn-lg" data-borrador data-busy="Guardando…">Guardar borrador</button><button class="btn btn-primary btn-lg" data-firmar data-busy="Firmando…">${icon('pen')}Guardar y firmar</button>`}</div>
    `, { ancho: true });
    const receta = $('[data-receta]', body);
    $('[data-mas]', body).addEventListener('click', () => { receta.insertAdjacentHTML('beforeend', filaReceta()); });
    receta.addEventListener('click', (e) => { const q = e.target.closest('[data-quitar]'); if (q) q.closest('[data-rx]').remove(); });
    const leerReceta = () => $$('[data-rx]', body).map((r) => ({ medicamento: $('[data-med]', r).value.trim(), dosis: $('[data-dosis]', r).value.trim(), indicaciones: $('[data-ind]', r).value.trim() })).filter((r) => r.medicamento);
    const err = $('[data-err]', body);
    if (editar) {
      $('[data-guardar]', body).addEventListener('click', (e) => ocupado(e.currentTarget, async () => {
        err.innerHTML = '';
        try { await api('PUT', `/notas/${nota.id}`, { diagnostico: $('[data-diag]', body).value.trim(), notas: $('[data-notas]', body).value, receta: leerReceta() }); cerrarModal(); toast('ok', 'Nota actualizada'); render(); }
        catch (er) { mostrarError(er, err); }
      }));
      return;
    }
    const guardar = (firmar) => (e) => ocupado(e.currentTarget, async () => {
      err.innerHTML = '';
      const datos = { veterinario_id: $('[data-vet]', body).value, diagnostico: $('[data-diag]', body).value.trim(), notas: $('[data-notas]', body).value, receta: leerReceta(), alergias: $('[data-alergias]', body).value.split(',').map((s) => s.trim()).filter(Boolean), firmar };
      if ($('[data-peso]', body).value) datos.peso = $('[data-peso]', body).value;
      try { await api('POST', `/mascotas/${m.id}/notas`, datos); cerrarModal(); toast('ok', firmar ? 'Nota guardada y firmada' : 'Borrador guardado', firmar ? 'La nota quedó sellada y ya no puede modificarse.' : 'Puedes editarla y firmarla después.'); render(); }
      catch (er) { mostrarError(er, err); }
    });
    $('[data-borrador]', body).addEventListener('click', guardar(false));
    $('[data-firmar]', body).addEventListener('click', guardar(true));
  }

  const estadoReportes = { tab: 'vacunas', desde: addDays(hoy(), -90), hasta: hoy() };
  async function pgReportes(view) {
    const { tab, desde, hasta } = estadoReportes;
    view.innerHTML = `
      <section class="card row between">
        <div class="tabs" role="tablist">${[['vacunas', 'Vacunas atrasadas'], ['productividad', 'Productividad'], ['ocupacion', 'Ocupación']].map(([k, l]) => `<button role="tab" class="${tab === k ? 'on' : ''}" data-tab="${k}">${l}</button>`).join('')}</div>
        ${tab !== 'ocupacion' ? `<form class="row" data-rango><div class="field"><label>Desde</label><input class="input" type="date" data-desde value="${desde}"></div><div class="field"><label>Hasta</label><input class="input" type="date" data-hasta value="${hasta}"></div><button class="btn btn-primary" style="align-self:flex-end" type="submit">${icon('refresh')}Aplicar</button></form>` : ''}
      </section>
      <section class="card" data-rep>${cargando()}</section>`;
    $$('[data-tab]', view).forEach((b) => b.addEventListener('click', () => { estadoReportes.tab = b.dataset.tab; render(); }));
    const f = $('[data-rango]', view);
    if (f) f.addEventListener('submit', (e) => { e.preventDefault(); estadoReportes.desde = $('[data-desde]', view).value; estadoReportes.hasta = $('[data-hasta]', view).value; render(); });
    const rep = $('[data-rep]', view);
    try {
      if (tab === 'vacunas') {
        const filas = await api('GET', `/reportes/vacunas-pendientes?desde=${desde}&hasta=${hasta}`);
        rep.innerHTML = `
          <div class="card-head"><div><h2>Vacunas atrasadas</h2><p class="sub">Citas de vacuna vencidas que no se aplicaron (US-13). Contacta al dueño para reagendar.</p></div>
          <a class="btn btn-mint" href="/reportes/vacunas-pendientes?desde=${desde}&hasta=${hasta}&formato=csv" download>${icon('download')}Descargar CSV</a></div>
          ${filas.length ? `<div class="table-wrap"><table class="t"><thead><tr><th>Mascota</th><th>Dueño</th><th>Celular</th><th>Cita de vacuna</th><th>Estado</th><th>Atraso</th></tr></thead><tbody>${filas.map((r) => `
            <tr><td><div class="row" style="flex-wrap:nowrap;gap:10px"><span class="avatar ${avatarClase(r.especie)}" style="width:32px;height:32px;border-radius:9px;font-size:13px">${esc(iniciales(r.mascota))}</span><a href="#/expediente/${esc(r.mascota_id)}" style="color:inherit;font-weight:600;text-decoration:none">${esc(r.mascota)}</a></div></td>
            <td>${esc(r.propietario)}</td><td class="mono">${esc(fmtCel(r.celular))}</td><td>${esc(fmtFechaHora(r.fecha_cita))}</td>
            <td><span class="badge ${ESTADOS[r.estado] ? ESTADOS[r.estado].badge : 'b-gray'}">${esc(r.estado === 'PROGRAMADA' ? 'No asistió' : cap(r.estado.toLowerCase()))}</span></td>
            <td><span class="badge ${r.dias_atraso > 30 ? 'b-red' : 'b-amber'}">${r.dias_atraso} ${r.dias_atraso === 1 ? 'día' : 'días'}</span></td></tr>`).join('')}</tbody></table></div>` : vacio('checkCircle', 'Ninguna vacuna atrasada', 'En este periodo todas las vacunas agendadas se aplicaron o siguen vigentes.')}`;
      } else if (tab === 'productividad') {
        const filas = await api('GET', `/reportes/productividad?desde=${desde}&hasta=${hasta}`);
        const max = Math.max(1, ...filas.map((r) => r.total));
        rep.innerHTML = `<div class="card-head"><div><h2>Productividad por veterinario</h2><p class="sub">Atenciones completadas en el periodo (US-14).</p></div></div>
          ${filas.length ? `<div class="table-wrap"><table class="t"><thead><tr><th>Veterinario</th><th>Consultas</th><th>Vacunas</th><th>Cirugías</th><th style="width:34%">Total</th></tr></thead><tbody>${filas.map((r) => `
            <tr><td><div class="row" style="flex-wrap:nowrap;gap:10px"><span class="avatar av-ink" style="width:32px;height:32px;border-radius:9px;font-size:13px">${esc(iniciales(r.veterinario))}</span><b>${esc(r.veterinario)}</b></div></td><td>${r.consultas}</td><td>${r.vacunas}</td><td>${r.cirugias}</td>
            <td><div class="hbar"><div class="bar"><span style="width:${(r.total / max) * 100}%"></span></div><b>${r.total}</b></div></td></tr>`).join('')}</tbody></table></div>` : vacio('chart', 'Sin atenciones completadas', 'Las citas que se marquen como completadas en la Agenda aparecerán aquí.')}`;
      } else {
        const o = await api('GET', '/hospitalizacion/ocupacion');
        rep.innerHTML = `<div class="card-head"><div><h2>Ocupación del internado</h2><p class="sub">Estado en tiempo real de las 10 jaulas (US-15).</p></div><a class="btn btn-ghost" href="#/hospitalizacion">Ir a Hospitalización ${icon('chevR')}</a></div>
          <div class="capacity" style="grid-template-columns:auto 1fr"><div class="ring" style="--p:${o.porcentaje};--ring-color:${o.ocupadas >= o.capacidad ? 'var(--red)' : 'var(--mint)'}"><div><b>${Math.round(o.porcentaje)}%</b><small>ocupación</small></div></div>
          <div class="grid g-3"><div class="rx"><span class="muted" style="font-size:12px">OCUPADAS</span><b style="font-size:24px;font-family:var(--display)">${o.ocupadas}</b></div><div class="rx"><span class="muted" style="font-size:12px">DISPONIBLES</span><b style="font-size:24px;font-family:var(--display)">${o.disponibles}</b></div><div class="rx"><span class="muted" style="font-size:12px">CAPACIDAD</span><b style="font-size:24px;font-family:var(--display)">${o.capacidad}</b></div></div></div>`;
      }
      hydrateIcons(rep);
    } catch (err) { rep.innerHTML = alertaHTML(err); }
  }

  const etiquetaAviso = (t) => ({ recordatorio_3_dias: 'Recordatorio de vacuna · 3 días antes', recordatorio_4_horas: 'Recordatorio · 4 horas antes', alerta_emergencia: 'Alerta de emergencia al veterinario', alerta_capacidad: 'Alerta de capacidad a administración' }[t] || cap(String(t).replace(/_/g, ' ')));
  function textoAviso(n) {
    let txt = n.mensaje || '';
    Object.values(mem.mascotas).forEach((m) => { if (txt.includes(m.id)) txt = txt.replace(m.id, m.nombre); });
    return txt;
  }
  async function pgAvisos(view) {
    const avisos = (await api('GET', '/notificaciones')).slice().reverse();
    view.innerHTML = `
      <div class="alert-box mint">${icon('whatsapp')}<div><h3>Mensajes generados automáticamente</h3><p>Cada cita y emergencia dispara un Domain Event que programa el aviso (US-09, US-10). En esta versión los mensajes quedan en una bandeja de salida; en producción se enviarían por WhatsApp Business API.</p></div></div>
      <section class="card">
        <div class="card-head"><h2>Bandeja de salida · ${avisos.length} ${avisos.length === 1 ? 'mensaje' : 'mensajes'}</h2><button class="btn btn-ghost btn-sm" data-refrescar>${icon('refresh')}Actualizar</button></div>
        ${avisos.length ? `<div class="wa">${avisos.map((n) => `
          <div class="bubble ${n.tipo.startsWith('alerta') ? 'alert' : ''}">
            <div class="meta"><b>${esc(etiquetaAviso(n.tipo))}</b></div>
            <div>${esc(textoAviso(n))}</div>
            <div class="meta"><span>Para: ${esc(n.tipo === 'alerta_emergencia' ? vetNombre(n.destino) : /^\d+$/.test(n.destino || '') ? fmtCel(n.destino) : 'Administración')}</span>·<span>${n.enviar_en === 'inmediato' ? 'Inmediato' : `Envío: ${esc(fmtFechaHora(n.enviar_en))}`}</span>·<span class="badge b-mint" style="padding:1px 8px">${esc(cap(String(n.estado || '').toLowerCase()))}</span></div>
          </div>`).join('')}</div>` : vacio('bell', 'Sin mensajes', 'Agenda una cita para ver aquí los recordatorios que se programan solos.')}
      </section>`;
    $('[data-refrescar]', view).addEventListener('click', () => render());
  }

  async function pgEquipo(view) {
    await cargarVets();
    view.innerHTML = `
      <section class="grid g-side">
        <div class="card">
          <div class="card-head"><h2>Veterinarios</h2><span class="badge b-gray">${mem.vets.length}</span></div>
          ${mem.vets.length ? `<div class="list">${mem.vets.map((v) => `
            <div class="list-item"><span class="avatar av-ink">${esc(iniciales(v.nombre))}</span><div class="grow"><div class="title">${esc(v.nombre)}</div><div class="muted mono">${esc(v.cedula)}</div></div>
            ${v.activo ? '<span class="badge b-mint">Activo</span>' : '<span class="badge b-gray">Inactivo</span>'}
            ${v.id === mem.vet ? `<span class="badge b-ink">${icon('stetho')}En turno</span>` : `<button class="btn btn-ghost btn-sm" data-turno="${esc(v.id)}">Poner en turno</button>`}</div>`).join('')}</div>` : vacio('stetho', 'Aún no hay veterinarios', 'Registra al menos uno para poder agendar citas, firmar notas e internar pacientes.')}
        </div>
        <div class="stack" style="gap:20px">
          <form class="card stack" data-form>
            <h3 style="margin:0;font-family:var(--display)">Registrar veterinario</h3>
            <div class="field"><label>Nombre</label><input class="input" data-nombre placeholder="Ej. Dra. Laura López"></div>
            <div class="field"><label>Cédula profesional</label><input class="input" data-cedula placeholder="Ej. CED-123456"></div>
            <div data-err></div>
            <button class="btn btn-primary" type="submit" data-busy="Registrando…">${icon('plus')}Registrar</button>
          </form>
          <div class="card stack" style="background:#F3FBF8;border-color:#BFE9DD">
            <h3 style="margin:0;font-family:var(--display)">Modo demostración</h3>
            <p class="sub">Crea 2 veterinarios, 3 clientes con 13 mascotas y 3 citas para mañana. Se puede ejecutar varias veces sin duplicar datos.</p>
            <button class="btn btn-mint" data-demo data-busy="Cargando datos…">${icon('sparkles')}Cargar datos de demostración</button>
          </div>
        </div>
      </section>`;
    $('[data-form]', view).addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = $('button[type=submit]', e.currentTarget);
      ocupado(btn, async () => {
        try {
          const v = await api('POST', '/veterinarios', { nombre: $('[data-nombre]', view).value.trim(), cedula: $('[data-cedula]', view).value.trim() });
          if (!mem.vet) { mem.vet = v.id; store.set('vet', v.id); }
          toast('ok', 'Veterinario registrado', v.nombre); render();
        } catch (er) { mostrarError(er, $('[data-err]', view)); }
      });
    });
    view.addEventListener('click', (e) => {
      const t = e.target.closest('[data-turno]');
      if (t) { mem.vet = t.dataset.turno; store.set('vet', mem.vet); cargarVets(); render(); }
    });
  }

  // ------------------------------------------------------------------ datos de demostración
  async function cargarDemo(btn) {
    await ocupado(btn, async () => {
      try {
        const vets = await api('GET', '/veterinarios');
        const vet = async (nombre, cedula) => vets.find((v) => v.cedula === cedula) || api('POST', '/veterinarios', { nombre, cedula });
        const v1 = await vet('Dra. Laura López', 'CED-DEMO-01');
        const v2 = await vet('Dr. Mario Garza', 'CED-DEMO-02');
        const refugio = ['Luna', 'Max', 'Toby', 'Nala', 'Coco', 'Simba', 'Kira', 'Bruno', 'Lola', 'Thor'].map((n, i) => ({ nombre: n, especie: i % 3 === 1 ? 'gato' : 'perro', raza: 'Mestizo', sexo: i % 2 ? 'Hembra' : 'Macho', peso: String(4 + i * 1.5) }));
        const clientes = [
          { nombre: 'Ana Martínez', celular: '8112345678', mascotas: [{ nombre: 'Firulais', especie: 'perro', raza: 'Labrador', sexo: 'Macho', peso: '28.5', fecha_nacimiento: '2020-03-14', alergias: ['penicilina'] }, { nombre: 'Michi', especie: 'gato', raza: 'Siamés', sexo: 'Hembra', peso: '4.2', fecha_nacimiento: '2022-07-01' }] },
          { nombre: 'Carlos Ruiz', celular: '8187654321', mascotas: [{ nombre: 'Rocky', especie: 'perro', raza: 'Bulldog francés', sexo: 'Macho', peso: '12', fecha_nacimiento: '2021-01-20' }] },
          { nombre: 'Refugio Patitas', celular: '8100000010', mascotas: refugio },
        ];
        const exps = {};
        for (const c of clientes) {
          let exp;
          try { exp = await api('GET', `/expedientes/${c.celular}`); } catch (e) { exp = await api('POST', '/expedientes', { nombre: c.nombre, celular: c.celular }); }
          for (const m of c.mascotas) {
            if (!exp.mascotas.some((x) => x.nombre === m.nombre)) exp = await api('POST', `/expedientes/${c.celular}/mascotas`, m);
          }
          recordarExpediente(exp);
          exps[c.celular] = exp;
        }
        const id = (cel, nombre) => exps[cel].mascotas.find((m) => m.nombre === nombre).id;
        const manana = addDays(hoy(), 1);
        const citas = [
          { mascota_id: id('8112345678', 'Firulais'), veterinario_id: v1.id, tipo: 'vacuna', inicio: `${manana}T09:00:00` },
          { mascota_id: id('8187654321', 'Rocky'), veterinario_id: v1.id, tipo: 'cirugia', inicio: `${manana}T10:00:00` },
          { mascota_id: id('8112345678', 'Michi'), veterinario_id: v2.id, tipo: 'consulta', inicio: `${manana}T12:30:00` },
        ];
        for (const c of citas) { try { const r = await api('POST', '/citas', c); recordarCita(r.cita); } catch (e) { /* ya existía o el horario está ocupado */ } }
        mem.vet = v1.id; store.set('vet', v1.id);
        await cargarVets();
        toast('ok', 'Datos de demostración listos', '2 veterinarios, 3 clientes, 13 mascotas y citas para mañana.');
        render();
      } catch (err) { mostrarError(err); }
    });
  }

  // ------------------------------------------------------------------ router
  const RUTAS = {
    inicio: { titulo: 'Inicio', eyebrow: 'Resumen del día', pagina: pgInicio },
    recepcion: { titulo: 'Recepción', eyebrow: 'Clientes y mascotas', pagina: pgRecepcion },
    agenda: { titulo: 'Agenda', eyebrow: 'Citas y cola de espera', pagina: pgAgenda },
    hospitalizacion: { titulo: 'Hospitalización', eyebrow: 'Internado · 10 jaulas', pagina: pgHospitalizacion },
    expediente: { titulo: 'Expediente', eyebrow: 'Historia clínica', pagina: pgExpediente, nav: 'recepcion' },
    reportes: { titulo: 'Reportes', eyebrow: 'Administración', pagina: pgReportes },
    avisos: { titulo: 'Avisos WhatsApp', eyebrow: 'Recordatorios y alertas', pagina: pgAvisos },
    equipo: { titulo: 'Veterinarios', eyebrow: 'Equipo médico', pagina: pgEquipo },
  };
  function ruta() {
    const [nombre, arg] = location.hash.replace(/^#\/?/, '').split('/');
    return RUTAS[nombre] ? { nombre, arg: decodeURIComponent(arg || '') } : { nombre: 'inicio', arg: '' };
  }
  let turno = 0;
  async function render() {
    const { nombre, arg } = ruta();
    const r = RUTAS[nombre];
    const mio = ++turno;
    $$('#nav a').forEach((a) => a.classList.toggle('active', a.dataset.route === (r.nav || nombre)));
    $('#pageTitle').textContent = r.titulo;
    $('#pageEyebrow').textContent = r.eyebrow;
    document.title = `${r.titulo} · VetCare 24`;
    const view = $('#view');
    const nueva = view.cloneNode(false); // quita listeners de la página anterior
    view.replaceWith(nueva);
    nueva.innerHTML = cargando();
    $('.app').classList.remove('menu-open');
    try {
      await r.pagina(nueva, arg);
      if (mio !== turno) return;
      hydrateIcons(nueva);
    } catch (err) {
      if (mio !== turno) return;
      nueva.innerHTML = `<div class="card">${alertaHTML(err instanceof ApiError ? err : new ApiError(0, 'No se pudo cargar', 'Ocurrió un error al mostrar esta sección.'))}<div class="row" style="margin-top:12px"><button class="btn btn-primary" data-reintentar>${icon('refresh')}Reintentar</button></div></div>`;
      $('[data-reintentar]', nueva).addEventListener('click', render);
    }
  }

  // ------------------------------------------------------------------ arranque
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-close]') || e.target === $('#modal')) { cerrarModal(); return; }
    const acc = e.target.closest('[data-accion]');
    if (acc) {
      const a = acc.dataset.accion;
      if (a === 'cita') modalNuevaCita({ fecha: ruta().nombre === 'agenda' ? estadoAgenda.fecha : '' });
      else if (a === 'emergencia') modalEmergencia();
      else if (a === 'internar') modalInternar();
    }
    const demo = e.target.closest('[data-demo]');
    if (demo) cargarDemo(demo);
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('#modal').hidden) cerrarModal(); });
  $('#btnEmergenciaGlobal').addEventListener('click', () => modalEmergencia());
  $('#menuToggle').addEventListener('click', () => $('.app').classList.toggle('menu-open'));
  $('#vetActual').addEventListener('change', (e) => { mem.vet = e.target.value; store.set('vet', mem.vet); if (['inicio', 'equipo'].includes(ruta().nombre)) render(); });
  window.addEventListener('hashchange', render);
  const reloj = () => { const d = new Date(); $('#clock').textContent = `${d.toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short' })} · ${fmtHora(isoLocal(d))}`; };
  reloj(); setInterval(reloj, 30000);
  hydrateIcons();
  (async () => {
    const st = $('#apiStatus');
    try { await api('GET', '/health'); st.className = 'status ok'; st.innerHTML = '<i></i>API en línea'; }
    catch (e) { st.className = 'status down'; st.innerHTML = '<i></i>API sin conexión'; }
    await cargarVets();
    render();
  })();
})();
