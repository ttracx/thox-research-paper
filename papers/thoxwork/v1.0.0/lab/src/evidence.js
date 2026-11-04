/*
 * THOX ThoxWork Evidence Lab: evidence core.
 *
 * Pure JavaScript SHA-256 (FIPS 180-4), HMAC-SHA-256 (RFC 2104), canonical JSON,
 * and a hash-chained, optionally keyed evidence log. Runs unchanged in the
 * browser (file:// or hosted) and in Node, so the lab page and the timed
 * experiments execute the same code.
 *
 * Copyright 2026 THOX.ai LLC. Licensed under the Apache License, Version 2.0.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.ThoxEvidence = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ]);

  /** Encode a JavaScript string as UTF-8 bytes. */
  function utf8(str) {
    if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(str);
    const out = [];
    for (let i = 0; i < str.length; i++) {
      let c = str.charCodeAt(i);
      if (c >= 0xd800 && c <= 0xdbff && i + 1 < str.length) {
        const d = str.charCodeAt(i + 1);
        if (d >= 0xdc00 && d <= 0xdfff) { c = 0x10000 + ((c - 0xd800) << 10) + (d - 0xdc00); i++; }
      }
      if (c < 0x80) out.push(c);
      else if (c < 0x800) out.push(0xc0 | (c >> 6), 0x80 | (c & 63));
      else if (c < 0x10000) out.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
      else out.push(0xf0 | (c >> 18), 0x80 | ((c >> 12) & 63), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
    }
    return Uint8Array.from(out);
  }

  function toBytes(input) {
    if (input instanceof Uint8Array) return input;
    if (typeof input === "string") return utf8(input);
    if (input && input.buffer instanceof ArrayBuffer) return new Uint8Array(input.buffer, input.byteOffset, input.byteLength);
    if (input instanceof ArrayBuffer) return new Uint8Array(input);
    throw new TypeError("sha256 input must be a string, Uint8Array or ArrayBuffer");
  }

  function hex(bytes) {
    let s = "";
    for (let i = 0; i < bytes.length; i++) s += (bytes[i] < 16 ? "0" : "") + bytes[i].toString(16);
    return s;
  }

  /** SHA-256 digest of a string or byte array; returns 32 bytes. */
  function sha256Bytes(input) {
    const msg = toBytes(input);
    const bitLen = msg.length * 8;
    const padLen = ((msg.length + 9 + 63) >> 6) << 6;
    const buf = new Uint8Array(padLen);
    buf.set(msg);
    buf[msg.length] = 0x80;
    // Length in bits as a 64-bit big-endian integer. High word covers inputs over 512 MiB.
    const hi = Math.floor(bitLen / 0x100000000);
    const lo = bitLen >>> 0;
    buf[padLen - 8] = hi >>> 24; buf[padLen - 7] = (hi >>> 16) & 255; buf[padLen - 6] = (hi >>> 8) & 255; buf[padLen - 5] = hi & 255;
    buf[padLen - 4] = lo >>> 24; buf[padLen - 3] = (lo >>> 16) & 255; buf[padLen - 2] = (lo >>> 8) & 255; buf[padLen - 1] = lo & 255;

    const H = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
    const W = new Uint32Array(64);
    for (let off = 0; off < padLen; off += 64) {
      for (let t = 0; t < 16; t++) {
        const j = off + t * 4;
        W[t] = (buf[j] << 24) | (buf[j + 1] << 16) | (buf[j + 2] << 8) | buf[j + 3];
      }
      for (let t = 16; t < 64; t++) {
        const w15 = W[t - 15], w2 = W[t - 2];
        const s0 = ((w15 >>> 7) | (w15 << 25)) ^ ((w15 >>> 18) | (w15 << 14)) ^ (w15 >>> 3);
        const s1 = ((w2 >>> 17) | (w2 << 15)) ^ ((w2 >>> 19) | (w2 << 13)) ^ (w2 >>> 10);
        W[t] = (W[t - 16] + s0 + W[t - 7] + s1) >>> 0;
      }
      let a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (let t = 0; t < 64; t++) {
        const S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
        const ch = (e & f) ^ (~e & g);
        const t1 = (h + S1 + ch + K[t] + W[t]) >>> 0;
        const S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
        const maj = (a & b) ^ (a & c) ^ (b & c);
        const t2 = (S0 + maj) >>> 0;
        h = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      H[0] = (H[0] + a) >>> 0; H[1] = (H[1] + b) >>> 0; H[2] = (H[2] + c) >>> 0; H[3] = (H[3] + d) >>> 0;
      H[4] = (H[4] + e) >>> 0; H[5] = (H[5] + f) >>> 0; H[6] = (H[6] + g) >>> 0; H[7] = (H[7] + h) >>> 0;
    }
    const out = new Uint8Array(32);
    for (let i = 0; i < 8; i++) {
      out[i * 4] = H[i] >>> 24; out[i * 4 + 1] = (H[i] >>> 16) & 255; out[i * 4 + 2] = (H[i] >>> 8) & 255; out[i * 4 + 3] = H[i] & 255;
    }
    return out;
  }

  /** SHA-256 as lowercase hex. */
  function sha256(input) { return hex(sha256Bytes(input)); }

  /** HMAC-SHA-256 (RFC 2104) as lowercase hex. */
  function hmacSha256(key, message) {
    let k = toBytes(key);
    if (k.length > 64) k = sha256Bytes(k);
    const ipad = new Uint8Array(64), opad = new Uint8Array(64);
    for (let i = 0; i < 64; i++) { const b = i < k.length ? k[i] : 0; ipad[i] = b ^ 0x36; opad[i] = b ^ 0x5c; }
    const m = toBytes(message);
    const inner = new Uint8Array(64 + m.length); inner.set(ipad); inner.set(m, 64);
    const ih = sha256Bytes(inner);
    const outer = new Uint8Array(96); outer.set(opad); outer.set(ih, 64);
    return hex(sha256Bytes(outer));
  }

  function hexToBytes(h) {
    if (typeof h !== "string" || h.length % 2 !== 0 || /[^0-9a-f]/i.test(h)) throw new TypeError("invalid hex string");
    const out = new Uint8Array(h.length / 2);
    for (let i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
    return out;
  }

  /** Constant-time comparison of two equal-length hex strings. */
  function safeEqual(a, b) {
    if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
    let diff = 0;
    for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
    return diff === 0;
  }

  /**
   * Canonical JSON: object keys sorted, no whitespace, finite numbers only.
   * Two parties that hold the same record produce the same bytes and the same hash.
   */
  function canonical(value) {
    if (value === null) return "null";
    const t = typeof value;
    if (t === "number") {
      if (!Number.isFinite(value)) throw new TypeError("canonical JSON rejects non-finite numbers");
      return JSON.stringify(value);
    }
    if (t === "boolean" || t === "string") return JSON.stringify(value);
    if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
    if (t === "object") {
      const keys = Object.keys(value).filter((k) => value[k] !== undefined).sort();
      return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonical(value[k])).join(",") + "}";
    }
    throw new TypeError("canonical JSON rejects " + t);
  }

  const GENESIS = "0".repeat(64);
  const KINDS = new Set([
    "session.open", "policy.decision", "lifecycle.transition", "approval.request", "approval.decision",
    "action.execute", "action.blocked", "handoff", "memory.contradiction", "capture.screenshot",
    "capture.recording", "note", "session.close",
  ]);

  /**
   * Hash-chained evidence log. Each record commits to the previous record's hash,
   * so editing, reordering, inserting or deleting any record breaks verification
   * at the first affected position. With a session key, each record also carries
   * an HMAC tag so a party without the key cannot rebuild a consistent chain.
   */
  class EvidenceChain {
    constructor(opts) {
      const o = opts || {};
      if (o.key !== undefined && typeof o.key !== "string") throw new TypeError("key must be a string");
      this.key = o.key || null;
      this.clock = typeof o.clock === "function" ? o.clock : () => new Date().toISOString();
      this.records = [];
    }

    head() { return this.records.length ? this.records[this.records.length - 1].hash : GENESIS; }

    /** Append a record and return it. kind must be a known evidence kind. */
    append(kind, actor, payload) {
      if (!KINDS.has(kind)) throw new RangeError("unknown evidence kind: " + kind);
      if (typeof actor !== "string" || !actor) throw new TypeError("actor must be a non-empty string");
      const body = { seq: this.records.length, ts: this.clock(), kind, actor, payload: payload === undefined ? null : payload, prev: this.head() };
      const bytes = canonical(body);
      const rec = Object.assign({}, body, { hash: sha256(bytes) });
      if (this.key) rec.tag = hmacSha256(this.key, rec.hash);
      this.records.push(rec);
      return rec;
    }

    /**
     * Verify the whole chain. Returns { ok, length, firstBad, reason }.
     * firstBad is the index of the first record that fails, or -1.
     */
    static verify(records, key) {
      let prev = GENESIS;
      for (let i = 0; i < records.length; i++) {
        const r = records[i];
        if (!r || typeof r !== "object") return { ok: false, length: records.length, firstBad: i, reason: "record is not an object" };
        if (r.seq !== i) return { ok: false, length: records.length, firstBad: i, reason: "sequence gap or reorder" };
        if (r.prev !== prev) return { ok: false, length: records.length, firstBad: i, reason: "previous-hash mismatch" };
        const body = { seq: r.seq, ts: r.ts, kind: r.kind, actor: r.actor, payload: r.payload, prev: r.prev };
        let h;
        try { h = sha256(canonical(body)); } catch (e) { return { ok: false, length: records.length, firstBad: i, reason: "record not canonicalizable" }; }
        if (!safeEqual(h, r.hash)) return { ok: false, length: records.length, firstBad: i, reason: "record hash mismatch" };
        if (key) {
          if (typeof r.tag !== "string" || !safeEqual(hmacSha256(key, r.hash), r.tag)) return { ok: false, length: records.length, firstBad: i, reason: "HMAC tag mismatch" };
        }
        prev = r.hash;
      }
      return { ok: true, length: records.length, firstBad: -1, reason: "" };
    }

    verify() { return EvidenceChain.verify(this.records, this.key); }

    /** Export a self-describing bundle. The key is never exported. */
    exportBundle(meta) {
      return {
        format: "thox.evidence.bundle", version: 1,
        meta: meta || {}, keyed: !!this.key, head: this.head(), count: this.records.length,
        records: this.records.map((r) => Object.assign({}, r)),
      };
    }

    static fromBundle(bundle, key) {
      if (!bundle || bundle.format !== "thox.evidence.bundle" || bundle.version !== 1 || !Array.isArray(bundle.records)) {
        throw new TypeError("not a thox.evidence.bundle v1");
      }
      const c = new EvidenceChain({ key });
      c.records = bundle.records.map((r) => Object.assign({}, r));
      return c;
    }
  }

  /** Known-answer tests: FIPS 180-4 examples and RFC 4231 HMAC cases 1, 2 and 6. */
  function selfTest() {
    const cases = [
      [sha256(""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
      [sha256("abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"],
      [sha256("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"), "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"],
      [sha256("a".repeat(1000)), "41edece42d63e8d9bf515a9ba6932e1c20cbc9f5a5d134645adb5db1b9737ea3"],
      [hmacSha256(hexToBytes("0b".repeat(20)), "Hi There"), "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"],
      [hmacSha256("Jefe", "what do ya want for nothing?"), "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"],
      [hmacSha256(hexToBytes("aa".repeat(131)), "Test Using Larger Than Block-Size Key - Hash Key First"), "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"],
    ];
    const results = cases.map(([got, want]) => got === want);
    return { ok: results.every(Boolean), passed: results.filter(Boolean).length, total: results.length };
  }

  return { sha256, sha256Bytes, hmacSha256, hexToBytes, canonical, safeEqual, EvidenceChain, GENESIS, KINDS: Array.from(KINDS), selfTest };
});
