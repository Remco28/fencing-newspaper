/* Real 3D pencils for the landing desk.
   One transparent WebGL canvas (OGL, ~40 kB gz) sits over the page; its camera is set so the
   desk plane (z = 0) maps 1:1 to CSS pixels, so a pencil "lying on the desk" lines up with the
   2D wood photo. Pencils roll/slide on that plane; past a desk edge they fall (gravity along -z,
   away from the viewer) into the dark backdrop and are gone until reload. */
(function () {
  'use strict';

  var OGL_URL = 'https://cdn.jsdelivr.net/npm/ogl@1.0.11/+esm';

  // Real pencil, millimetres: 190.5 long, 6.5 flat-to-flat hex barrel (~29:1).
  var LEN = 190.5, APO = 3.25, CORNER = APO / Math.cos(Math.PI / 6);
  var SECT = 96;                       // radial segments (16 per hex face)
  var LEN_FRAC = 0.25;                 // pencil length as a fraction of the desk width
  var CAM_H = 1200;                    // camera height above the desk plane, in px
  var TAU = Math.PI * 2;

  function rnd(a, b) { return a + Math.random() * (b - a); }
  function clamp(v, a, b) { return Math.min(Math.max(v, a), b); }
  function smooth(a, b, x) { x = clamp((x - a) / (b - a), 0, 1); return x * x * (3 - 2 * x); }

  /* ---------- geometry: lathe around the X axis, optionally hexagonal ---------- */
  // rings: [x, radius, hex?]. With hex, the section is a hexagon of apothem `radius` further
  // limited by `cut` (a cone), which carves the sharpened scallops into the painted barrel.
  function lathe(rings, opt) {
    opt = opt || {};
    var N = SECT, R = rings.length;
    var pos = new Float32Array(R * (N + 1) * 3), nor = new Float32Array(pos.length);
    var uv = new Float32Array(R * (N + 1) * 2), aux = new Float32Array(R * (N + 1));
    var x0 = opt.uMin || 0, xs = opt.uSpan || LEN;
    for (var i = 0; i < R; i++) {
      var rg = rings[i];
      for (var j = 0; j <= N; j++) {
        var ph = (j % N) / N * TAU, k = i * (N + 1) + j;
        var r = rg[1], a = 0;
        if (rg[2]) {
          var d = ((ph + Math.PI / 6) % (Math.PI / 3)) - Math.PI / 6;
          var rh = APO / Math.cos(d);
          r = Math.min(rh, rg[3]);
          a = smooth(0, 0.14, rh - r);     // 1 where the cone has cut through the paint
        }
        pos[k * 3] = rg[0] - LEN / 2; pos[k * 3 + 1] = r * Math.cos(ph); pos[k * 3 + 2] = r * Math.sin(ph);
        uv[k * 2] = (rg[0] - x0) / xs; uv[k * 2 + 1] = j / N + 1 / 12;
        aux[k] = a;
      }
    }
    var idx = [], acc = new Float32Array(R * N * 3);
    function P(i, j) { var k = i * (N + 1) + (j % N); return [pos[k * 3], pos[k * 3 + 1], pos[k * 3 + 2]]; }
    for (i = 0; i < R - 1; i++) {
      for (j = 0; j < N; j++) {
        var A = i * (N + 1) + j, B = A + 1, C = A + N + 1, D = C + 1;
        idx.push(A, B, C, B, D, C);
        [[[i, j], [i, j + 1], [i + 1, j]], [[i, j + 1], [i + 1, j + 1], [i + 1, j]]].forEach(function (t) {
          var p0 = P(t[0][0], t[0][1]), p1 = P(t[1][0], t[1][1]), p2 = P(t[2][0], t[2][1]);
          var u = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]], v = [p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]];
          var n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
          t.forEach(function (q) { var o = (q[0] * N + (q[1] % N)) * 3; acc[o] += n[0]; acc[o + 1] += n[1]; acc[o + 2] += n[2]; });
        });
      }
    }
    for (i = 0; i < R; i++) for (j = 0; j <= N; j++) {
      var o = (i * N + (j % N)) * 3, nx = acc[o], ny = acc[o + 1], nz = acc[o + 2], l = Math.hypot(nx, ny, nz) || 1, kk = (i * (N + 1) + j) * 3;
      if (l < 1e-9 || !isFinite(l)) { nx = -1; ny = 0; nz = 0; l = 1; }
      nor[kk] = nx / l; nor[kk + 1] = ny / l; nor[kk + 2] = nz / l;
    }
    return { position: { size: 3, data: pos }, normal: { size: 3, data: nor }, uv: { size: 2, data: uv }, aux: { size: 1, data: aux }, index: { data: new Uint16Array(idx) } };
  }

  function eraserRings() {
    var r = [[0, 0]], rr = 3.0, cap = 1.2;
    for (var b = 0; b <= 8; b++) { var t = b / 8 * Math.PI / 2; r.push([cap * (1 - Math.cos(t)), rr - cap + cap * Math.sin(t)]); }
    r.push([9, rr]);
    return r;
  }
  function ferruleRings() {
    var R = 3.8, g = 3.5;
    return [[5.5, 3.0], [5.5, 3.55], [5.8, 3.72], [6.3, R], [6.9, R], [7.1, g], [7.4, g], [7.6, R],
      [8.7, R], [8.9, g], [9.2, g], [9.4, R], [17.4, R], [17.8, 3.72], [18, 3.5], [18, 3.1]];
  }
  function bodyRings() { // hex barrel then the sharpened cone (x in mm along the pencil)
    var r = [[17.5, 0, 1, 99], [60, 0, 1, 99], [120, 0, 1, 99], [165, 0, 1, 99]], n = 30;
    for (var i = 1; i <= n; i++) {
      var t = i / n, x = 165 + 22 * t;
      r.push([x, 0, 1, CORNER + (1.75 - CORNER) * t]);
    }
    return r;
  }
  function graphiteRings() { return [[186.7, 1.78], [188.6, 1.0], [190.2, 0.35], [190.5, 0.2], [190.5, 0]]; }

  /* ---------- barrel paint texture (6 faces stacked along v, length along u) ---------- */
  function barrelTexture() {
    var W = 2048, F = 44, H = F * 6, c = document.createElement('canvas');
    c.width = W; c.height = H;
    var g = c.getContext('2d');
    var grad = g.createLinearGradient(0, 0, 0, F);
    grad.addColorStop(0, '#f6c52a'); grad.addColorStop(.5, '#f2b81a'); grad.addColorStop(1, '#eeb016');
    for (var f = 0; f < 6; f++) { g.fillStyle = grad; g.save(); g.translate(0, f * F); g.fillRect(0, 0, W, F); g.restore(); }
    g.fillStyle = 'rgba(120,70,0,.35)';
    for (f = 0; f < 6; f++) g.fillRect(0, f * F - 1.5, W, 3);          // painted edge between faces
    g.fillStyle = 'rgba(120,70,0,.35)'; g.fillRect(0, H - 1.5, W, 3);
    g.fillStyle = '#1b1713'; g.fillRect(0, 0, W * 0.047, H);              // dark dipped end under the ferrule
    g.fillStyle = '#b01f1f'; g.fillRect(W * 0.047, 0, W * 0.006, H);
    g.fillStyle = 'rgba(52,30,2,.88)'; g.textBaseline = 'middle'; g.font = 'bold 21px Georgia, serif';
    function stamp(face, txt, x) {
      g.save(); g.translate(x, face * F + F / 2 + 1); g.scale(1, 1); g.fillText(txt, 0, 0); g.restore();
    }
    stamp(0, 'ELITE FENCERS CLUB  •  CHATHAM NJ  •  EN GARDE GAZETTE', W * 0.1);
    stamp(3, 'ÉPÉE  •  No. 2  •  HB', W * 0.12);
    return c;
  }

  /* ---------- shaders ---------- */
  var VERT = 'precision highp float;attribute vec3 position;attribute vec3 normal;attribute vec2 uv;attribute float aux;' +
    'uniform mat4 modelViewMatrix;uniform mat4 projectionMatrix;uniform mat3 normalMatrix;' +
    'varying vec3 vN;varying vec3 vP;varying vec2 vUv;varying float vAux;' +
    'void main(){vN=normalMatrix*normal;vUv=uv;vAux=aux;vec4 mv=modelViewMatrix*vec4(position,1.0);vP=mv.xyz;gl_Position=projectionMatrix*mv;}';
  var FRAG = 'precision highp float;uniform sampler2D uMap;uniform vec3 uTint;uniform vec3 uWood;uniform float uSpec;uniform float uShin;' +
    'uniform float uMetal;uniform float uDark;varying vec3 vN;varying vec3 vP;varying vec2 vUv;varying float vAux;' +
    'void main(){' +
    'vec3 N=normalize(vN);vec3 V=normalize(-vP);vec3 L=normalize(vec3(-0.5,0.62,0.78));' +
    'vec3 base=texture2D(uMap,vUv).rgb*uTint;' +
    'float gr=0.5+0.5*sin(vUv.y*95.0+sin(vUv.x*41.0)*1.6);' +
    'base=mix(base,uWood*(0.9+0.14*gr),vAux);' +
    'float nl=dot(N,L);float wrap=clamp((nl+0.4)/1.4,0.0,1.0);' +
    'vec3 col=base*(0.24+0.86*wrap+0.08*N.z);' +
    'vec3 H=normalize(L+V);float sp=pow(max(dot(N,H),0.0),uShin)*uSpec;' +
    'float band=pow(1.0-abs(N.y*0.9+0.1),3.0);' +
    'col=mix(col,base*(0.35+1.15*band)+0.05,uMetal);' +
    'col+=vec3(1.0,0.96,0.85)*sp;' +
    'col*=(1.0-uDark);' +
    'gl_FragColor=vec4(col,1.0);}';
  var SH_VERT = 'precision highp float;attribute vec3 position;attribute vec2 uv;uniform mat4 modelViewMatrix;uniform mat4 projectionMatrix;varying vec2 vUv;' +
    'void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}';
  var SH_FRAG = 'precision highp float;varying vec2 vUv;uniform vec2 uSize;uniform float uHalf;uniform float uRad;uniform float uBlur;uniform float uAlpha;' +
    'void main(){vec2 p=(vUv-0.5)*uSize;float d=length(vec2(max(abs(p.x)-uHalf,0.0),p.y))-uRad;' +
    'float a=(1.0-smoothstep(-uBlur*0.4,uBlur,d))*0.75+(1.0-smoothstep(0.0,uBlur*3.2,d))*0.25;' +
    'gl_FragColor=vec4(0.0,0.0,0.0,a*uAlpha);}';

  /* ---------- controller ---------- */
  EGG.Pencils3D = function (stage, edge) {
    var G = {}, all = [], list = [], spawned = false, ctx = null, canvas = null, raf = 0, lastTs = 0, needRender = false;
    var dragP = null, pending = [], fallers = [];
    var api = {
      lib: 'ogl', ready: false, all: all, list: list, fallen: 0,
      get gl() { return ctx && ctx.gl; },
      scatter: function () { run(scatter); },
      flick: function (i, vx, vy) { var p = list[i]; if (!p || p.fall) return; p.vx = vx; p.vy = vy; kick(); },
      setPose: function (i, x, y, th) { var p = list[i]; if (!p) return; p.x = x; p.y = y; p.th = th; p.vx = p.vy = 0; draw(); },
      /* client-space centre + endpoints, for tests */
      project: function (i) { var p = list[i]; return p ? geom(p) : null; },
      render: function () { draw(); }
    };
    window.__pencils3d = api;
    api.whenReady = new Promise(function (res, rej) { G.resolve = res; G.reject = rej; });
    api.whenReady.catch(function () {});

    function run(fn) { if (ctx) fn(); else pending.push(fn); }

    function stageRect() { return stage.getBoundingClientRect(); }
    function sc() { return stageRect().width / 1300; }
    function lenPx() { return stageRect().width * LEN_FRAC; }
    function pxMM() { return lenPx() / LEN; }
    function apoPx() { return APO * pxMM(); }
    function outside(p) { return p.x <= edge.x0 || p.x >= edge.x1 || p.y <= edge.y0 || p.y >= edge.y1; }

    function geom(p) {
      var r = stageRect(), th = p.th * Math.PI / 180, h = lenPx() / 2;
      var cx = r.left + p.x * r.width, cy = r.top + p.y * r.height;
      return { cx: cx, cy: cy, x0: cx - Math.cos(th) * h, y0: cy - Math.sin(th) * h, x1: cx + Math.cos(th) * h, y1: cy + Math.sin(th) * h, r: apoPx() };
    }

    /* ---------- WebGL setup (lazy: the module is fetched after the desk is already usable) ---------- */
    import(OGL_URL).then(function (ogl) {
      var Renderer = ogl.Renderer, Camera = ogl.Camera, Program = ogl.Program, Mesh = ogl.Mesh, Geometry = ogl.Geometry,
          Transform = ogl.Transform, Texture = ogl.Texture, Plane = ogl.Plane, Quat = ogl.Quat;
      canvas = document.createElement('canvas');
      canvas.className = 'pencil-canvas';
      canvas.setAttribute('aria-hidden', 'true');
      document.body.appendChild(canvas);
      var renderer = new Renderer({ canvas: canvas, alpha: true, premultipliedAlpha: true, antialias: true, dpr: Math.min(window.devicePixelRatio || 1, 2) });
      var gl = renderer.gl;
      if (!gl) throw new Error('no webgl');
      gl.clearColor(0, 0, 0, 0);
      var camera = new Camera(gl, { fov: 30, near: 50, far: CAM_H * 4 });
      camera.position.set(0, 0, CAM_H);
      var scene = new Transform();

      function fit() {
        var w = window.innerWidth, h = window.innerHeight;
        renderer.setSize(w, h);
        camera.perspective({ fov: 2 * Math.atan(h / 2 / CAM_H) * 180 / Math.PI, aspect: w / h });
      }
      fit();

      var white = new Texture(gl, { image: (function () { var c = document.createElement('canvas'); c.width = c.height = 2; var g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, 2, 2); return c; })(), generateMipmaps: false, minFilter: gl.LINEAR });
      var paint = new Texture(gl, { image: barrelTexture(), flipY: false, wrapT: gl.REPEAT, generateMipmaps: true, minFilter: gl.LINEAR_MIPMAP_LINEAR, anisotropy: 8 });
      var WOOD = [0.93, 0.74, 0.46];
      function prog(map, tint, spec, shin, metal) {
        return new Program(gl, { vertex: VERT, fragment: FRAG, cullFace: gl.BACK, uniforms: {
          uMap: { value: map }, uTint: { value: tint }, uWood: { value: WOOD }, uSpec: { value: spec }, uShin: { value: shin }, uMetal: { value: metal }, uDark: { value: 0 } } });
      }
      var mats = {
        body: prog(paint, [1, 1, 1], 0.32, 38, 0),
        eraser: prog(white, [0.92, 0.55, 0.6], 0.08, 10, 0),
        ferrule: prog(white, [0.86, 0.68, 0.33], 0.9, 60, 0.85),
        lead: prog(white, [0.2, 0.2, 0.23], 0.55, 22, 0)
      };
      var geos = {
        body: new Geometry(gl, lathe(bodyRings(), { uMin: 17.5, uSpan: LEN - 17.5 - 3.5 })),
        eraser: new Geometry(gl, lathe(eraserRings())),
        ferrule: new Geometry(gl, lathe(ferruleRings())),
        lead: new Geometry(gl, lathe(graphiteRings()))
      };
      var shadowProg = new Program(gl, { vertex: SH_VERT, fragment: SH_FRAG, transparent: true, depthWrite: false, cullFace: false,
        uniforms: { uSize: { value: [1, 1] }, uHalf: { value: 1 }, uRad: { value: 1 }, uBlur: { value: 1 }, uAlpha: { value: 0.4 } } });
      shadowProg.setBlendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
      var shadowGeo = new Plane(gl);
      var qa = new Quat(), qb = new Quat(), qc = new Quat();

      function build() {
        var grp = new Transform(), p = { grp: grp, parts: [], x: 0.5, y: 0.5, th: 0, roll: rnd(0, TAU), zl: 0, zf: 0, vx: 0, vy: 0, vz: 0, dark: 0, fall: null, drag: null, gone: false };
        Object.keys(geos).forEach(function (k) {
          var m = new Mesh(gl, { geometry: geos[k], program: mats[k], frustumCulled: false });
          m.onBeforeRender(function () { mats[k].uniforms.uDark.value = p.dark; });
          m.setParent(grp); p.parts.push(m);
        });
        var sh = new Mesh(gl, { geometry: shadowGeo, program: shadowProg, frustumCulled: false, renderOrder: 1 });
        sh.onBeforeRender(function () {
          var u = shadowProg.uniforms, s = p.shadow;
          u.uSize.value = s.size; u.uHalf.value = s.half; u.uRad.value = s.rad; u.uBlur.value = s.blur; u.uAlpha.value = s.alpha;
        });
        sh.setParent(scene); p.sh = sh; p.shadow = { size: [1, 1], half: 1, rad: 1, blur: 1, alpha: 0 };
        grp.setParent(scene);
        return p;
      }

      function pose(p) {
        var r = stageRect(), k = pxMM(), vw = window.innerWidth, vh = window.innerHeight, L = lenPx();
        var cx = r.left + p.x * r.width, cy = r.top + p.y * r.height;
        var ap = apoPx(), zc = ap + p.zl + p.zf;
        var th = p.th * Math.PI / 180;
        qa.fromAxisAngle([0, 0, 1], -th);
        qb.fromAxisAngle([1, 0, 0], p.roll);
        qa.multiply(qb);
        if (p.fall) { qc.fromAxisAngle(p.fall.axis, p.fall.a); qc.multiply(qa); p.grp.quaternion.copy(qc); }
        else p.grp.quaternion.copy(qa);
        p.grp.scale.set(k, k, k);
        p.grp.position.set(cx - vw / 2, -(cy - vh / 2), zc);
        // soft contact shadow on the desk plane: offsets and spreads with height, gone once it drops below the desk
        var clear = Math.max(p.zl + Math.max(p.zf, 0), 0), s = p.shadow;
        var fade = p.fall ? Math.max(0, 1 - p.fall.t / 0.12) : 1;
        var pad = 36 * (r.width / 1300);
        s.size = [L + pad * 2, ap * 2 + pad * 2]; s.half = L / 2 - ap * 0.6; s.rad = ap * 0.85;
        s.blur = 2.5 + clear * 0.2 + ap * 0.5; s.alpha = 0.55 / (1 + clear * 0.012) * fade;
        p.sh.visible = s.alpha > 0.01;
        p.sh.scale.set(s.size[0], s.size[1], 1);
        p.sh.rotation.z = -th;
        p.sh.position.set(cx - vw / 2 + (2 + clear * 0.35) * (r.width / 1300) * 1.6, -(cy - vh / 2) - (3.5 + clear * 0.6) * (r.width / 1300) * 1.6, 0.4);
      }

      function draw() {
        needRender = false;
        list.concat(fallers).forEach(pose);
        renderer.render({ scene: scene, camera: camera });
      }
      G.draw = draw;
      api.render = draw;
      function schedule() { if (!needRender) { needRender = true; if (!raf) raf = requestAnimationFrame(frame); } }
      G.schedule = schedule;

      window.addEventListener('resize', function () { fit(); schedule(); });
      window.addEventListener('scroll', schedule, { passive: true });

      G.build = build;
      ctx = { gl: gl, renderer: renderer, scene: scene };
      api.ready = true;
      pending.splice(0).forEach(function (f) { f(); });
      G.resolve(api);
      draw();
    }).catch(function (err) {
      console.warn('3D pencils unavailable', err);
      if (canvas) canvas.remove();
      G.reject(err);
    });

    function draw() { if (G.draw) G.draw(); }

    /* ---------- placement ---------- */
    function place(p, x, y, th) { p.x = x; p.y = y; p.th = th; p.vx = p.vy = 0; p.zl = 0; }
    function scatter() {
      if (!spawned) {
        spawned = true;
        for (var q = 0; q < 2; q++) { var np = G.build(); all.push(np); list.push(np); }
      }
      // survivors only: pencils that already rolled off the desk never come back
      list.forEach(function (p, i) {
        var top = i % 2 === 0, flip = Math.random() < .5 ? 180 : 0;
        place(p, (top ? rnd(22, 45) : rnd(55, 78)) / 100, (top ? rnd(11, 16) : rnd(84, 89)) / 100, rnd(-20, 20) + flip);
        p.roll = rnd(0, TAU);
      });
      draw();
    }

    /* ---------- physics ---------- */
    function startFall(p) {
      var vx = p.vx, vy = p.vy, th = p.th * Math.PI / 180, c = Math.cos(th), s = Math.sin(th);
      // which edge it went over
      var ox = p.x <= edge.x0 ? -1 : p.x >= edge.x1 ? 1 : 0, oy = p.y <= edge.y0 ? -1 : p.y >= edge.y1 ? 1 : 0;
      if (ox && oy) { if (Math.abs(p.x - 0.5) / 0.5 > Math.abs(p.y - 0.5) / 0.5) oy = 0; else ox = 0; }
      var out = Math.max(vx * ox + vy * oy, 0);
      p.fall = { t: 0, a: 0, w: 1.1 + out / (lenPx() * 1.4), axis: [oy, ox, 0], spin: rnd(-70, 70) * Math.PI / 180 * (Math.random() < .5 ? -1 : 1), rv: (-vx * s + vy * c) / apoPx() };
      // axis = edge direction in world space (y up): rotating the outward side toward -z tips it over
      p.vz = 0;
      p.dark = 0;
      var i = list.indexOf(p); if (i >= 0) list.splice(i, 1);
      dragP === p && (dragP = null);
      fallers.push(p);
    }
    function removePencil(p) {
      p.gone = true; p.grp.setParent(null); p.sh.setParent(null);
      var f = fallers.indexOf(p); if (f >= 0) fallers.splice(f, 1);
      api.fallen++;
    }

    function tick(dt, r) {
      var active = false, k = sc(), ap = apoPx();
      list.slice().forEach(function (p) {
        var target = p.drag ? 15 * k : 0;
        if (Math.abs(p.zl - target) > 0.05) { p.zl += (target - p.zl) * Math.min(1, dt * 16); active = true; }
        else p.zl = target;
        if (p.drag) { active = true; return; }
        var sp = Math.hypot(p.vx, p.vy);
        if (sp < 6) { p.vx = p.vy = 0; return; }
        var th = p.th * Math.PI / 180, c = Math.cos(th), sn = Math.sin(th);
        var va = p.vx * c + p.vy * sn, vp = -p.vx * sn + p.vy * c;
        va *= Math.exp(-7 * dt);                 // sliding along its axis: grips fast
        vp *= Math.exp(-1.25 * dt);              // rolling: keeps momentum
        var vpm = Math.max(Math.abs(vp) - 30 * k * dt, 0); vp = vp < 0 ? -vpm : vpm;
        p.vx = va * c - vp * sn; p.vy = va * sn + vp * c;
        p.x += p.vx * dt / r.width; p.y += p.vy * dt / r.height;
        p.roll += vp * dt / ap;
        if (outside(p)) startFall(p); else active = true;
      });
      var g = 2000 * k;
      fallers.slice().forEach(function (p) {
        var f = p.fall; f.t += dt; f.w += 4 * dt; f.a += f.w * dt;
        p.vz -= g * dt; p.zf += p.vz * dt;
        p.x += p.vx * dt / r.width; p.y += p.vy * dt / r.height;
        p.vx *= Math.exp(-0.6 * dt); p.vy *= Math.exp(-0.6 * dt);
        p.th += f.spin * 180 / Math.PI * dt; p.roll += f.rv * dt * 0.5;
        p.dark = clamp(-p.zf / (330 * k), 0, 1);
        p.dark = Math.pow(p.dark, 0.8);
        if (p.zf < -520 * k || f.t > 2) removePencil(p); else active = true;
      });
      return active;
    }

    function frame(ts) {
      raf = 0;
      var dt = Math.min((ts - lastTs) / 1000 || 0.016, 0.034);
      lastTs = ts;
      var active = tick(dt, stageRect());
      draw();
      if (active) raf = requestAnimationFrame(frame);
    }
    function kick() { if (!raf && ctx) { lastTs = performance.now(); raf = requestAnimationFrame(frame); } }

    /* ---------- pointer interaction (hit-tested against the pencil axis; claims the event before papers) ---------- */
    function hit(e) {
      var best = null, bd = 1e9, ap = apoPx(), slop = Math.max(ap + 9, 13);
      list.forEach(function (p) {
        if (p.fall) return;
        var g = geom(p), ax = g.x1 - g.x0, ay = g.y1 - g.y0, l2 = ax * ax + ay * ay || 1;
        var t = clamp(((e.clientX - g.x0) * ax + (e.clientY - g.y0) * ay) / l2, 0, 1);
        var d = Math.hypot(e.clientX - (g.x0 + ax * t), e.clientY - (g.y0 + ay * t));
        if (d < slop && d < bd) { bd = d; best = p; }
      });
      return best;
    }

    stage.addEventListener('pointerdown', function (e) {
      if (e.button !== 0 || !ctx) return;
      var p = hit(e);
      if (!p) return;
      e.stopPropagation(); e.preventDefault();
      p.vx = p.vy = 0;
      p.drag = { id: e.pointerId, px: e.clientX, py: e.clientY, moved: false, trail: [{ t: e.timeStamp, x: e.clientX, y: e.clientY }] };
      dragP = p;
      try { stage.setPointerCapture(e.pointerId); } catch (_) {}
      document.body.classList.add('pencil-drag');
      kick();
    }, true);

    stage.addEventListener('pointermove', function (e) {
      var p = dragP;
      if (!p || !p.drag || e.pointerId !== p.drag.id) {
        if (!dragP && ctx && e.pointerType === 'mouse') document.body.classList.toggle('pencil-hover', !!hit(e));
        return;
      }
      var d = p.drag, r = stageRect();
      var dx = e.clientX - d.px, dy = e.clientY - d.py;
      if (!d.moved) { if (Math.hypot(dx, dy) < 3) return; d.moved = true; }
      d.px = e.clientX; d.py = e.clientY;
      var th = p.th * Math.PI / 180;
      p.roll += (-dx * Math.sin(th) + dy * Math.cos(th)) / apoPx();   // dragging sideways rolls it
      p.x = clamp(p.x + dx / r.width, edge.x0, edge.x1);
      p.y = clamp(p.y + dy / r.height, edge.y0, edge.y1);
      d.trail.push({ t: e.timeStamp, x: e.clientX, y: e.clientY });
      while (d.trail.length > 2 && e.timeStamp - d.trail[0].t > 90) d.trail.shift();
      kick();
    });

    function end(e, cancelled) {
      var p = dragP;
      if (!p || !p.drag || e.pointerId !== p.drag.id) return;
      var d = p.drag, tr = d.trail;
      p.drag = null; dragP = null;
      document.body.classList.remove('pencil-drag');
      if (!d.moved || cancelled) { kick(); return; }
      var a = tr[0], b = tr[tr.length - 1], span = (b.t - a.t) / 1000;
      if (span > 0.012 && e.timeStamp - b.t < 80) { p.vx = (b.x - a.x) / span; p.vy = (b.y - a.y) / span; }
      var sp = Math.hypot(p.vx, p.vy);
      if (sp > 2400) { p.vx *= 2400 / sp; p.vy *= 2400 / sp; }
      // a small nudge near the rim is enough to tip it over
      var tip = 0.03, nx = 0, ny = 0;
      if (p.x - edge.x0 < tip) nx = -1; else if (edge.x1 - p.x < tip) nx = 1;
      if (p.y - edge.y0 < tip * 1.5) ny = -1; else if (edge.y1 - p.y < tip * 1.5) ny = 1;
      if (nx || ny) {
        var n = Math.hypot(nx, ny); nx /= n; ny /= n;
        var out = p.vx * nx + p.vy * ny;
        if (out < 160) { p.vx += nx * (160 - out); p.vy += ny * (160 - out); }
      }
      if (outside(p)) startFall(p);
      kick();
    }
    stage.addEventListener('pointerup', function (e) { end(e, false); });
    stage.addEventListener('pointercancel', function (e) { end(e, true); });

    return api;
  };
})();
