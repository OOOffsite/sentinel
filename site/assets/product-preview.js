(() => {
  'use strict';
  const root = document.getElementById('product-preview');
  if (!root) return;
  const data = window.SentinelProductPreviewData;
  const factories = window.SentinelProductPreviewRenderers;
  const $ = id => document.getElementById(`product-${id}`);
  if (!data || !factories) {
    $('description').textContent = 'The bundled product preview could not load. The guides and reference remain available.';
    return;
  }
  const ids = data.roster.map(r => `${r.team}.${r.seat}`);
  const roster = new Map(data.roster.map((r, i) => [ids[i], r]));
  const tone = {idle:.28,planning:.65,coding:1,review:.85,testing:.9,syncing:.95,blocked:.65,offline:.15,unknown:.35};
  const format = time => `${String(Math.floor(time / 60000)).padStart(2, '0')}:${String(Math.floor(time / 1000) % 60).padStart(2, '0')}`;
  const text = (id, value) => { $(id).textContent = value; };
  const make = (tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  };
  let mode = 'simulation', moment = 0, team = 'all', selected = 'foundation.lead';
  const simulation = factories.simulation($('canvas'), value => text('links', value));
  const observation = factories.observed($('observed-svg'), node => {
    selected = node;
    render();
  });

  function selectionOptions() {
    $('agent').replaceChildren();
    if (mode === 'simulation') {
      for (const t of data.teams.filter(t => team === 'all' || t.id === team)) {
        const group = document.createElement('optgroup');
        group.label = t.name;
        for (const id of ids.filter(id => id.startsWith(`${t.id}.`))) group.append(new Option(id, id));
        $('agent').append(group);
      }
      if (team !== 'all' && !selected.startsWith(`${team}.`)) selected = `${team}.lead`;
      if (!roster.has(selected)) selected = team === 'all' ? 'foundation.lead' : `${team}.lead`;
    } else {
      const seats = data.observed[moment].seats;
      for (const seat of seats) $('agent').append(new Option(seat.seat, seat.node_id));
      if (!seats.some(seat => seat.node_id === selected)) selected = seats[0].node_id;
    }
    $('agent').value = selected;
  }

  function fields(entries) {
    const list = $('agent-fields');
    list.replaceChildren();
    for (const [key, value] of entries) list.append(make('dt', '', key), make('dd', '', String(value)));
  }

  function renderTeams() {
    const host = $('teams');
    host.replaceChildren();
    const agents = mode === 'simulation' ? new Map(data.snapshots[moment].agents) : null;
    for (const t of data.teams) {
      const members = ids.filter(id => id.startsWith(`${t.id}.`));
      const button = make('button', 'product-team');
      button.type = 'button';
      button.style.setProperty('--team-color', t.color);
      button.setAttribute('aria-pressed', String(team === t.id));
      button.setAttribute('aria-label', `${t.name}, ${members.length} declared seats${mode === 'simulation' ? '; filter this team' : '; synthetic observation fixture'}`);
      if (mode === 'observed') button.disabled = true;
      const top = make('span', 'product-team-top');
      const name = make('span', 'product-team-name');
      name.append(make('i', ''), document.createTextNode(t.name));
      top.append(name, make('span', 'product-team-count', `${team === 'all' || team === t.id ? members.length : 0}/32`));
      const strip = make('span', 'product-strip');
      strip.setAttribute('aria-hidden', 'true');
      for (const id of members) {
        const item = agents?.get(id);
        const fixture = mode === 'observed' ? data.observed[moment].seats.find(s => s.seat === id) : null;
        const state = item?.state || fixture?.activity || 'unknown';
        const seat = make('i', 'product-seat');
        seat.title = `${id} · ${state}`;
        seat.style.setProperty('--seat-color', state === 'blocked' ? '#ff637e' : t.color);
        seat.style.setProperty('--seat-opacity', team !== 'all' && team !== t.id ? '.08' : String(tone[state] ?? (state === 'working' ? 1 : .35)));
        strip.append(seat);
      }
      const meta = mode === 'simulation' ? `${t.lead} supervisor · ${members.filter(id => agents.get(id).state === 'blocked').length} blocked` : '4 fixture nodes · 32 planned seats';
      button.append(top, strip, make('span', 'product-team-meta', meta));
      button.addEventListener('click', () => {
        team = team === t.id ? 'all' : t.id;
        $('team').value = team;
        selectionOptions();
        render();
      });
      host.append(button);
    }
  }

  function renderEvents(events) {
    $('events').replaceChildren();
    for (const event of events) {
      const row = make('li', '');
      const detail = make('span', '');
      detail.append(make('b', '', event.type.slice(6, -3).toUpperCase()), make('span', '', simulation.describe(event)));
      row.append(make('span', 'product-event-time', format(event.atlasoffset)), detail);
      $('events').append(row);
    }
  }

  function renderMesh() {
    if (mode === 'simulation') simulation.render(data.snapshots[moment], selected, team);
    else observation.render(data.observed[moment], selected);
  }

  function render() {
    $('agent').value = selected;
    renderTeams();
    if (mode === 'simulation') {
      const snapshot = data.snapshots[moment], agents = new Map(snapshot.agents);
      const visible = ids.filter(id => team === 'all' || id.startsWith(`${team}.`));
      const agent = agents.get(selected), r = roster.get(selected);
      text('kpi-seats', visible.length);
      text('kpi-active', visible.filter(id => !['idle', 'offline', 'unknown', 'blocked'].includes(agents.get(id).state)).length);
      text('kpi-third', `${snapshot.summary.accepted} / ${data.missions.length}`);
      text('kpi-fourth', snapshot.cursor.toLocaleString());
      text('position', format(snapshot.at));
      text('graph-status', `${visible.length} visible / 128 logical seats`);
      text('state-tag', agent.state.toUpperCase());
      text('agent-name', r.seat);
      text('agent-meta', `${r.team} / ${r.cell} · ${r.runtime}`);
      fields([['Activity', agent.state], ['Mission', agent.mission || '—'], ['Ownership', r.scope],
        ['Heartbeat', agent.heartbeat === null ? 'Unknown' : format(agent.heartbeat)], ['Tx / Rx', `${agent.tx} / ${agent.rx}`]]);
      renderEvents(snapshot.events);
      $('moment').setAttribute('aria-valuetext', `${snapshot.at / 1000} seconds into included simulation`);
    } else {
      const snapshot = data.observed[moment], agent = snapshot.seats.find(s => s.node_id === selected);
      text('kpi-seats', `${snapshot.seats.length} / 128`);
      text('kpi-active', snapshot.seats.filter(s => s.presence === 'running').length);
      text('kpi-third', `${snapshot.ttl_seconds}s`);
      text('kpi-fourth', 'Unknown');
      text('position', snapshot.label.toUpperCase());
      text('graph-status', '128 planned seats · 16 synthetic fixture nodes');
      text('links', 'NO MESSAGE LINKS');
      text('state-tag', agent.activity.toUpperCase());
      text('agent-name', agent.seat.split('.').slice(1).join('.'));
      text('agent-meta', `${agent.seat.split('.')[0]} · ${agent.runtime}`);
      fields([['Activity', agent.activity], ['Presence', agent.presence], ['Sample age', `${agent.sample_age_seconds}s`],
        ['Needs input', agent.needs_input], ['Messages', 'Unavailable']]);
      $('events').replaceChildren();
      const row = make('li', '');
      row.append(make('span', 'product-event-time', '—'), make('span', '', 'Synthetic fixture only. No retained source logs, directed messages, or real seat identity are asserted.'));
      $('events').append(row);
      $('moment').setAttribute('aria-valuetext', snapshot.label);
    }
    renderMesh();
  }

  function changeMode(next) {
    mode = next;
    moment = 0;
    team = 'all';
    $('team').value = 'all';
    $('team').disabled = mode === 'observed';
    $('all-teams').disabled = mode === 'observed';
    $('mode-simulation').setAttribute('aria-pressed', String(mode === 'simulation'));
    $('mode-observed').setAttribute('aria-pressed', String(mode === 'observed'));
    $('canvas').toggleAttribute('hidden', mode !== 'simulation');
    $('observed-svg').toggleAttribute('hidden', mode !== 'observed');
    $('legend').hidden = mode !== 'simulation';
    text('origin', mode === 'simulation' ? 'Included simulation · recorded sample data' : 'Observed UI · synthetic fixtures, not live data');
    text('mode-note', mode === 'simulation' ? 'Original Atlas renderer · frozen moments' : 'Original observed renderer · example freshness states');
    text('mesh-title', mode === 'simulation' ? '128-seat constellation' : 'Observed mesh');
    text('kpi-label-seats', mode === 'simulation' ? 'Visible seats' : 'Fixture / planned seats');
    text('kpi-label-active', mode === 'simulation' ? 'Busy in sample' : 'Running in fixture');
    text('kpi-label-third', mode === 'simulation' ? 'Accepted missions' : 'Freshness TTL');
    text('kpi-label-fourth', mode === 'simulation' ? 'Journal cursor' : 'Historical completeness');
    text('events-title', mode === 'simulation' ? 'Recorded events' : 'Observation boundary');
    text('moment-label', mode === 'simulation' ? 'Recorded moment' : 'Fixture freshness');
    text('description', mode === 'simulation' ? 'Explore three frozen moments from the included Atlas simulation. All activity and message evidence shown here is fictional.' : 'Two synthetic examples rendered by the actual observed mesh: fresh supported samples, then samples older than the 90-second TTL. No directed message evidence is available.');
    $('moment').value = '0';
    $('moment').max = mode === 'simulation' ? '2' : '1';
    $('ticks').replaceChildren(...(mode === 'simulation' ? ['00:45', '01:30', '02:30'] : ['Fresh sample · 5s age', 'Stale sample · 120s age']).map(label => make('span', '', label)));
    selectionOptions();
    render();
  }

  $('mode-simulation').addEventListener('click', () => changeMode('simulation'));
  $('mode-observed').addEventListener('click', () => changeMode('observed'));
  $('team').addEventListener('change', event => {
    team = event.target.value;
    selectionOptions();
    render();
  });
  $('all-teams').addEventListener('click', () => {
    team = 'all';
    $('team').value = team;
    selectionOptions();
    render();
  });
  $('agent').addEventListener('change', event => {
    selected = event.target.value;
    render();
  });
  $('moment').addEventListener('input', event => {
    moment = Number(event.target.value);
    render();
  });
  $('canvas').addEventListener('click', event => {
    const id = simulation.hit(event);
    if (id) { selected = id; render(); }
  });
  if ('ResizeObserver' in window) new ResizeObserver(renderMesh).observe($('canvas').parentElement);
  else window.addEventListener('resize', renderMesh);
  changeMode('simulation');
})();
